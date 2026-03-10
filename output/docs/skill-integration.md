# Portfolio Manager 集成指南

> **维护者**: Portfolio 项目  
> **目标读者**: 项目管理 Skill 维护者  
> **最后更新**: 2026-03-10

---

## 概述

本文档定义 Portfolio Manager 与项目管理 Skill 之间的集成规范，确保项目进度数据能够被 Portfolio 正确消费。

**核心机制**: Schema 契约 + 双格式输出

---

## 集成背景

### 问题
Portfolio 需要聚合多个项目的进度信息，但各项目的 `progress.md` 格式不统一，导致解析困难。

### 解决方案
采用"事前预防"策略：
1. 定义统一的 schema 规范
2. 项目管理 Skill 同时输出 `progress.md`（人类可读）和 `progress.json`（机器可读）
3. Portfolio 直接解析结构化的 `progress.json`

---

## Schema 契约

### Schema 文件

**来源**: [Portfolio Manager output/schemas/progress-schema.v1.json](../output/schemas/progress-schema.v1.json)

**复制到**: 项目管理 Skill 的 `schemas/progress-schema.json`

**版本管理**: 
- 主版本变更（v1 → v2）需双方同步升级
- 次版本变更（v1.0 → v1.1）保持向后兼容

### 核心字段说明

| 字段 | 必填 | 说明 |
|------|------|------|
| `project_id` | ✅ | 项目唯一标识，建议用 kebab-case |
| `project_name` | ✅ | 显示名称 |
| `current_phase` | ✅ | 当前阶段，如"需求澄清" |
| `progress_percentage` | ✅ | 0-100 整数 |
| `status` | ✅ | active/paused/blocked/completed |
| `tasks` | ✅ | 任务数组，每个任务必须有 id/name/status/assignee |
| `agents` | ✅ | 参与 Agent 列表 |
| `blockers` | ❌ | 阻塞项，没有时传空数组 |
| `updated_at` | ✅ | ISO 8601 格式时间戳 |
| `updated_by` | ❌ | 更新者标识 |

### 任务状态枚举

```yaml
- todo        # 待开始
- in_progress # 进行中
- review      # 等待 Review
- done        # 已完成
- blocked     # 阻塞
```

---

## 项目管理 Skill 修改清单

### 1. 文件结构变更

```
skills/project-management-product-design/
├── SKILL.md                          [修改] 增加输出格式规范章节
├── CHECKLIST.md                      [可选] 增加双格式检查点
├── schemas/
│   └── progress-schema.json          [新增] 从 Portfolio 复制
├── scripts/
│   ├── validate-and-save-progress.py [新增] 校验并双写脚本
│   └── ...                           [已有]
└── TEMPLATE/
    ├── progress.md                   [可选] 更新模板
    └── progress.json                 [新增] json 模板
```

### 2. SKILL.md 新增章节

在 SKILL.md 中增加以下内容：

```markdown
## 输出格式规范

### 双格式输出要求
本 Skill 同时维护两种格式的进度文件：
- `progress.md` - 人类可读（展示用）
- `progress.json` - 机器可读（Portfolio 消费用）

两个文件必须位于同一目录，文件名相同仅扩展名不同。

### Schema 契约
`progress.json` 遵循 Portfolio Manager 定义的 schema：
- Schema 路径: `{baseDir}/output/schemas/progress-schema.json`
- 规范来源: [Portfolio Manager](https://github.com/xxx/portfolio-manager)
- 当前版本: v1.0

### 写入流程（强制）

更新进度时必须执行以下步骤：

1. **构建数据对象**
   按 schema 构建完整的 JSON 数据对象

2. **Schema 校验**
   调用校验脚本验证数据格式
   ```bash
   python3 {baseDir}/scripts/validate-and-save-progress.py \
     --validate-only \
     --data "<json-string>"
   ```

3. **双写文件**（仅校验通过时）
   同时写入 progress.md 和 progress.json
   ```bash
   python3 {baseDir}/scripts/validate-and-save-progress.py \
     --data "<json-string>" \
     --md-path "./progress.md" \
     --json-path "./progress.json"
   ```

4. **失败处理**
   - 校验失败: 向用户展示错误信息，不写入文件
   - 写入失败: 回滚，保持原文件不变

### 校验脚本说明

`validate-and-save-progress.py` 参数：

| 参数 | 说明 |
|------|------|
| `--data` | JSON 字符串（必须） |
| `--md-path` | progress.md 输出路径 |
| `--json-path` | progress.json 输出路径 |
| `--validate-only` | 仅校验，不写入 |
| `--schema-path` | schema 文件路径（默认使用内置） |

### 数据构建示例

```python
progress_data = {
    "project_id": "my-project",
    "project_name": "我的项目",
    "current_phase": "开发实现",
    "progress_percentage": 60,
    "status": "active",
    "tasks": [
        {
            "id": "T1",
            "name": "设计数据模型",
            "status": "done",
            "assignee": "pd",
            "priority": "high"
        }
    ],
    "agents": [
        {"id": "pd", "role": "负责"},
        {"id": "dev", "role": "协助"}
    ],
    "blockers": [],
    "updated_at": "2026-03-10T14:00:00Z",
    "updated_by": "clawd"
}
```
```

