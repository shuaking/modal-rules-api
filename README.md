# AI Skills API

一个轻量级的云端技能服务，为 AI Agent（如 Claude, Obsidian AI 插件）提供动态 Skill 加载能力。

## ✨ 核心特性

- **动态加载**：根据项目目录或需求自动加载对应 Skill
- **版本管理**：Skill 文件自带版本号，便于追踪变更
- **零运维**：基于 Modal 部署，自动 HTTPS，无需服务器管理
- **免费额度**：Modal 提供 $30/月免费额度，个人使用成本 ≈ $0
- **多 Skill 支持**：一个 API 服务托管多种 Skill 类型

## 📦 项目结构

```
modal-rules-api/
├── app.py              # Modal 应用主文件 (API 服务)
├── requirements.txt    # Python 依赖
├── skills/             # Skill 文件目录（可持久化）
│   ├── dev-service.md  # 示例：服务端开发技能
│   ├── dev-repo.md     # 示例：仓库管理技能
│   └── README.md
└── README.md
```

## 🚀 快速部署（5 分钟）

### 1. 前置条件

- 安装 Python 3.9+
- 注册 [Modal](https://modal.com) 账号（免费）
- 安装 Modal CLI：
  ```bash
  pip install modal
  ```

### 2. 登录 Modal

```bash
modal token new
```
浏览器会打开，登录后授权 CLI。

### 3. 创建 Skill 卷（持久化存储）

```bash
modal volume create ai-skills
```

### 4. 上传 Skill 文件

```bash
# 上传所有 Skill 文件到 Modal 卷
modal volume put ai-skills skills/ /
```

### 5. 部署应用

```bash
# 进入项目目录
cd modal-rules-api

# 部署到 Modal
modal deploy app.py
```

输出类似：
```
✓ Created objects:
- App: ai-skills-api
- Function: web
- URL: https://your-username--ai-skills-api-web.modal.run
```

### 6. 验证部署

```bash
# 健康检查
curl https://your-username--ai-skills-api-web.modal.run/health

# 列出所有 Skill
curl https://your-username--ai-skills-api-web.modal.run/skills

# 获取特定 Skill
curl https://your-username--ai-skills-api-web.modal.run/skills/dev-service
```

## 📋 可用 API 端点

| 端点 | 方法 | 描述 |
|------|------|------|
| `/` | GET | API 信息和使用说明 |
| `/health` | GET | 健康检查（附带 Skill 数量） |
| `/skills` | GET | 列出所有可用 Skill |
| `/skills/{name}` | GET | 获取指定 Skill 全文（纯文本） |
| `/skills/{name}/version` | GET | 获取 Skill 版本信息（JSON） |

## 🔧 在 Obsidian 中使用

### 方式一：使用 Templater 插件

创建模板文件 `Insert-AI-Skill.md`：

```javascript
<%*
// 替换为你的 API 地址
const url = "https://your-username--ai-skills-api-web.modal.run/skills/dev-service";
try {
    const response = await fetch(url);
    if (!response.ok) throw new Error("Network response was not ok");
    const text = await response.text();
    tR += text;
} catch (error) {
    tR += "❌ 获取 Skill 失败: " + error.message;
}
%>
```

### 方式二：使用 Iframe

```html
<iframe 
    src="https://your-username--ai-skills-api-web.modal.run/skills/dev-service" 
    style="width: 100%; height: 600px; border: 1px solid #ccc;">
</iframe>
```

## 📝 添加新 Skill

### 1. 创建 Skill 文件

在 `skills/` 目录创建新的 `.md` 文件，例如 `python-expert.md`：

```markdown
# Python Expert Skill

version: 1.0.0
last_updated: 2024-02-08

## 角色设定
你是一位 Python 专家，擅长编写高性能、Pythonic 的代码。

## 指导原则
1. 优先使用列表推导式
2. 总是添加 Type Hints
...
```

### 2. 上传到 Modal

```bash
modal volume put -f ai-skills skills/python-expert.md /python-expert.md
```

或者使用自动脚本：
```bash
python upload_skills.py
```

## 🔄 自动化更新 (GitHub Actions)

项目已内置 `.github/workflows/update-skills.yml`：

```yaml
name: Update AI Skills
on:
  push:
    branches: [main]
    paths: ['skills/**', 'app.py']

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Install Modal
        run: pip install modal
      - name: Set Modal token
        run: modal token set --token-id ${{ secrets.MODAL_TOKEN_ID }} --token-secret ${{ secrets.MODAL_TOKEN_SECRET }}
      - name: Update Skills Volume
        run: modal volume put -f ai-skills skills/ /
      - name: Deploy app
        run: modal deploy app.py
```

### 配置 Secrets
在 GitHub 仓库设置中添加：
1. `MODAL_TOKEN_ID`
2. `MODAL_TOKEN_SECRET`
