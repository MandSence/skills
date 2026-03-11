# Mermaid语法快速参考

## 基础规则

- 统一使用英文半角符号
- 关键字推荐使用小写
- 节点ID使用英文+数字+下划线，无空格、中文
- 注释使用 `%%` 开头

## 常用图表类型

### 1. Flowchart（流程图）- 用于业务流程

```mermaid
flowchart TD
    start(开始) --> step1[操作步骤1]
    step1 --> judge{条件判断?}
    judge -- 是 --> step2[分支1]
    judge -- 否 --> step3[分支2]
    step2 --> end_node(结束)
    step3 --> end_node
```

**节点类型**：
- `start(开始)` / `end(结束)`: 圆角节点，用于流程起始和结束
- `step1[操作步骤]`: 矩形节点，普通操作步骤
- `judge{条件判断?}`: 菱形节点，条件判断

### 2. Sequence Diagram（时序图）- 用于接口交互

```mermaid
sequenceDiagram
    participant U as 用户
    participant F as 前端
    participant B as 后端
    U->>F: 提交请求
    F->>B: 发送API调用
    B-->>F: 返回结果
    F-->>U: 显示结果
```

**消息类型**：
- `U->>F`: 同步消息（实线箭头）
- `B-->>F`: 返回消息（虚线箭头）

### 3. Class Diagram（类图）- 用于数据模型

```mermaid
classDiagram
    class User{
        -id: Long
        -name: String
        +getName(): String
    }
    class Order{
        -orderId: String
        +calculateTotal(): Number
    }
    User "1" --> "*" Order: 用户下单
```

**关系符号**：
- `<|--`: 继承关系（子类指向父类）
- `-->`: 关联关系
- `*--`: 聚合关系

### 4. 架构图示例

```mermaid
flowchart TD
    subgraph 前端层
        web[Web浏览器]
        mobile[移动端]
    end

    subgraph 网关层
        gateway[API网关]
    end

    subgraph 业务层
        service1[服务模块1]
        service2[服务模块2]
    end

    web --> gateway
    mobile --> gateway
    gateway --> service1
    gateway --> service2
```