### 3. 新增脚本: validate-and-save-progress.py

**功能需求**:

1. **加载 Schema**
   - 从 `--schema-path` 或默认路径加载 JSON schema
   - 缓存 schema 避免重复加载

2. **校验数据**
   - 使用 jsonschema 库验证数据格式
   - 收集所有校验错误（不只是第一个）
   - 返回详细的错误信息

3. **生成 Markdown**
   - 将 JSON 数据转换为 progress.md 格式
   - 保持与原有模板一致的可读性
   - 支持自定义 markdown 模板

4. **双写文件**
   - 原子性写入（先写临时文件，再重命名）
   - 确保两个文件同时成功或同时失败
   - 保留备份（可选）

5. **错误处理**
   - 校验错误：返回非零退出码 + 错误信息
   - IO 错误：清理临时文件，返回错误
   - 成功：返回 0

**伪代码**:

```python
#!/usr/bin/env python3
import json
import sys
import argparse
from jsonschema import validate, ValidationError

def main():
    args = parse_args()
    schema = load_schema(args.schema_path)
    data = json.loads(args.data)
    
    # 校验
    errors = validate_data(data, schema)
    if errors:
        print_errors(errors)
        sys.exit(1)
    
    if args.validate_only:
        print("✅ 校验通过")
        sys.exit(0)
    
    # 生成 markdown
    md_content = generate_markdown(data)
    
    # 双写
    try:
        atomic_write(args.json_path, json.dumps(data, indent=2))
        atomic_write(args.md_path, md_content)
        print("✅ 写入成功")
    except Exception as e:
        print(f"❌ 写入失败: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
```

### 4. 依赖管理

**requirements.txt 新增**:
```
jsonschema>=4.0.0
```

或者 Skill 提供自包含的校验脚本（不依赖外部库）。

### 5. 模板更新

**新增模板文件**: `TEMPLATE/progress.json`

```json
{
  "project_id": "{{project_id}}",
  "project_name": "{{project_name}}",
  "current_phase": "{{current_phase}}",
  "progress_percentage": {{progress_percentage}},
  "status": "{{status}}",
  "tasks": [],
  "agents": [],
  "blockers": [],
  "next_steps": [],
  "updated_at": "{{updated_at}}",
  "updated_by": "{{updated_by}}"
}
```

---

## 测试验证

### 集成测试步骤

1. **Schema 校验测试**
   ```bash
   # 在项目管理 Skill 目录
   python3 scripts/validate-and-save-progress.py \
     --validate-only \
     --data '{"project_id": "test", ...}'
   ```

2. **双写测试**
   ```bash
   # 创建测试项目
   mkdir -p /tmp/test-project
   
   # 执行双写
   python3 scripts/validate-and-save-progress.py \
     --data '<valid-json>' \
     --md-path /tmp/test-project/progress.md \
     --json-path /tmp/test-project/progress.json
   
   # 验证两个文件都存在且内容正确
   ```

3. **Portfolio 消费测试**
   ```bash
   # 在 Portfolio 目录
   portfolio-cli parse /tmp/test-project/progress.json
   # 应能正确解析，无错误
   ```

---

## 版本演进

### Schema 版本管理

| 版本 | 日期 | 变更说明 |
|------|------|----------|
| v1.0 | 2026-03-10 | 初始版本 |

### 升级流程

1. Portfolio 项目发布新 schema 版本
2. 通知项目管理 Skill 维护者
3. 项目管理 Skill 同步更新 schema 文件
4. 测试双方兼容性
5. 发布 Skill 更新

---

## 联系与支持

- **Schema 问题**: [Portfolio Manager Issues](https://github.com/xxx/portfolio-manager/issues)
- **Skill 实现问题**: 项目管理 Skill 维护者

---

*本文档随 Portfolio Manager 版本更新*
