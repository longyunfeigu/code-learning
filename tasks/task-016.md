# TASK-016: CLI 命令行工具

## 基本信息

| 属性 | 值 |
|------|-----|
| **任务编号** | TASK-016 |
| **任务名称** | CLI 命令行工具 |
| **版本** | V0.6 |
| **状态** | 🔵 规划中 |
| **优先级** | P2 - 中 |
| **预计工时** | 2-3 天 |
| **前置任务** | TASK-012 |

---

## 任务描述

开发命令行工具，支持开发者在终端中进行项目分析、学习会话等操作。使用 Typer 框架实现，提供友好的命令行交互体验。

### 主要工作内容

1. **CLI 框架 (`cli/main.py`)**
   - 使用 Typer 框架
   - 支持子命令
   - 彩色输出
   - 进度条显示

2. **命令设计**
   
   **项目管理：**
   ```bash
   # 分析项目
   coach analyze https://github.com/org/repo --goals architecture,agent
   
   # 查看项目列表
   coach projects list
   
   # 查看项目状态
   coach projects status <project_id>
   
   # 删除项目
   coach projects delete <project_id>
   ```
   
   **学习会话：**
   ```bash
   # 开始学习
   coach learn <project_id> --mode macro
   
   # 交互式问答
   coach chat <session_id>
   
   # 查看进度
   coach progress <session_id>
   ```
   
   **分析文档：**
   ```bash
   # 查看分析
   coach analysis <project_id>
   
   # 导出文档
   coach export <project_id> --format markdown --output ./analysis.md
   ```
   
   **配置：**
   ```bash
   # 配置 API 地址
   coach config set api_url http://localhost:8000
   
   # 查看配置
   coach config list
   ```

3. **交互式模式 (`cli/interactive.py`)**
   - 类似 `ipython` 的交互式 shell
   - 支持历史记录
   - 支持自动补全
   - 支持多行输入

4. **输出格式化**
   - 表格输出：项目列表、问题列表
   - Markdown 渲染：分析文档
   - 进度条：分析进度
   - 彩色状态标识

5. **配置管理 (`~/.coach/config.yaml`)**
   - API 服务地址
   - 默认输出格式
   - 主题设置

---

## 验收标准

- [ ] 所有命令有 `--help` 帮助信息
- [ ] 命令支持 `-v/--verbose` 详细输出
- [ ] 错误信息友好，包含解决建议
- [ ] 进度条显示分析进度
- [ ] 交互式模式支持历史记录
- [ ] 配置文件正确保存和读取
- [ ] 支持 `--output` 指定输出文件
- [ ] 支持 `--format` 指定输出格式 (json/table/markdown)
- [ ] Tab 补全功能正常
- [ ] pip 安装后命令可用

---

## 注意事项

1. **Typer 命令定义**
   ```python
   import typer
   from rich.console import Console
   from rich.progress import Progress
   
   app = typer.Typer(help="开源项目学习教练 CLI")
   console = Console()
   
   @app.command()
   def analyze(
       repo_url: str = typer.Argument(..., help="仓库 URL"),
       goals: str = typer.Option("architecture", help="学习目标"),
   ):
       """分析开源项目"""
       with Progress() as progress:
           task = progress.add_task("分析中...", total=100)
           # 调用 API
           ...
           progress.update(task, advance=50)
   ```

2. **交互式问答**
   ```python
   from prompt_toolkit import prompt
   from prompt_toolkit.history import FileHistory
   
   def chat_loop(session_id: str):
       history = FileHistory("~/.coach/history")
       while True:
           input_text = prompt(">> ", history=history)
           if input_text.strip() == "/exit":
               break
           response = send_message(session_id, input_text)
           console.print(f"教练: {response}")
   ```

3. **输出格式化**
   ```python
   from rich.table import Table
   from rich.markdown import Markdown
   
   def show_projects(projects: list):
       table = Table(title="项目列表")
       table.add_column("ID")
       table.add_column("名称")
       table.add_column("状态")
       for p in projects:
           table.add_row(p["id"], p["name"], p["status"])
       console.print(table)
   ```

4. **安装方式**
   ```toml
   # pyproject.toml
   [project.scripts]
   coach = "cli.main:app"
   ```

---

## 相关文档

- [架构设计文档 - 1.5 架构全景图](../docs/code-learning-coach-architecture.md#15-架构全景图)
- [Typer 文档](https://typer.tiangolo.com/)
- [Rich 文档](https://rich.readthedocs.io/)
