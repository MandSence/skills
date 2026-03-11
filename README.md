# ckh-marketplace 插件市场
这是一个用于存储和分享日常工作技能、工具、插件等的插件市场。

## 目录结构

```
ckl-marketplace/
├── .claude-plugin/
│   └── marketplace.json    # 插件市场配置文件
└── skills/
│    ├── code-extractor/           # 代码提取器技能
│    ├── code-from-design-doc/     # 基于系统设计文档生成源代码技能
│    ├── mermaid-to-png/           # Mermaid 图转换为 PNG 图片技能
│    └── software-copyright-applicant/  # 软著编写技能
└── README.md    # 插件市场说明文档
```

## skills下技能概览
### code-extractor
对系统源代码进行代码抽取，并生成代码提取文件。

### code-from-design-doc
基于系统设计文档生成源代码。

### mermaid-to-png
将Mermaid图表代码转换为PNG图片，用于文档、演示等应用中。

### software-copyright-applicant
编写软件著作权申请文档，包括：系统设计说明文档、源代码提取文档
