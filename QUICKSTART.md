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
modal volume create ai-skills
```

### 步骤 4：上传 Skill（1 分钟）

```bash
modal volume put ai-skills skills/ /
```

### 步骤 5：部署应用（1 分钟）

```bash
modal deploy app.py
```

### 步骤 6：测试 API（30 秒）

```bash
# 替换 your-username 为实际用户名
curl https://your-username--ai-skills-api-web.modal.run/health
```

## ✅ 完成！

你的 AI Skills API 已上线，URL 类似：
```
https://your-username--ai-skills-api-web.modal.run
```

## 🔗 在 Obsidian 中使用

使用 Templater 插件快速插入 Skill：

```javascript
<%*
const url = "https://your-username--ai-skills-api-web.modal.run/skills/dev-service";
const response = await fetch(url);
const text = await response.text();
tR += text;
%>
```

## 🔗 在 CLAUDE.md 中使用

```markdown
# 引用远程 Skill
- Dev Skill: https://your-username--ai-skills-api-web.modal.run/skills/dev-service
```

## ❓ 遇到问题？

查看 `README.md` 的故障排除部分，或运行：

```bash
# 查看应用状态
modal app list

# 查看日志
modal logs your-username--ai-skills-api-web
```
