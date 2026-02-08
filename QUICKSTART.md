# 🚀 快速开始指南

## 5 分钟完成部署

### 步骤 1：安装依赖（1 分钟）

```bash
pip install modal
```

### 步骤 2：登录 Modal（1 分钟）

```bash
modal token new
```
浏览器打开 → 登录 Modal 账号 → 授权。

### 步骤 3：创建存储卷（30 秒）

```bash
modal volume create ai-rules
```

### 步骤 4：上传规则（1 分钟）

```bash
modal put ai-rules:./rules/ rules/*.md
```

### 步骤 5：部署应用（1 分钟）

```bash
modal deploy app.py
```

### 步骤 6：测试 API（30 秒）

```bash
# 替换 your-username 为实际用户名
curl https://your-username--ai-rules-api.modal.run/health

# 示例输出
# {"status":"healthy","timestamp":"2024-01-15T...","rules_count":2}
```

## ✅ 完成！

你的 AI Rules API 已上线，URL 类似：
```
https://your-username--ai-rules-api.modal.run
```

## 🔗 在 CLAUDE.md 中使用

在你的项目中创建 `.ai/Development_Service.md`：

```markdown
# 项目规则

请从以下 URL 获取开发规范并严格遵守：

https://your-username--ai-rules-api.modal.run/rules/dev-service
```

然后在 CLAUDE.md 中添加检测逻辑：

```markdown
## 项目规则加载

当你看到项目目录中有 `.ai/*.md` 文件时：
1. 读取文件中的每个 URL
2. 通过 HTTP GET 获取规则内容
3. 将该规则作为当前会话的约束条件
```

## 🎯 测试效果

现在和 AI 对话时，它会自动加载你的规范：

```
你：refactor. 重构用户服务模块
AI：已加载 dev-service 规则，将遵守以下规范：
    1. 使用 TypeScript 5.0+
    2. 分层架构（controllers/services/repositories）
    3. 所有函数必须有完整类型定义
    4. 错误处理使用 ServiceError 类
    ...
```

## 📝 下一步

- [ ] 自定义 `rules/dev-service.md` 为你的项目规范
- [ ] 上传更多规则文件（如 `mobile-dev.md`, `data-eng.md`）
- [ ] 在 CLAUDE.md 中实现 Task Mode 前缀
- [ ] 设置 GitHub Actions 自动更新规则

## ❓ 遇到问题？

查看 `README.md` 的故障排除部分，或运行：

```bash
# 查看应用状态
modal app list

# 查看日志
modal logs your-username--ai-rules-api

# 重新部署
modal deploy --force app.py
```

祝你使用愉快！🎉