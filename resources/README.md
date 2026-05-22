# 团队资源配置指南

## API Key 配置

### Claude Code
```bash
claude config set api_key sk-xxxx
```

### OpenAI / Kimi / 其他
配置在 `~/.openclaw/secrets/` 或环境变量中：
```bash
export OPENAI_API_KEY=sk-xxx
export KIMI_API_KEY=sk-xxx
```

## VPN 代理配置

### 终端代理
```bash
export HTTPS_PROXY=http://proxy.example.com:port
export HTTP_PROXY=http://proxy.example.com:port
```

### Claude Code 代理
```bash
claude config set http_proxy http://proxy.example.com:port
```

## 账号清单

| 服务 | 用途 | 状态 |
|------|------|------|
| Google | ChatGPT 登录 | ✅ |
| GitHub | 代码仓库 | ✅ |
| Notion | 知识库 | ✅ |

## 团队共享资源

- **模型选择**: Claude 3.7 Sonnet（代码能力强）
- **Skill 仓库**: 本仓库 `skills/` 目录
- **Prompt 库**: `prompts/` 目录
- **文档中心**: `docs/` 目录

---

> ⚠️ 注意：API key 和敏感信息不要提交到 Git！
> 使用环境变量或本地配置文件管理。
