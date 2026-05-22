# 自动驾驶团队 AI 应用提效建设

> 团队级 AI 工具链与知识资产库

## 📁 目录结构

```
team-ai-repo/
├── skills/          # 可复用的 AI skill（按模块划分）
├── prompts/         # 常用 prompt 模板
├── tools/           # 脚本与自动化工具
├── docs/            # 团队文档与使用指南
└── resources/       # 资源清单（API keys、账号、配置）
```

## 🚀 快速开始

1. **安装 Claude Code**
   ```bash
   npm install -g @anthropic-ai/claude-code
   ```

2. **配置 API Key**
   - 在 `resources/` 目录下查看团队 API key 配置方式
   - 或使用个人 key

3. **使用 Skill**
   ```bash
   # 在 Claude Code 中加载团队 skill
   /skill load ./skills/标定助手
   ```

## 📋 当前已上线 Skill

| Skill | 模块 | 状态 |
|-------|------|------|
| 标定助手 | 标定 | 🚧 开发中 |
| 部署检查 | 部署运维 | 🚧 开发中 |
| 代码审查 | 通用 | 🚧 开发中 |
| 技术方案生成 | 文档 | 🚧 开发中 |

## 🎯 AI 应用领域

- [ ] AI 代码生成、代码审查
- [ ] 技术方案编写
- [ ] 算法研究辅助
- [ ] 汇报材料编写
- [ ] 部署、调试自动化工作流

---

> 维护者：Vincent
> 最后更新：2026-05-22
