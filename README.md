# AI Rules API

一个轻量级的云端规则服务，为 AI Agent（如 Claude）提供动态规则加载能力。

## ✨ 核心特性

- **动态加载**：根据项目目录自动加载对应规则
- **版本管理**：规则文件自带版本号，便于追踪变更
- **零运维**：基于 Modal 部署，自动 HTTPS，无需服务器管理
- **免费额度**：Modal 提供 $30/月免费额度，个人使用成本 ≈ $0
- **多规则支持**：一个 API 服务托管多种规则类型

## 📦 项目结构

```
modal-rules-api/
├── app.py              # Modal 应用主文件
├── requirements.txt    # Python 依赖
├── rules/              # 规则文件目录（可持久化）
│   ├── dev-service.md  # 服务端开发规范
│   ├── dev-repo.md     # 仓库管理规范
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

### 3. 创建规则卷（持久化存储）

```bash
modal volume create ai-rules
```

### 4. 上传规则文件

```bash
# 上传所有规则文件到 Modal 卷
modal put ai-rules:./rules/ rules/*.md
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
- App: ai-rules-api
- Function: web
- Snapshot: fs-snapshot-xxx
- Workspace: your-username--ai-rules-api

✓ App deployed! URL: https://your-username--ai-rules-api.modal.run
```

### 6. 验证部署

```bash
# 健康检查
curl https://your-username--ai-rules-api.modal.run/health

# 列出所有规则
curl https://your-username--ai-rules-api.modal.run/rules

# 获取特定规则
curl https://your-username--ai-rules-api.modal.run/rules/dev-service
```

## 📋 可用 API 端点

| 端点 | 方法 | 描述 |
|------|------|------|
| `/` | GET | API 信息和使用说明 |
| `/health` | GET | 健康检查（附带规则数量） |
| `/rules` | GET | 列出所有可用规则 |
| `/rules/{type}` | GET | 获取指定规则全文（纯文本） |
| `/rules/{type}/version` | GET | 获取规则版本信息（JSON） |

## 🔧 在 CLAUDE.md 中使用

### 基础集成

在你的项目根目录的 `CLAUDE.md` 中添加：

```markdown
## 项目特定规则

当你进入包含 `.ai/` 目录的项目时，请执行：

1. 检查 `.ai/*.md` 文件是否存在
2. 读取文件中的 URL（每行一个）
3. 对每个 URL 发起 HTTP GET 请求
4. 将获取的规则作为当前会话的约束条件

示例 `.ai/Development_Service.md` 内容：
```
https://your-username--ai-rules-api.modal.run/rules/dev-service
https://your-username--ai-rules-api.modal.run/rules/dev-repo
```
```

### Task Mode 前缀（推荐）

结合 Task Mode 使用：

```markdown
## Task Mode 前缀

- `feature.` - 新功能开发（遵循 dev-service 规则）
- `refactor.` - 代码重构（遵循 dev-repo 规范）
- `debug.` - 问题调试（遵循 dev-service 规范）
```

使用示例：
```
refactor. 重构用户认证模块，遵循 dev-service 规范
```

## 📝 添加新规则

### 1. 创建规则文件

在 `rules/` 目录创建新的 `.md` 文件，例如 `mobile-dev.md`：

```markdown
# Mobile Development Rules

version: 1.0.0
last_updated: 2024-01-15

## 技术栈
- React Native 0.72+
- TypeScript 5.0+
- ...

## 规范
...
```

### 2. 上传到 Modal

```bash
modal put ai-rules:./rules/ rules/mobile-dev.md
```

### 3. 重新部署（可选，热加载支持）

规则文件存储在独立 Volume，修改后自动生效，无需重新部署应用：

```bash
# 直接更新文件即可
modal put ai-rules:./rules/ rules/mobile-dev.md
```

## 🔄 自动化更新（GitHub Actions）

创建 `.github/workflows/deploy-rules.yml`：

```yaml
name: Deploy AI Rules

on:
  push:
    branches: [main]
    paths: ['rules/**']

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Install Modal
        run: pip install modal
      - name: Set Modal token
        run: modal token set --token ${{ secrets.MODAL_TOKEN }}
      - name: Update rules volume
        run: modal put ai-rules:./rules/ rules/*.md
      - name: Deploy app (if app.py changed)
        if: contains(github.event.head_commit.message, 'deploy')
        run: modal deploy app.py
```

## 🛠️ 本地开发

### 运行本地测试服务器

```bash
# 安装依赖
pip install -r requirements.txt

# 运行本地服务器
modal run app.py::main
```

访问 `http://localhost:8000` 测试 API。

### 本地测试规则

```bash
# 创建本地规则目录
mkdir -p local-rules
cp rules/*.md local-rules/

# 修改 app.py 中的路径为本地路径进行测试
# 将 /rules 改为 ./local-rules
```

## 🔐 安全性

### API 访问控制（可选）

如果需要限制访问，可以在 `app.py` 中添加 API Key 验证：

```python
from fastapi import Request, HTTPException, Depends

API_KEY = os.environ.get("API_KEY")

def verify_api_key(request: Request):
    key = request.headers.get("X-API-Key")
    if not key or key != API_KEY:
        raise HTTPException(status_code=401, detail="Invalid API Key")
    return True

@app.get("/rules/{rule_type}")
async def get_rule(rule_type: str, authorized: bool = Depends(verify_api_key)):
    # ...
```

设置环境变量：
```bash
modal secret create ai-rules-api-api-key API_KEY=your-secret-key
```

然后在 `app.py` 中声明 secret：
```python
@app.function(
    image=image,
    volumes={"/rules": rules_volume},
    secrets=[modal.Secret.from_name("ai-rules-api-api-key")],
    keep_warm=1,
)
```

### 规则文件安全
- 规则文件仅包含规范文档，不包含敏感信息
- 建议定期审计规则文件内容
- 避免在规则中泄露内部系统信息

## 📊 成本估算

Modal 定价（2024）：
- **免费额度**：$30/月
- **热实例（1 个）**：≈ $50/月
- **存储（10MB）**：≈ $0.01/月

**个人使用**：在免费额度范围内，实际成本 ≈ $0

## 🐛 故障排除

### 问题：访问 API 返回 404

**可能原因**：
- 应用未部署成功
- URL 拼写错误
- 规则文件未上传

**解决**：
```bash
# 检查应用状态
modal app list

# 重新部署
modal deploy app.py

# 检查规则卷内容
modal volume ls ai-rules
```

### 问题：本地运行报错 `No module named 'fastapi'`

**解决**：
```bash
pip install -r requirements.txt
```

### 问题：规则更新后 API 未生效

Modal Volume 是持久化的，但可能需要几秒同步。尝试：
```bash
# 强制重新部署
modal deploy --force app.py
```

## 🎯 高级功能

### 1. 规则预览模式

在 CLAUDE.md 中实现预览：

```markdown
当你获取远程规则后，先总结核心要点（不超过 5 条），
然后询问用户是否确认应用该规则，再执行。
```

### 2. 规则版本检查

```markdown
获取规则后，检查 version 字段：
- 如果版本高于当前缓存版本，提示用户规则已更新
- 询问是否重新加载
```

### 3. 多环境支持

在规则 URL 中添加环境参数：

```
https://app.modal.run/rules/dev-service?env=staging
```

在 `app.py` 中根据 `env` 返回不同内容。

## 📚 相关资源

- [Modal 官方文档](https://modal.com/docs)
- [FastAPI 文档](https://fastapi.tiangolo.com/)
- [Conventional Commits](https://www.conventionalcommits.org/)
- [GitFlow 工作流](https://nvie.com/posts/a-successful-git-branching-model/)

## 🤝 贡献

欢迎提交 Issue 和 PR 改进规则模板或 API 功能。

## 📄 许可证

MIT License - 可自由使用和修改。

---

**现在就开始部署吧！** 🚀

```bash
git clone <your-repo>
cd modal-rules-api
pip install modal
modal token new
modal volume create ai-rules
modal put ai-rules:./rules/ rules/*.md
modal deploy app.py
```