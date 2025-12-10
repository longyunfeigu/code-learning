"""
问题生成 Prompt 模版
"""

QUESTION_GENERATE_PROMPT = """基于以下项目信息，生成学习问题。

## 项目画像
- 项目类型: {archetype}
- 主要语言: {language}
- 框架: {framework}
- 项目描述: {description}

## 代码地图摘要
{repo_map_summary}

## 学习阶段
{learning_stage}

## 已回答的问题
{answered_questions}

## 要求
请生成 3-5 个适合当前学习阶段的问题，每个问题包含：
1. title: 问题标题（简洁明了）
2. description: 详细描述（引导用户思考的方向）
3. recommended_files: 推荐查看的文件列表
4. difficulty: 难度等级 (easy/medium/hard)
5. prerequisites: 前置问题ID（如有）

问题应该：
- 从宏观到微观，循序渐进
- 引导用户主动探索代码
- 关注设计意图而非实现细节
- 与项目的核心功能和特色相关

请以 JSON 格式返回问题列表。"""

