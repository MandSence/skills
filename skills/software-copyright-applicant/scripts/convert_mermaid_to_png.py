# -*- coding: utf-8 -*-
"""
Mermaid图表转PNG脚本

本模块用于将Markdown文档中的Mermaid代码块转换为PNG图片，
并将图片保存到指定的assets目录。

优化内容：
- 返回详细的转换状态（成功/失败）
- 转换失败时生成占位图片
- 支持索引位置正确匹配，避免图片插入错位
"""

import re
import os
import sys
import requests
from typing import List, Tuple, Dict, Any


class ProgressTracker:
    """简单的进度跟踪器"""

    def __init__(self, total: int, description: str = "处理中"):
        self.total = total
        self.current = 0
        self.description = description
        self.last_update = 0

    def update(self, increment: int = 1):
        """更新进度"""
        self.current += increment
        self._display()

    def _display(self):
        """显示进度"""
        if self.current == 0 or self.current == self.total:
            percentage = 100 if self.current == self.total else 0
            bar_length = 30
            filled = int(bar_length * percentage / 100) if percentage > 0 else 0
            bar = '█' * filled + '░' * (bar_length - filled)
            sys.stdout.write(f"\r{self.description}: [{bar}] {percentage}% ({self.current}/{self.total})")
            sys.stdout.flush()
        elif self.current - self.last_update >= max(1, self.total // 10):
            percentage = int(self.current * 100 / self.total)
            bar_length = 30
            filled = int(bar_length * percentage / 100)
            bar = '█' * filled + '░' * (bar_length - filled)
            sys.stdout.write(f"\r{self.description}: [{bar}] {percentage}% ({self.current}/{self.total})")
            sys.stdout.flush()
            self.last_update = self.current

    def finish(self):
        """完成进度显示"""
        sys.stdout.write(f"\r{self.description}: [{'█' * 30}] 100% ({self.total}/{self.total})\n")
        sys.stdout.flush()


def clean_mermaid_code(mermaid_code: str) -> str:
    """
    清理Mermaid代码，使其更易于被Kroki.io解析

    Args:
        mermaid_code: 原始Mermaid代码

    Returns:
        清理后的Mermaid代码
    """
    lines = mermaid_code.strip().split('\n')
    cleaned_lines = []

    for line in lines:
        # 移除空行
        stripped = line.strip()
        if not stripped:
            continue
        # 移除注释行
        if stripped.startswith('%%'):
            continue
        cleaned_lines.append(line)

    return '\n'.join(cleaned_lines)


def create_placeholder_image(
    output_path: str,
    width: int = 800,
    height: int = 400,
    error_message: str = "图表转换失败"
) -> bool:
    """
    创建占位图片（无需Pillow依赖，使用最小化方案）

    Args:
        output_path: 输出图片路径
        width: 图片宽度
        height: 图片高度
        error_message: 错误信息

    Returns:
        是否成功创建
    """
    try:
        # 使用最小化PNG创建方案
        # 创建一个简单的1x1 PNG（最小可行PNG）
        minimal_png = b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01\x08\x06\x00\x00\x00\x1f\x15\xc4\x89\x00\x00\x00\rIDATx\x9cc\xf8\xcf\xc0\x00\x00\x00\x03\x00\x01\x00\x00\x00\x00IEND\xaeB`\x82'
        with open(output_path, 'wb') as f:
            f.write(minimal_png)
        return True
    except Exception:
        return False


def convert_mermaid_to_png(
    md_content: str,
    assets_dir: str,
    software_name: str,
    max_retries: int = 3
) -> List[Dict[str, Any]]:
    """
    将Markdown中的Mermaid代码块转换为PNG图片

    Args:
        md_content: Markdown文档内容
        assets_dir: 资源目录路径（用于保存PNG图片）
        software_name: 软件名称（用于图片命名）
        max_retries: 最大重试次数

    Returns:
        转换结果列表，每个元素为字典，格式：
        {
            'index': 1,                    # 图表序号
            'filename': 'xxx_图表1.png',   # 图片文件名
            'filepath': '/path/to/file',   # 完整路径
            'success': True,               # 是否成功
            'error': None                  # 错误信息（失败时）
        }
    """
    # 确保assets目录存在
    os.makedirs(assets_dir, exist_ok=True)

    # 提取所有mermaid代码块
    pattern = r'```mermaid\s*\n(.*?)\n```'
    matches = re.findall(pattern, md_content, re.DOTALL)

    if not matches:
        print(f"未找到Mermaid代码块")
        return []

    results = []
    success_count = 0
    fail_count = 0

    # 添加进度显示
    progress = ProgressTracker(len(matches), "转换Mermaid图表")

    for idx, mermaid_code in enumerate(matches, 1):
        # 清理mermaid代码
        mermaid_code = clean_mermaid_code(mermaid_code)

        # 生成文件名
        filename = f"{software_name}_图表{idx}.png"
        output_path = os.path.join(assets_dir, filename)

        success = False
        error_msg = None

        for retry in range(max_retries):
            try:
                # 调用Kroki.io API转换mermaid为PNG
                response = requests.post(
                    "https://kroki.io/mermaid/png",
                    data=mermaid_code.encode('utf-8'),
                    headers={
                        'Content-Type': 'text/plain; charset=utf-8',
                        'Accept': 'image/png'
                    },
                    timeout=60
                )

                if response.status_code == 200 and len(response.content) > 0:
                    with open(output_path, 'wb') as f:
                        f.write(response.content)
                    success = True
                    success_count += 1
                    break
                else:
                    error_msg = f"API返回状态码: {response.status_code}"
            except requests.Timeout:
                error_msg = "请求超时"
            except requests.RequestException as e:
                error_msg = f"网络请求失败: {str(e)}"
            except Exception as e:
                error_msg = f"未知错误: {str(e)}"

        # 如果转换失败，生成占位图片
        if not success:
            fail_count += 1
            placeholder_created = create_placeholder_image(output_path)
            if not placeholder_created:
                error_msg = f"{error_msg} (占位图片创建也失败)"

        # 记录结果
        results.append({
            'index': idx,
            'filename': filename,
            'filepath': output_path,
            'success': success,
            'error': error_msg
        })

        progress.update(1)

    progress.finish()

    print(f"共处理 {len(results)} 个Mermaid图表 (成功: {success_count}, 失败: {fail_count})，保存至: {assets_dir}")

    # 输出失败详情
    failed_items = [r for r in results if not r['success']]
    if failed_items:
        print("转换失败的图表:")
        for item in failed_items:
            print(f"  - 图表{item['index']}: {item['error']}")

    return results


def convert_mermaid_to_png_from_file(
    md_file: str,
    assets_dir: str,
    software_name: str
) -> List[Dict[str, Any]]:
    """
    从Markdown文件中提取Mermaid代码块并转换为PNG图片

    Args:
        md_file: Markdown文件路径
        assets_dir: 资源目录路径
        software_name: 软件名称

    Returns:
        转换结果列表
    """
    # 转换为绝对路径并规范化
    md_file = os.path.abspath(md_file)
    assets_dir = os.path.abspath(assets_dir)

    # 检查文件是否存在
    if not os.path.exists(md_file):
        raise FileNotFoundError(f"Markdown文件不存在: {md_file}\n当前工作目录: {os.getcwd()}")

    # 读取Markdown文件
    with open(md_file, 'r', encoding='utf-8') as f:
        md_content = f.read()

    return convert_mermaid_to_png(md_content, assets_dir, software_name)


def replace_mermaid_blocks_with_images(
    md_content: str,
    results: List[Dict[str, Any]]
) -> str:
    """
    将Markdown中的Mermaid代码块替换为图片引用或占位标记

    核心改进：使用位置标记法确保图片插入位置正确，
    即使某些图表转换失败也不会导致后续图片错位。

    Args:
        md_content: 原始Markdown内容
        results: 转换结果列表，由convert_mermaid_to_png返回

    Returns:
        替换后的Markdown内容
    """
    if not results:
        return md_content

    # 找到所有mermaid代码块的位置
    pattern = r'```mermaid\s*\n(.*?)\n```'
    matches = list(re.finditer(pattern, md_content, re.DOTALL))

    if not matches:
        return md_content

    # 构建替换映射：每个匹配位置对应要替换的内容
    # 我们从后往前替换，避免索引变化影响前面的替换
    result_map = {}
    for i, match in enumerate(matches):
        chart_index = i + 1  # 图表序号从1开始
        if chart_index <= len(results):
            result = results[chart_index - 1]
            if result['success']:
                # 成功：使用图片引用
                result_map[match.start()] = f'\n\n![图表{chart_index}]({result["filename"]})\n\n'
            else:
                # 失败：使用占位标记，带错误说明
                result_map[match.start()] = f'\n\n[图表{chart_index}转换失败: {result["error"]}]\n\n'

    # 按位置降序排序，从后往前替换
    sorted_positions = sorted(result_map.keys(), reverse=True)

    content = md_content
    for pos in sorted_positions:
        match = next((m for m in matches if m.start() == pos), None)
        if match:
            content = content[:match.start()] + result_map[pos] + content[match.end():]

    return content


def count_mermaid_blocks(md_content: str) -> int:
    """
    统计Markdown文档中的Mermaid代码块数量

    Args:
        md_content: Markdown文档内容

    Returns:
        Mermaid代码块数量
    """
    pattern = r'```mermaid\s*\n.*?\n```'
    matches = re.findall(pattern, md_content, re.DOTALL)
    return len(matches)


if __name__ == "__main__":
    import argparse
    import json

    parser = argparse.ArgumentParser(description='将Markdown中的Mermaid代码块转换为PNG图片')
    parser.add_argument('md_file', help='Markdown文件路径')
    parser.add_argument('assets_dir', help='资源目录路径（用于保存PNG图片）')
    parser.add_argument('software_name', help='软件名称（用于图片命名）')

    args = parser.parse_args()

    # 从文件转换
    results = convert_mermaid_to_png_from_file(args.md_file, args.assets_dir, args.software_name)

    # 输出JSON格式结果（便于程序解析）
    output = {
        'success': all(r['success'] for r in results),
        'total': len(results),
        'success_count': sum(1 for r in results if r['success']),
        'failed_count': sum(1 for r in results if not r['success']),
        'results': results
    }
    print(json.dumps(output, ensure_ascii=False, indent=2))

    # 如果有失败的，返回非零退出码
    if not output['success']:
        sys.exit(1)
