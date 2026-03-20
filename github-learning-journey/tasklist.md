# GitHub Learning Journey Generator - 实施任务列表

## 项目阶段一：基础设施搭建

- [ ] 1. 创建项目目录结构
  - backend/app/{agents,api,core,models,schemas,services,utils}
  - frontend/src/{components,pages,hooks,utils,assets}
  - storage/{tasks,cache}

- [ ] 2. 后端核心配置
  - [ ] 2.1 创建 requirements.txt 包含所有Python依赖
  - [ ] 2.2 创建 FastAPI 应用入口和配置
  - [ ] 2.3 配置日志系统和环境变量管理

- [ ] 3. 数据库设置
  - [ ] 3.1 实现SQLite数据库连接和初始化
  - [ ] 3.2 创建Tasks表、TaskResults表、AgentLogs表的模型定义

- [ ] 4. 验证点 - 确保数据库连接正常，应用能启动

## 项目阶段二：智能体框架核心

- [ ] 5. 智能体基类实现
  - [ ] 5.1 创建Agent基类，定义execute、validate_input、parse_output接口
  - [ ] 5.2 实现AgentRegistry实现智能体注册和发现
  - [ ] 5.3 创建PromptManager实现提示词模板管理

- [ ] 6. LLM客户端实现
  - [ ] 6.1 创建LLMClient基类封装OpenAI API调用
  - [ ] 6.2 实现重试机制和错误处理
  - [ ] 6.3 实现响应JSON解析和验证

- [ ] 7. 验证点 - Agent框架基本功能可用

## 项目阶段三：任务管理系统

- [ ] 8. 任务管理核心
  - [ ] 8.1 实现TaskRepository处理任务的CRUD操作
  - [ ] 8.2 实现TaskManager处理任务状态转换
  - [ ] 8.3 实现ProgressTracker追踪任务进度

- [ ] 9. 任务队列集成
  - [ ] 9.1 配置Celery和Redis
  - [ ] 9.2 创建异步任务函数execute_agent_task
  - [ ] 9.3 实现任务取消和超时处理

- [ ] 10. 验证点 - 任务能够正常创建、执行、查询

## 项目阶段四：五大智能体实现

- [ ] 11. Code Analyst Agent
  - [ ] 11.1 实现GitHub API调用获取仓库信息
  - [ ] 11.2 实现仓库文件结构解析（深度5层）
  - [ ] 11.3 实现依赖配置文件解析
  - [ ] 11.4 输出标准化的仓库分析报告JSON

- [ ] 12. Curriculum Designer Agent
  - [ ] 12.1 实现知识图谱构建
  - [ ] 12.2 实现学习里程碑设计
  - [ ] 12.3 实现知识点到源代码的映射
  - [ ] 12.4 输出学习路径JSON

- [ ] 13. Technical Writer Agent
  - [ ] 13.1 实现Markdown教程生成
  - [ ] 13.2 实现代码示例提取和解释
  - [ ] 13.3 实现课程总览文档生成
  - [ ] 13.4 输出教程内容（Markdown + JSON）

- [ ] 14. Quiz Engineer Agent
  - [ ] 14.1 实现选择题生成
  - [ ] 14.2 实现实践题生成
  - [ ] 14.3 实现答案和评分标准生成
  - [ ] 14.4 输出练习题JSON

- [ ] 15. Frontend Developer Agent
  - [ ] 15.1 实现静态网站HTML/CSS/JS生成
  - [ ] 15.2 实现内容JSON数据打包
  - [ ] 15.3 输出完整的网站资源

- [ ] 16. 验证点 - 五大智能体均能独立执行并输出正确格式

## 项目阶段五：API层实现

- [ ] 17. API路由实现
  - [ ] 17.1 实现POST /api/v1/tasks 创建任务
  - [ ] 17.2 实现GET /api/v1/tasks/{id} 获取任务详情
  - [ ] 17.3 实现GET /api/v1/tasks 列出任务
  - [ ] 17.4 实现DELETE /api/v1/tasks/{id} 取消任务
  - [ ] 17.5 实现GET /api/v1/tasks/{id}/download 下载网站包

- [ ] 18. 中间件和错误处理
  - [ ] 18.1 实现认证中间件
  - [ ] 18.2 实现全局异常处理器
  - [ ] 18.3 实现请求验证（Pydantic）

- [ ] 19. 验证点 - API端点测试通过

## 项目阶段六：前端开发

- [ ] 20. React项目初始化
  - [ ] 20.1 创建React项目（Vite + TypeScript）
  - [ ] 20.2 配置TailwindCSS和Radix UI
  - [ ] 20.3 配置React Router

- [ ] 21. 核心组件开发
  - [ ] 21.1 实现CourseOutline课程大纲组件
  - [ ] 21.2 实现TutorialViewer教程内容渲染组件
  - [ ] 21.3 实现CodeBlock代码展示块组件
  - [ ] 21.4 实现QuizCard练习题卡片组件
  - [ ] 21.5 实现ProgressBar进度条组件
  - [ ] 21.6 实现MilestoneCard里程碑卡片组件

- [ ] 22. 页面开发
  - [ ] 22.1 实现Home首页
  - [ ] 22.2 实现Course课程页面
  - [ ] 22.3 实现Tutorial教程详情页面
  - [ ] 22.4 实现Exercise练习页面
  - [ ] 22.5 实现Progress学习进度页面

- [ ] 23. 功能实现
  - [ ] 23.1 实现Markdown渲染（react-markdown + prismjs）
  - [ ] 23.2 实现代码复制功能
  - [ ] 23.3 实现练习题提交和评分
  - [ ] 23.4 实现学习进度持久化（localStorage）

- [ ] 24. 验证点 - 前端应用完整可用

## 项目阶段七：智能体编排和工作流

- [ ] 25. 工作流编排器
  - [ ] 25.1 实现工作流定义和配置
  - [ ] 25.2 实现基于依赖图的执行顺序控制
  - [ ] 25.3 实现工作流状态机

- [ ] 26. 端到端集成
  - [ ] 26.1 实现从GitHub URL到网站生成的完整流程
  - [ ] 26.2 实现中间结果存储和传递
  - [ ] 26.3 实现最终网站打包

- [ ] 27. 验证点 - 端到端流程测试通过

## 项目阶段八：部署和运维

- [ ] 28. Docker配置
  - [ ] 28.1 创建后端Dockerfile
  - [ ] 28.2 创建docker-compose.yml
  - [ ] 28.3 配置nginx反向代理

- [ ] 29. 环境配置
  - [ ] 29.1 创建.env.example示例配置
  - [ ] 29.2 配置生产环境变量
  - [ ] 29.3 配置日志输出

- [ ] 30. 验证点 - 应用能通过Docker正常部署

## 项目阶段九：测试

- [ ]* 31. 单元测试
  - [ ]* 31.1 为Agent基类编写单元测试
  - [ ]* 31.2 为TaskManager编写单元测试
  - [ ]* 31.3 为API路由编写单元测试

- [ ]* 32. 集成测试
  - [ ]* 32.1 实现API端到端测试
  - [ ]* 32.2 实现工作流集成测试

- [ ]* 33. E2E测试
  - [ ]* 33.1 实现完整任务流程E2E测试
  - [ ]* 33.2 实现网站功能E2E测试

## 检查点

- [ ] 所有核心功能测试通过
- [ ] API文档完整（OpenAPI/Swagger）
- [ ] 代码质量通过lint检查
