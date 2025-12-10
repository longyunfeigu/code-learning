# TASK-004: Git 服务与代码分析基础

## 基本信息

| 属性 | 值 |
|------|-----|
| **任务编号** | TASK-004 |
| **任务名称** | Git 服务与代码分析基础 |
| **版本** | V0.2 |
| **状态** | 🔵 规划中 |
| **优先级** | P0 - 最高 |
| **预计工时** | 3-4 天 |
| **前置任务** | TASK-001 |

---

## 任务描述

实现 Git 仓库克隆、文件访问等基础服务，以及基于 tree-sitter 的代码 AST 解析能力。这是代码分析和索引的基础。

### 主要工作内容

1. **Git 服务 (`infrastructure/code_analysis/git_service.py`)**
   - 仓库克隆：支持 HTTPS/SSH 协议
   - 浅克隆：`--depth 1` 减少下载量
   - 分支切换：支持指定分支/tag/commit
   - 仓库更新：pull 最新代码
   - 文件读取：读取指定路径文件内容
   - 目录遍历：列出仓库文件结构
   - 存储管理：克隆到 MinIO 或本地目录

2. **Tree-sitter 解析器 (`infrastructure/code_analysis/tree_sitter_parser.py`)**
   - 多语言支持：Python, TypeScript/JavaScript, Java, Go, Rust
   - AST 解析：解析源文件生成语法树
   - 符号提取：提取类、函数、方法、变量定义
   - 位置信息：记录每个符号的行号范围
   - 注释提取：提取文档字符串和注释

3. **符号模型定义**
   - Symbol 数据类：name, kind, file, start_line, end_line, body
   - SymbolKind 枚举：CLASS, FUNCTION, METHOD, VARIABLE, IMPORT
   - FileSymbols：单文件的符号列表
   - ProjectSymbols：整个项目的符号索引

4. **符号搜索 (`infrastructure/code_analysis/symbol_search.py`)**
   - 按名称搜索：模糊匹配、精确匹配
   - 按类型过滤：只搜索类/函数/方法
   - 按文件路径过滤
   - 返回符号定义和源码

5. **Celery 异步任务**
   - 仓库克隆任务：大仓库异步处理
   - 进度回调：报告克隆进度
   - 超时处理：克隆超时自动取消

---

## 验收标准

- [ ] 支持克隆公开 GitHub 仓库
- [ ] 支持克隆私有仓库（通过 token 认证）
- [ ] 浅克隆大仓库（>100MB）耗时 < 60s
- [ ] Tree-sitter 支持至少 Python、TypeScript、JavaScript
- [ ] 能正确提取 Python 类和函数定义
- [ ] 能正确提取 TypeScript 类、函数、接口定义
- [ ] 符号搜索支持模糊匹配
- [ ] 仓库文件存储路径可配置
- [ ] 提供仓库大小限制配置（默认 500MB）
- [ ] 克隆失败时返回明确错误信息

---

## 注意事项

1. **安全性**
   - 验证仓库 URL 格式，防止路径遍历攻击
   - 限制克隆仓库大小，防止资源耗尽
   - 私有仓库 token 不记录到日志

2. **Tree-sitter 语言支持**
   - 需要安装对应语言的 tree-sitter 绑定
   - Python: `tree-sitter-python`
   - TypeScript: `tree-sitter-typescript`
   - 动态加载语言解析器

3. **性能优化**
   - 使用浅克隆减少下载时间
   - AST 解析结果缓存
   - 大文件跳过解析（>1MB）

4. **存储策略**
   - 开发环境：本地 `/tmp/repos/` 目录
   - 生产环境：MinIO 对象存储
   - 定期清理过期仓库

5. **错误处理**
   - 仓库不存在：REPO_NOT_FOUND
   - 无权限访问：REPO_ACCESS_DENIED
   - 克隆超时：REPO_CLONE_TIMEOUT
   - 仓库过大：REPO_TOO_LARGE

---

## 相关文档

- [架构设计文档 - 5.2 代码索引数据流](../docs/code-learning-coach-architecture.md#52-代码索引数据流)
- [Tree-sitter 文档](https://tree-sitter.github.io/tree-sitter/)

