# 团队 AI 使用指南

## 一、Knowhow 补齐清单

### 1. Agent / Skill 概念
- **Agent**: AI 代理，能自主完成任务的智能体
- **Skill**: 封装好的能力模块，可被 Agent 调用
- 类比：Agent = 人，Skill = 工具/技能

### 2. Claude Code 常用指令
```bash
# 启动
claude

# 常用命令
/help          # 查看帮助
/skill         # 管理 skill
/terminal      # 终端模式
/compact       # 压缩上下文
```

### 3. Skill 开发流程
```bash
# 1. 创建 skill 目录
mkdir skills/xxx助手

# 2. 编写 SKILL.md
# 3. 测试验证
# 4. 提交到团队仓库
```

## 二、工具配置

### API Key 配置
在 Claude Code 中设置：
```bash
claude config set api_key sk-xxxx
```

### VPN 代理配置
```bash
export HTTPS_PROXY=http://your-proxy:port
```

## 三、Skill 使用示例

### 标定助手
```bash
/skill load ./skills/calibration-assistant
# 然后输入标定数据，获取分析报告
```

### 代码审查
```bash
/skill load ./skills/code-review
# 上传代码文件，获取审查意见
```

## 四、团队规范

1. **Skill 命名**: 模块+功能，如 `calibration-assistant`
2. **文档要求**: 每个 skill 必须包含 README.md
3. **测试要求**: 提交前需通过至少 3 个测试用例
4. **更新流程**: 修改 → 测试 → PR → 合并

---

> 有问题联系 Vincent
