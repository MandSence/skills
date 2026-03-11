# 架构与技术栈参考指南

## 目录
- [1. 主流架构模式](#1-主流架构模式)
  - [1.1 按使用场景分类](#11-按使用场景分类)
  - [1.2 关键选型建议](#12-关键选型建议)
- [2. 主流技术栈](#2-主流技术栈)
  - [2.1 后端技术栈](#21-后端技术栈)
  - [2.2 前端技术栈](#22-前端技术栈)
  - [2.3 全栈快速开发选项](#23-全栈快速开发选项)
- [3. 主流框架](#3-主流框架)
  - [3.1 后端框架](#31-后端框架)
  - [3.2 前端框架](#32-前端框架)
  - [3.3 辅助/通用框架](#33-辅助通用框架)
- [4. AI能力对接框架](#4-ai能力对接框架)
  - [4.1 Python AI框架](#41-python-ai框架)
  - [4.2 Java AI框架](#42-java-ai框架)
  - [4.3 AI场景选型指南](#43-ai场景选型指南)
  - [4.4 AI项目目录结构](#44-ai项目目录结构)
- [5. 项目目录结构建议](#5-项目目录结构建议)
  - [5.1 后端项目结构](#51-后端项目结构)
    - [5.1.1 单体架构（精简版）](#511-单体架构精简版)
    - [5.1.2 分层架构（MVC）](#512-分层架构mvc)
    - [5.1.3 微服务架构](#513-微服务架构)
  - [5.2 前端项目结构](#52-前端项目结构)
    - [5.2.1 Vue3 项目结构](#521-vue3-项目结构)
    - [5.2.2 React 项目结构](#522-react-项目结构)
- [6. 总结与快速参考](#6-总结与快速参考)

---

## 1. 主流架构模式

### 1.1 按使用场景分类

| 架构类型 | 核心特点 | 适用场景 | 核心优势 |
|---------|---------|---------|---------|
| **微服务架构** | 将系统拆分为独立部署的小型服务（如用户服务、订单服务），服务间通过API通信 | 中大型系统、高并发/高可用需求（如电商、政务系统） | 解耦、易扩展、故障隔离 |
| **分层架构（经典）** | 按职责分层：表现层→业务层→数据访问层→数据层（MVC是分层的子集） | 中小型单体系统（如管理后台、工具类系统） | 结构清晰、开发维护成本低 |
| **事件驱动架构** | 基于「事件发布-订阅」模式，异步处理业务（如消息队列） | 高并发、异步场景（如秒杀、日志处理、物联网） | 解耦、峰值抗压、异步解耦 |
| **服务网格（Service Mesh）** | 微服务的进阶版，用Sidecar代理管理服务通信（如Istio） | 超大型微服务集群（如大厂核心业务） | 统一治理（限流/监控/熔断） |
| **单体架构（精简版）** | 所有功能打包为单个应用部署（如Spring Boot单体应用） | 小型工具、原型系统、低并发内部系统 | 开发快、部署简单、成本低 |

### 1.2 关键选型建议

| 系统规模 | 推荐架构 |
|---------|---------|
| **小型系统**（如带宽管理后台） | 优先：**分层架构（MVC）** 或**精简单体架构** |
| **中大型系统**（如电商、政务平台） | 优先：**微服务架构** |
| **高并发/异步场景**（如物联网、秒杀） | 叠加**事件驱动架构** |

---

## 2. 主流技术栈

### 2.1 后端技术栈

| 技术方向 | 主流选型 | 适用场景 |
|---------|---------|---------|
| **开发语言** | Java、Python、Go、Node.js（少量PHP/.NET） | Java：企业级系统；Go：高并发；Python：AI/工具 |
| **数据存储** | MySQL（关系型）、Redis（缓存）、MongoDB（非结构化）、Elasticsearch（搜索） | 通用场景：MySQL+Redis；大数据：ES/MongoDB |
| **中间件** | Kafka/RabbitMQ（消息队列）、Nginx（反向代理）、Zookeeper（服务注册） | 微服务/异步场景必备 |
| **部署/运维** | Docker、K8s、Jenkins（CI/CD）、Prometheus（监控） | 云原生/微服务系统 |

### 2.2 前端技术栈（前后端分离核心）

| 技术方向 | 主流选型 | 适用场景 |
|---------|---------|---------|
| **核心框架** | Vue3（+Vite）、React（+Next.js）、Angular（少量） | 管理后台：Vue3；大型应用：React |
| **工程化工具** | npm/yarn/pnpm、Webpack/Vite、ESLint/Prettier | 前端工程化标配 |
| **移动端适配** | UniApp、React Native、Flutter（跨端） | 需适配移动端的系统（如小程序/APP） |

### 2.3 全栈快速开发选项

| 场景 | 推荐技术栈 |
|-----|----------|
| **轻量场景** | Python（FastAPI）+ Vue3 + MySQL + Redis |
| **企业级场景** | Java（Spring Boot）+ Vue3 + MySQL + Redis + Kafka |
| **高并发场景** | Go（Gin）+ React + MySQL + Redis + K8s |

---

## 3. 主流框架

### 3.1 后端框架

| 开发语言 | 核心框架 | 核心优势 |
|---------|---------|---------|
| **Java** | Spring Boot（微服务基础）<br>Spring Cloud / Spring Cloud Alibaba（微服务全家桶） | 生态完善、企业级标配、易扩展 |
| **Python** | FastAPI（高性能API）<br>Django（全栈）<br>Flask（轻量） | 开发快、易上手、AI生态适配 |
| **Go** | Gin（高性能）、Beego（全栈）、Kitex（微服务） | 高性能、低资源占用、适配高并发 |
| **Node.js** | Express（轻量）、NestJS（企业级） | 前后端同语言、异步非阻塞 |

### 3.2 前端框架

| 框架 | 核心优势 | 适用场景 |
|-----|---------|---------|
| **Vue3** | 易学易用、轻量、生态丰富（Element Plus/Naive UI） | 管理后台、中小型前端项目 |
| **React** | 组件化强、生态庞大（Ant Design/Next.js） | 大型前端应用、跨端开发 |
| **Angular** | 全功能框架、TypeScript原生支持 | 大型企业级前端项目（少量使用） |

### 3.3 辅助/通用框架（全场景）

| 框架/工具 | 用途 | 核心优势 |
|----------|-----|---------|
| **MyBatis / MyBatis-Plus** | Java数据库访问 | 灵活、适配复杂SQL |
| **Hibernate** | Java ORM框架 | 全自动映射、减少SQL编写 |
| **RedisTemplate** | Java操作Redis | 简化Redis操作、适配Spring生态 |
| **Axios** | 前端HTTP请求 | 易用、拦截器完善、适配Promise |

---

## 4. AI能力对接框架

### 4.1 Python AI框架

| 框架名称 | 核心特点 | 适用场景 | 核心优势 |
|---------|---------|---------|---------|
| **LangChain** | 最流行的LLM应用开发框架，支持链式调用、代理、记忆、RAG等 | 复杂LLM应用、RAG系统、AI Agent | 生态最丰富、社区活跃、学习资源多 |
| **LlamaIndex** | 专注于数据索引和检索，RAG领域的领导者 | 文档问答、知识库检索、数据增强生成 | 检索能力强、索引优化好、文档完善 |
| **Haystack** | 深度学习NLP框架，专注搜索和问答 | 企业搜索、文档问答系统、问答机器人 | 支持多种检索器、可定制性强 |
| **Semantic Kernel** | 微软推出的框架，支持多语言（Python、Java、C#） | 企业级AI应用、跨平台AI集成 | 微软生态、企业级支持、跨平台 |
| **AutoGPT** | 自主Agent框架，实现AI自主决策和执行 | 自动化任务执行、自主AI助手 | 自主决策能力强、任务分解能力 |
| **CrewAI** | 多Agent协作框架，支持角色分工和团队协作 | 团队协作式AI任务、复杂工作流 | 角色定义清晰、协作逻辑完善 |
| **LangGraph** | LangChain生态中的图状态管理框架 | 复杂工作流、状态机应用、多Agent系统 | 状态管理强、支持循环、可视化好 |
| **Dify** | 开源LLM应用开发平台，提供可视化界面 | 快速构建AI应用、低代码开发 | 可视化界面、部署简单、中文支持好 |
| **PromptLayer** | 提示词工程和管理平台 | 提示词优化、A/B测试、版本管理 | 提示词管理、性能追踪 |
| **Guidance** | Microsoft的语言控制框架，精细控制输出格式 | 结构化输出、格式约束、代码生成 | 输出控制精确、性能优化好 |

**Python AI框架依赖配置示例：**

```python
# requirements.txt - LangChain 生态
langchain>=0.1.0
langchain-openai>=0.0.5
langchain-community>=0.0.20
langchain-anthropic>=0.1.0
langchain-core>=0.1.0
langchain-experimental>=0.0.50

# LlamaIndex
llama-index>=0.10.0
llama-index-llms-openai>=0.1.0
llama-index-embeddings-openai>=0.1.0
llama-index-vector-stores-chroma>=0.1.0
llama-index-readers-file>=0.1.0

# 向量数据库
chromadb>=0.4.0
pinecone-client>=2.2.0
pgvector>=0.2.0

# 基础依赖
openai>=1.0.0
anthropic>=0.18.0
tiktoken>=0.5.0
```

### 4.2 Java AI框架

| 框架名称 | 核心特点 | 适用场景 | 核心优势 |
|---------|---------|---------|---------|
| **LangChain4j** | LangChain的Java版本，完全兼容生态 | 企业级Java应用、Spring Boot集成 | 与Python LangChain API相似、Spring友好 |
| **Spring AI** | Spring官方AI框架，与Spring生态深度集成 | Spring项目、企业微服务、Spring Cloud | 原生Spring支持、自动配置、生态完善 |
| **Semantic Kernel (Java)** | 微软SK的Java SDK，跨平台支持 | 跨平台企业应用、Azure集成 | 微软支持、跨语言一致、Azure深度集成 |
| **Langchain-java** | 社区维护的LangChain Java实现 | 简单LLM集成、快速原型 | 轻量级、简单易用 |
| **LangStream** | 实时流式AI处理框架 | 实时数据处理、流式AI、IoT | 流式处理强、低延迟 |
| **Milo** | Java AI编排框架 | 工作流编排、任务调度 | 编排能力强、可视化 |
| **Quarkus LangChain4j** | 基于LangChain4j的Quarkus扩展 | 云原生应用、Kubernetes部署 | 启动快、内存占用低 |
| **Ai-LLM** | 轻量级Java LLM客户端库 | 简单API调用、小型项目 | 轻量、无依赖 |
| **Easy-LLM** | 简化的Java LLM集成 | 快速原型开发、教学示例 | API简单、学习成本低 |
| **ZhipuAI Java SDK** | 智谱AI官方Java SDK | 国内大模型接入、国产化需求 | 国内模型、官方支持 |

**Java AI框架依赖配置示例（Maven）：**

```xml
<!-- LangChain4j 核心依赖 -->
<dependency>
    <groupId>dev.langchain4j</groupId>
    <artifactId>langchain4j</artifactId>
    <version>0.29.1</version>
</dependency>

<!-- LLM 提供商 -->
<dependency>
    <groupId>dev.langchain4j</groupId>
    <artifactId>langchain4j-open-ai</artifactId>
    <version>0.29.1</version>
</dependency>

<!-- Spring AI -->
<dependency>
    <groupId>org.springframework.ai</groupId>
    <artifactId>spring-ai-openai-spring-boot-starter</artifactId>
    <version>1.0.0-M2</version>
</dependency>

<!-- 向量存储 -->
<dependency>
    <groupId>dev.langchain4j</groupId>
    <artifactId>langchain4j-pgvector</artifactId>
    <version>0.29.1</version>
</dependency>
```

### 4.3 AI场景选型指南

#### 4.3.1 按开发语言选择

| 开发语言 | 推荐框架 | 适用场景 |
|---------|---------|---------|
| **Python** | LangChain / LlamaIndex | 快速原型、AI研究、创新公司 |
| **Java** | LangChain4j / Spring AI | 企业级系统、Spring生态、金融/政务 |
| **跨语言团队** | Semantic Kernel | 需要Python/Java/C#协作的团队 |

#### 4.3.2 按AI应用类型选择

| 应用类型 | 推荐框架 | 核心考虑 |
|---------|---------|---------|
| **文档问答（RAG）** | LlamaIndex / LangChain | 检索能力、索引优化 |
| **AI Agent** | LangChain + LangGraph / CrewAI | 状态管理、工具调用 |
| **聊天机器人** | LangChain / Spring AI | 对话管理、记忆功能 |
| **代码生成** | LangChain / Guidance | 结构化输出、代码解析 |
| **企业知识库** | LlamaIndex + Haystack | 搜索能力、可扩展性 |
| **低代码平台** | Dify | 可视化界面、部署简单 |

#### 4.3.3 按场景复杂度选择

| 复杂度 | 推荐框架 | 说明 |
|-------|---------|------|
| **简单AI调用** | Ai-LLM / Easy-LLM / 原生API | 单一LLM调用、无复杂逻辑 |
| **中等复杂度** | LangChain / LangChain4j | 链式调用、简单Agent |
| **高复杂度** | LangChain + LangGraph / CrewAI | 多Agent协作、复杂工作流 |
| **企业级** | Spring AI / Semantic Kernel | 企业级支持、安全性、可维护性 |

### 4.4 AI项目目录结构

#### 4.4.1 Python + LangChain 项目结构

```
ai-project/
├── app/
│   ├── __init__.py
│   ├── main.py                                       # 程序入口
│   ├── config/                                       # 配置
│   │   ├── __init__.py
│   │   ├── settings.py                               # AI模型配置
│   │   └── prompts.py                                # 提示词模板
│   ├── agents/                                       # Agent定义
│   │   ├── __init__.py
│   │   ├── base.py                                   # 基础Agent
│   │   ├── research_agent.py
│   │   └── writer_agent.py
│   ├── chains/                                       # 链定义
│   │   ├── __init__.py
│   │   ├── retrieval_chain.py                        # RAG链
│   │   └── conversation_chain.py                     # 对话链
│   ├── tools/                                        # 工具函数
│   │   ├── __init__.py
│   │   ├── search.py
│   │   ├── calculator.py
│   │   └── database.py
│   ├── memory/                                       # 记忆管理
│   │   ├── __init__.py
│   │   ├── base_memory.py
│   │   └── redis_memory.py
│   ├── retrievers/                                   # 检索器
│   │   ├── __init__.py
│   │   ├── vector_store.py                           # 向量存储
│   │   └── hybrid_retriever.py                       # 混合检索
│   ├── embeddings/                                    # 嵌入模型
│   │   ├── __init__.py
│   │   └── custom_embeddings.py
│   ├── indexers/                                     # 文档索引
│   │   ├── __init__.py
│   │   ├── document_loader.py
│   │   └── text_splitter.py
│   ├── api/                                          # API接口
│   │   ├── __init__.py
│   │   ├── v1/
│   │   │   ├── __init__.py
│   │   │   ├── chat.py
│   │   │   ├── rag.py
│   │   │   └── agent.py
│   ├── schemas/                                      # 数据模型
│   │   ├── __init__.py
│   │   ├── chat.py
│   │   └── document.py
│   ├── services/                                     # 业务服务
│   │   ├── __init__.py
│   │   ├── rag_service.py
│   │   └── agent_service.py
│   ├── utils/                                        # 工具函数
│   │   ├── __init__.py
│   │   ├── prompt_utils.py
│   │   └── token_counter.py
│   └── monitors/                                     # 监控
│       ├── __init__.py
│       ├── cost_tracker.py                           # 成本追踪
│       └── performance_tracker.py                   # 性能监控
├── data/                                             # 数据目录
│   ├── documents/                                    # 原始文档
│   ├── indexed/                                      # 索引后的文档
│   └── prompts/                                      # 提示词模板
├── tests/
│   ├── unit/
│   └── integration/
├── prompts/                                          # 提示词文件
│   ├── system/
│   │   ├── agent.txt
│   │   └── rag.txt
│   └── user/
│       ├── chat.txt
│       └── qa.txt
├── requirements.txt
├── .env.example
└── README.md
```

#### 4.4.2 Java + LangChain4j 项目结构

```
ai-project/
├── src/
│   ├── main/
│   │   ├── java/
│   │   │   └── com/
│   │   │       └── example/
│   │   │           ├── AiApplication.java            # 程序入口
│   │   │           ├── config/                       # 配置类
│   │   │           │   ├── LangChainConfig.java
│   │   │           │   ├── EmbeddingModelConfig.java
│   │   │           │   ├── VectorStoreConfig.java
│   │   │           │   └── PromptConfig.java
│   │   │           ├── agent/                        # Agent定义
│   │   │           │   ├── BaseAgent.java
│   │   │           │   ├── ChatAgent.java
│   │   │           │   └── RAGAgent.java
│   │   │           ├── chain/                        # 链定义
│   │   │           │   ├── RetrievalChain.java
│   │   │           │   └── ConversationChain.java
│   │   │           ├── tool/                         # 工具函数
│   │   │           │   ├── SearchTool.java
│   │   │           │   ├── CalculatorTool.java
│   │   │           │   └── DatabaseTool.java
│   │   │           ├── memory/                       # 记忆管理
│   │   │           │   ├── ChatMemoryProvider.java
│   │   │           │   └── PersistentChatMemory.java
│   │   │           ├── retriever/                    # 检索器
│   │   │           │   ├── EmbeddingModel.java
│   │   │           │   ├── EmbeddingStore.java
│   │   │           │   └── Retriever.java
│   │   │           ├── service/                      # 业务服务
│   │   │           │   ├── RagService.java
│   │   │           │   ├── AgentService.java
│   │   │           │   └── ChatService.java
│   │   │           ├── controller/                   # REST API
│   │   │           │   ├── ChatController.java
│   │   │           │   ├── RAGController.java
│   │   │           │   └── AgentController.java
│   │   │           ├── dto/                          # 数据传输对象
│   │   │           │   ├── request/
│   │   │           │   │   ├── ChatRequest.java
│   │   │   │   │   └── RAGRequest.java
│   │   │           │   └── response/
│   │   │           │       └── ChatResponse.java
│   │   │           ├── model/                        # 数据模型
│   │   │           │   ├── Document.java
│   │   │           │   └── Message.java
│   │   │           ├── monitor/                      # 监控
│   │   │           │   ├── CostTracker.java
│   │   │           │   └── PerformanceTracker.java
│   │   │           └── common/                       # 通用组件
│   │   │               ├── exception/
│   │   │               │   └── AIException.java
│   │   │               ├── constant/
│   │   │               │   └── ModelConstants.java
│   │   │               └── util/
│   │   │                   ├── PromptUtil.java
│   │   │                   └── TokenCounter.java
│   │   └── resources/
│   │       ├── application.yml
│   │       └── prompts/                              # 提示词模板
│   │           ├── system/
│   │           │   ├── agent.txt
│   │           │   └── rag.txt
│   │           └── user/
│   │               ├── chat.txt
│   │               └── qa.txt
│   └── test/                                          # 测试
│       ├── unit/
│       └── integration/
├── data/                                             # 数据目录
│   ├── documents/                                    # 原始文档
│   └── indexed/                                      # 索引后的文档
├── pom.xml
└── README.md
```

---

## 5. 项目目录结构建议

### 5.1 后端项目结构

#### 5.1.1 单体架构（精简版）

**适用于：** 小型工具、原型系统、低流量内部系统

**结构（Java/Spring Boot示例）：**

```
project-name/
├── src/
│   ├── main/
│   │   ├── java/
│   │   │   └── com/
│   │   │       └── example/
│   │   │           ├── ProjectApplication.java      # 程序入口
│   │   │           ├── config/                       # 配置类
│   │   │           ├── controller/                   # REST API端点
│   │   │           ├── service/                      # 业务逻辑
│   │   │           ├── repository/                   # 数据访问
│   │   │           ├── entity/                       # 数据库模型
│   │   │           ├── dto/                          # 数据传输对象
│   │   │           └── common/                       # 通用工具
│   │   └── resources/
│   │       ├── application.yml                       # 配置文件
│   │       └── application-dev.yml                   # 开发环境配置
│   └── test/                                          # 单元/集成测试
├── build.gradle                                       # 构建配置
├── settings.gradle
└── README.md
```

**结构（Python/FastAPI示例）：**

```
project-name/
├── app/
│   ├── __init__.py
│   ├── main.py                                       # 程序入口
│   ├── config.py                                     # 配置
│   ├── api/                                          # API路由
│   │   ├── __init__.py
│   │   └── v1/
│   │       ├── __init__.py
│   │       └── endpoints/
│   ├── models/                                       # 数据库模型
│   ├── schemas/                                      # Pydantic模式（DTOs）
│   ├── services/                                     # 业务逻辑
│   ├── core/                                         # 核心工具
│   │   ├── security.py
│   │   └── database.py
│   └── utils/                                        # 通用工具
├── tests/                                            # 单元/集成测试
├── requirements.txt                                  # Python依赖
├── .env.example                                      # 环境变量模板
└── README.md
```

---

#### 5.1.2 分层架构（MVC）

**适用于：** 中小型单体系统、管理后台、工具类系统

**结构（Java/Spring Boot示例）：**

```
project-name/
├── src/
│   ├── main/
│   │   ├── java/
│   │   │   └── com/
│   │   │       └── example/
│   │   │           ├── ProjectApplication.java
│   │   │           ├── config/                       # 配置层
│   │   │           │   ├── SecurityConfig.java
│   │   │           │   ├── DatabaseConfig.java
│   │   │           │   └── RedisConfig.java
│   │   │           ├── controller/                   # 表现层
│   │   │           │   ├── UserController.java
│   │   │           │   └── OrderController.java
│   │   │           ├── service/                      # 业务逻辑层
│   │   │           │   ├── UserService.java
│   │   │           │   ├── impl/
│   │   │           │   │   └── UserServiceImpl.java
│   │   │           │   └── OrderService.java
│   │   │           ├── repository/                   # 数据访问层
│   │   │           │   ├── UserRepository.java
│   │   │           │   └── OrderRepository.java
│   │   │           ├── entity/                       # 数据模型
│   │   │           │   ├── User.java
│   │   │           │   └── Order.java
│   │   │           ├── dto/                          # 数据传输对象
│   │   │           │   ├── request/
│   │   │           │   │   ├── UserCreateRequest.java
│   │   │           │   │   └── UserUpdateRequest.java
│   │   │           │   └── response/
│   │   │           │       └── UserResponse.java
│   │   │           ├── common/                       # 通用组件
│   │   │           │   ├── exception/
│   │   │           │   │   └── GlobalExceptionHandler.java
│   │   │           │   ├── constant/
│   │   │           │   │   └── ErrorCode.java
│   │   │           │   └── util/
│   │   │           │       └── DateUtil.java
│   │   │           └── mapper/                       # 对象映射（MapStruct）
│   │   │               └── UserMapper.java
│   │   └── resources/
│   │       ├── application.yml
│   │       ├── mapper/                               # MyBatis XML文件
│   │       └── static/                               # 静态资源
│   └── test/                                          # 测试
│       ├── unit/
│       └── integration/
├── build.gradle
└── README.md
```

**结构（Python/FastAPI示例）：**

```
project-name/
├── app/
│   ├── __init__.py
│   ├── main.py                                       # 程序入口
│   ├── config/                                       # 配置
│   │   ├── __init__.py
│   │   ├── settings.py                               # 设置管理
│   │   └── logging.py                                # 日志配置
│   ├── api/                                          # 表现层
│   │   ├── __init__.py
│   │   ├── deps.py                                   # 依赖注入（auth, db）
│   │   └── v1/
│   │       ├── __init__.py
│   │       └── endpoints/
│   │           ├── __init__.py
│   │           ├── users.py
│   │           └── orders.py
│   ├── core/                                         # 核心层
│   │   ├── __init__.py
│   │   ├── security.py                               # 安全逻辑
│   │   ├── database.py                               # 数据库连接
│   │   └── redis.py                                  # Redis连接
│   ├── models/                                       # 数据模型（ORM）
│   │   ├── __init__.py
│   │   ├── base.py                                   # 基础模型
│   │   ├── user.py
│   │   └── order.py
│   ├── schemas/                                      # Pydantic模式（DTO）
│   │   ├── __init__.py
│   │   ├── user.py
│   │   └── order.py
│   ├── services/                                     # 业务逻辑层
│   │   ├── __init__.py
│   │   ├── user_service.py
│   │   └── order_service.py
│   ├── repositories/                                 # 数据访问层
│   │   ├── __init__.py
│   │   ├── base_repository.py
│   │   ├── user_repository.py
│   │   └── order_repository.py
│   └── utils/                                        # 通用工具
│       ├── __init__.py
│       ├── validators.py
│       └── helpers.py
├── tests/
│   ├── unit/
│   └── integration/
├── alembic/                                          # 数据库迁移
├── requirements.txt
├── alembic.ini
├── .env.example
└── README.md
```

---

#### 5.1.3 微服务架构

**适用于：** 中大型系统、高并发、高可用需求

**Monorepo结构（推荐用于相关服务）：**

```
project-name/
├── services/                                         # 所有微服务
│   ├── user-service/                                 # 用户服务
│   │   ├── src/
│   │   │   ├── main/
│   │   │   │   ├── java/
│   │   │   │   │   └── com/
│   │   │   │   │       └── example/
│   │   │   │   │           └── user/
│   │   │   │   │               ├── UserServiceApplication.java
│   │   │   │   │               ├── config/
│   │   │   │   │               ├── controller/
│   │   │   │   │               ├── service/
│   │   │   │   │               ├── repository/
│   │   │   │   │               ├── entity/
│   │   │   │   │               ├── dto/
│   │   │   │   │               └── common/
│   │   │   │   └── resources/
│   │   │   │       ├── application.yml
│   │   │   │       └── bootstrap.yml                 # 服务发现配置
│   │   │   └── test/
│   │   ├── Dockerfile
│   │   └── build.gradle
│   │
│   ├── order-service/                                # 订单服务
│   │   ├── src/
│   │   │   └── (类似结构)
│   │   ├── Dockerfile
│   │   └── build.gradle
│   │
│   ├── payment-service/                              # 支付服务
│   ├── notification-service/                         # 通知服务
│   └── gateway-service/                               # API网关
│
├── shared/                                           # 共享代码
│   ├── common/                                        # 通用工具
│   │   ├── src/
│   │   │   └── main/
│   │   │       └── java/
│   │   │           └── com/
│   │   │               └── example/
│   │   │                   └── common/
│   │   │                       ├── exception/
│   │   │                       ├── constant/
│   │   │                       ├── util/
│   │   │                       └── dto/              # 共享DTOs
│   │   └── build.gradle
│   │
│   └── api/                                           # API契约（OpenAPI）
│       ├── user-api.yaml
│       ├── order-api.yaml
│       └── payment-api.yaml
│
├── infrastructure/                                   # 基础设施代码
│   ├── config-server/                                 # 配置中心
│   ├── registry-server/                               # 服务注册中心（Eureka/Nacos）
│   ├── oauth-server/                                  # OAuth2认证服务器
│   └── monitoring/
│       ├── prometheus/
│       ├── grafana/
│       └── jaeger/                                    # 分布式追踪
│
├── deployments/                                      # 部署配置
│   ├── docker/
│   │   ├── docker-compose.yml                        # 本地开发
│   │   └── docker-compose.prod.yml                    # 生产环境
│   ├── k8s/                                           # Kubernetes清单
│   │   ├── base/
│   │   ├── overlays/dev/
│   │   └── overlays/prod/
│   └── terraform/                                     # 云资源IaC
│
├── scripts/                                          # 构建/部署脚本
│   ├── build-all.sh
│   ├── deploy-dev.sh
│   └── deploy-prod.sh
│
├── docs/                                             # 文档
│   ├── api/
│   ├── architecture/
│   └── deployment/
│
├── build.gradle                                       # 根构建文件
├── settings.gradle
└── README.md
```

**Multi-repo结构（每个服务一个仓库）：**

```
user-service/
├── src/
│   ├── main/
│   │   ├── java/
│   │   │   └── com/
│   │   │       └── example/
│   │   │           └── user/
│   │   │               ├── UserServiceApplication.java
│   │   │               ├── config/
│   │   │               │   ├── SecurityConfig.java
│   │   │               │   ├── DatabaseConfig.java
│   │   │               │   ├── RedisConfig.java
│   │   │               │   └── FeignConfig.java                    # 服务间调用
│   │   │               ├── controller/
│   │   │               ├── service/
│   │   │               ├── repository/
│   │   │               ├── entity/
│   │   │               ├── dto/
│   │   │               ├── common/
│   │   │               └── client/                                   # 外部服务客户端
│   │   │                   └── OrderClient.java
│   │   └── resources/
│   │       ├── application.yml
│   │       └── bootstrap.yml
│   └── test/
├── Dockerfile
├── deploy/
│   ├── k8s/
│   └── docker-compose.yml
├── build.gradle
└── README.md
```

---

### 5.2 前端项目结构

#### 5.2.1 Vue3 项目结构

**适用于：** 管理后台、中小型前端项目

```
frontend-project/
├── public/                                           # 静态资源
│   ├── favicon.ico
│   └── index.html
├── src/
│   ├── main.ts                                        # 程序入口
│   ├── App.vue                                        # 根组件
│   ├── components/                                    # 可复用组件
│   │   ├── common/                                    # 通用组件
│   │   │   ├── Button.vue
│   │   │   ├── Input.vue
│   │   │   └── Modal.vue
│   │   └── business/                                 # 业务组件
│   │       ├── UserCard.vue
│   │       └── OrderList.vue
│   ├── views/                                         # 页面组件
│   │   ├── Home.vue
│   │   ├── About.vue
│   │   └── users/
│   │       ├── UserList.vue
│   │       └── UserDetail.vue
│   ├── router/                                        # Vue Router配置
│   │   ├── index.ts
│   │   └── modules/
│   │       ├── user.ts
│   │       └── order.ts
│   ├── store/                                         # Pinia状态管理
│   │   ├── index.ts
│   │   ├── modules/
│   │   │   ├── user.ts
│   │   │   └── order.ts
│   │   └── types.ts
│   ├── api/                                           # API请求
│   │   ├── index.ts                                  # Axios实例
│   │   ├── user.ts
│   │   └── order.ts
│   ├── composables/                                   # Vue 3组合式函数
│   │   ├── useAuth.ts
│   │   ├── useTable.ts
│   │   └── useModal.ts
│   ├── hooks/                                         # 自定义钩子（旧版）
│   ├── utils/                                         # 工具函数
│   │   ├── request.ts                                 # 请求拦截器
│   │   ├── format.ts
│   │   └── validate.ts
│   ├── assets/                                        # 资源文件
│   │   ├── images/
│   │   ├── icons/
│   │   └── styles/
│   │       ├── index.scss
│   │       ├── variables.scss
│   │       └── mixins.scss
│   ├── types/                                         # TypeScript定义
│   │   ├── user.ts
│   │   ├── order.ts
│   │   └── api.ts
│   ├── directives/                                    # 自定义指令
│   │   └── loading.ts
│   ├── layout/                                        # 布局组件
│   │   ├── DefaultLayout.vue
│   │   ├── AuthLayout.vue
│   │   └── components/
│   │       ├── Header.vue
│   │       ├── Sidebar.vue
│   │       └── Footer.vue
│   └── constants/                                     # 常量
│       ├── config.ts
│       └── enums.ts
├── tests/                                            # 测试文件
│   ├── unit/
│   └── e2e/
├── .env                                               # 环境变量
├── .env.development
├── .env.production
├── vite.config.ts                                     # Vite配置
├── tsconfig.json                                      # TypeScript配置
├── package.json
├── tsconfig.app.json
├── tsconfig.node.json
└── README.md
```

---

#### 5.2.2 React 项目结构

**适用于：** 大型前端应用、跨平台开发

**Create React App / Vite 结构：**

```
frontend-project/
├── public/                                           # 静态资源
│   ├── favicon.ico
│   └── index.html
├── src/
│   ├── main.tsx                                       # 程序入口
│   ├── App.tsx                                        # 根组件
│   ├── index.css                                      # 全局样式
│   ├── components/                                    # 可复用组件
│   │   ├── common/                                    # 通用UI组件
│   │   │   ├── Button/
│   │   │   │   ├── Button.tsx
│   │   │   │   ├── Button.test.tsx
│   │   │   │   └── index.ts
│   │   │   ├── Input/
│   │   │   └── Modal/
│   │   ├── layout/                                    # 布局组件
│   │   │   ├── Header/
│   │   │   ├── Sidebar/
│   │   │   └── MainLayout/
│   │   └── business/                                 # 业务组件
│   │       ├── UserCard/
│   │       └── OrderList/
│   ├── pages/                                         # 页面组件
│   │   ├── Home/
│   │   │   ├── Home.tsx
│   │   │   ├── Home.test.tsx
│   │   │   └── index.ts
│   │   ├── About/
│   │   └── users/
│   │       ├── UserList/
│   │       ├── UserDetail/
│   │       └── index.ts
│   ├── router/                                        # React Router配置
│   │   ├── index.tsx
│   │   ├── routes.tsx                                # 路由定义
│   │   └── guards/                                    # 路由守卫
│   │       └── AuthGuard.tsx
│   ├── store/                                         # 状态管理（Redux/Zustand）
│   │   ├── index.ts
│   │   ├── slices/                                   # Redux slices
│   │   │   ├── userSlice.ts
│   │   │   └── orderSlice.ts
│   │   └── hooks.ts                                   # 自定义钩子
│   ├── services/                                      # API服务
│   │   ├── api/                                      # API客户端
│   │   │   ├── client.ts
│   │   │   ├── interceptors.ts
│   │   │   └── index.ts
│   │   ├── user/
│   │   │   ├── userService.ts
│   │   │   └── types.ts
│   │   └── order/
│   │       └── orderService.ts
│   ├── hooks/                                         # 自定义React钩子
│   │   ├── useAuth.ts
│   │   ├── useTable.ts
│   │   ├── useModal.ts
│   │   └── useDebounce.ts
│   ├── utils/                                         # 工具函数
│   │   ├── format.ts
│   │   ├── validate.ts
│   │   ├── storage.ts
│   │   └── date.ts
│   ├── assets/                                        # 资源文件
│   │   ├── images/
│   │   ├── icons/
│   │   └── styles/
│   │       ├── globals.css
│   │       ├── variables.css
│   │       └── mixins.css
│   ├── types/                                         # TypeScript定义
│   │   ├── user.ts
│   │   ├── order.ts
│   │   ├── api.ts
│   │   └── index.ts
│   ├── contexts/                                      # React Context
│   │   ├── AuthContext.tsx
│   │   └── ThemeContext.tsx
│   ├── config/                                        # 配置
│   │   └── index.ts
│   ├── constants/                                     # 常量
│   │   ├── routes.ts
│   │   ├── api.ts
│   │   └── enums.ts
│   └── styles/                                         # 样式模块
│       └── themes/
│           ├── light.ts
│           └── dark.ts
├── tests/                                            # 测试文件
│   ├── unit/
│   └── integration/
├── .env                                               # 环境变量
├── .env.development
├── .env.production
├── vite.config.ts                                     # Vite配置
├── tsconfig.json                                      # TypeScript配置
├── package.json
└── README.md
```

**Next.js 结构（用于 SSR/SSG）：**

```
nextjs-project/
├── public/                                           # 静态资源
│   ├── images/
│   └── favicon.ico
├── src/
│   ├── app/                                           # App Router（Next.js 13+）
│   │   ├── layout.tsx                                 # 根布局
│   │   ├── page.tsx                                   # 首页
│   │   ├── loading.tsx                                # 全局加载
│   │   ├── error.tsx                                  # 错误页
│   │   ├── not-found.tsx                              # 404页
│   │   ├── api/                                       # API路由
│   │   │   ├── users/
│   │   │   │   └── route.ts
│   │   │   └── auth/
│   │   │       └── route.ts
│   │   ├── (auth)/                                    # 路由组
│   │   │   ├── login/
│   │   │   │   └── page.tsx
│   │   │   └── register/
│   │   │       └── page.tsx
│   │   ├── (dashboard)/                               # 带布局的路由组
│   │   │   ├── layout.tsx
│   │   │   ├── users/
│   │   │   │   └── page.tsx
│   │   │   └── orders/
│   │   │       └── page.tsx
│   │   └── global.css                                 # 全局样式
│   │
│   ├── components/                                    # React组件
│   │   ├── ui/                                        # UI组件
│   │   │   ├── Button.tsx
│   │   │   ├── Input.tsx
│   │   │   └── Modal.tsx
│   │   ├── layout/                                    # 布局组件
│   │   │   ├── Header.tsx
│   │   │   ├── Sidebar.tsx
│   │   │   └── Footer.tsx
│   │   ├── features/                                  # 特定功能组件
│   │   │   ├── UserCard.tsx
│   │   │   └── OrderList.tsx
│   │   └── providers/                                 # React providers
│   │       ├── SessionProvider.tsx
│   │       └── ThemeProvider.tsx
│   │
│   ├── lib/                                           # 工具库
│   │   ├── db.ts                                      # 数据库工具
│   │   ├── auth.ts                                    # 认证工具
│   │   ├── utils.ts                                   # 辅助函数
│   │   ├── api.ts                                     # API客户端
│   │   └── validations.ts                             # 验证模式
│   │
│   ├── hooks/                                         # 自定义钩子
│   │   ├── useAuth.ts
│   │   ├── useTable.ts
│   │   └── useDebounce.ts
│   │
│   ├── store/                                         # 状态管理
│   │   ├── index.ts
│   │   └── slices/
│   │
│   ├── types/                                         # TypeScript类型
│   │   ├── user.ts
│   │   ├── order.ts
│   │   └── index.ts
│   │
│   ├── config/                                        # 配置
│   │   └── site.ts
│   │
│   ├── styles/                                        # 样式
│   │   └── globals.css
│   │
│   └── middleware.ts                                  # Next.js中间件
│
├── prisma/                                           # 数据库模式（Prisma）
│   └── schema.prisma
│
├── .env.local                                        # 本地环境变量
├── next.config.js                                     # Next.js配置
├── tsconfig.json                                      # TypeScript配置
├── tailwind.config.ts                                 # Tailwind CSS配置
├── package.json
└── README.md
```

---

## 6. 总结与快速参考

### 6.1 架构选型

| 系统规模 | 推荐架构 |
|---------|---------|
| 小型系统 | 分层/单体架构 |
| 中大型系统 | 微服务架构 |
| 高并发 | 叠加事件驱动架构 |

### 6.2 技术栈选型

| 场景 | 推荐技术栈 |
|-----|----------|
| 企业级 | Java + Vue3 |
| 轻量/AI场景 | Python + Vue3 |
| 高并发 | Go + React |

### 6.3 框架选型

| 类别 | 语言 | 推荐框架 |
|-----|-----|---------|
| 后端 | Java | Spring Boot |
| 后端 | Python | FastAPI |
| 后端 | Go | Gin |
| 前端（管理后台） | - | Vue3 |
| 前端（大型应用） | - | React |

### 6.4 目录结构选型

| 项目类型 | 推荐结构 |
|---------|---------|
| 小型后端（Java） | 单体架构（精简版） |
| 小型后端（Python） | 单体架构（精简版） |
| 中型后端（Java） | 分层架构（MVC） |
| 中型后端（Python） | 分层架构（MVC） |
| 大型后端 | 微服务架构（Monorepo） |
| 前端管理后台 | Vue3 项目结构 |
| 大型前端应用 | React 项目结构 |
| SEO关键应用 | Next.js 结构 |
