---
name: prototype-prompt-generator
description: Generate concise Figma Make prompts for B2B product page prototypes based on project documentation. Use when user needs to create high-fidelity prototypes from project_goal.md and low-fidelity wireframes.
---

# Prototype Prompt Generator

Generate concise Figma Make prompts for B2B product page prototypes.

## Core Principle

**简洁优先**：Prompt 应该直接、清晰、无冗余。只包含 Figma Make 需要的关键信息。

## Input

读取：
- `project_goal.md` - 需求来源
- `progress.md` - 当前设计任务
- 低保真原型（如有）- 结构参考

## Output Format

```markdown
🎯 设计范围说明（必须遵守）

* 本次设计范围：项目章程中"[需求章节标题]"
* 参考项目章程中的上下文
* 已有原型结构（如有）

设计"[功能模块/页面名称]"页面。

不要根据项目章程设计完整产品。
原型中的红字部分为标注说明（用于解释规则/状态/逻辑），不是页面真实展示内容。
从提供的低保真原型中参考页面结构。

🧩 设计目标

围绕用户角色 [角色名] 优化体验：
* [用户故事核心点1]
* [用户故事核心点2]
* [用户故事核心点3]

🎨 关键设计点

[关键交互/状态/规则，简洁描述]

- [设计点1]
- [设计点2]
- [设计点3]
```

## Rules

1. **不要展开完整产品**：只设计当前任务对应的页面/模块
2. **红字说明**：提醒原型中的红字是标注，不是真实内容
3. **用户故事简化**：提取核心目标，不复制完整用户故事
4. **结构简洁**：用列表而非长段落
5. **关键设计点**：只列最重要的交互、状态、规则

## Example

输入：
- 设计任务：工单详情页 - 流程日志
- 需求来源：项目章程"工单详情页优化"

输出：

```markdown
🎯 设计范围说明（必须遵守）

* 本次设计范围：项目章程中"## 【需求】工单详情页优化"
* 参考项目章程中的上下文
* 已有原型结构

设计"工单详情页 - 流程日志"模块。

不要根据项目章程设计完整产品。
原型中的红字部分为标注说明，不是页面真实展示内容。
从提供的低保真原型中参考页面结构。

🧩 设计目标

围绕用户角色 Tech Owner（TO）优化体验：
* 了解当前进度（到了哪个环节）
* 快速识别状态（进行中/已完成/跳过/报错）
* 减少信息干扰（只显示环节标题）

🎨 关键设计点

- 只显示环节标题，不显示技术细节
- 状态：进行中（高亮）、已完成（✓）、跳过（文字"跳过"）、报错（红色标记）
- 无中间件时，第一步显示"跳过"
- 步骤间用连线表示进度流向
```

## Workflow

1. 从 `progress.md` 读取当前设计任务
2. 从 `project_goal.md` 定位对应需求章节
3. 提取：用户角色 + 核心目标（3-4条）
4. 提取：关键设计点（交互/状态/规则）
5. 按输出格式生成中文 Prompt
6. 只输出 Prompt，不附加解释
