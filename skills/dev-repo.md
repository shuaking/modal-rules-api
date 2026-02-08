# Development Repository Rules

version: 1.0.0
last_updated: 2024-01-15

## 📦 仓库管理规范

本文档定义代码仓库的组织、分支策略、提交规范和 CI/CD 要求。

## 🌿 Git 工作流

### 分支模型（GitFlow 简化版）
```
main          -> 生产环境代码（只允许通过 PR 合并）
develop       -> 开发集成分支（功能完成后合并至此）
feature/*     -> 功能分支（从 develop 创建）
hotfix/*      -> 紧急修复分支（从 main 创建）
release/*     -> 发布准备分支（从 develop 创建）
```

### 分支命名
- `feature/user-auth` - 新功能
- `bugfix/login-error` - 缺陷修复
- `hotfix/security-patch` - 紧急修复
- `refactor/service-layer` - 重构
- `docs/update-readme` - 文档更新

## 📝 提交规范（Conventional Commits）

### 格式
```
<type>(<scope>): <subject>

<body>

<footer>
```

### Type 枚举
- `feat`: 新功能
- `fix`: 缺陷修复
- `docs`: 文档变更
- `style`: 代码格式调整（不影响逻辑）
- `refactor`: 代码重构
- `perf`: 性能优化
- `test`: 测试相关
- `chore`: 构建/工具变更
- `ci`: CI 配置变更

### 示例
```bash
# ✅ 正确
feat(auth): add JWT refresh token support
fix(api): correct pagination calculation bug
docs(readme): add local setup instructions

# ❌ 禁止
fixed bug
updated code
```

### 自动化工具
- 使用 `commitlint` + `husky` 预检查
- 配置 IDE 插件（Conventional Commits）

## 🔀 Pull Request 流程

### PR 模板
```markdown
## 变更描述
[描述本次变更的内容和目的]

## 类型
- [ ] feat: 新功能
- [ ] fix: 缺陷修复
- [ ] refactor: 重构
- [ ] docs: 文档
- [ ] chore: 其他

## 变更影响
- [ ] 数据库迁移
- [ ] API 接口变更
- [ ] 配置文件变更
- [ ] 向后不兼容

## 测试验证
- [ ] 单元测试通过
- [ ] 集成测试通过
- [ ] 手动测试通过

## 检查清单
- [ ] 代码符合编码规范
- [ ] 添加/更新测试用例
- [ ] 更新相关文档
- [ ] 无敏感信息泄露
```

### PR 要求
- **描述清晰**：说明为什么改、怎么改、影响范围
- **小颗粒度**：单次 PR 只做一件事（< 500 行）
- **关联 Issue**：PR 描述中需包含 `Closes #123` 或 `Fixes #123`
- **代码评审**：至少 1 名团队成员 approval
- **CI 通过**：所有检查必须通过

## 🧪 代码质量门禁

### CI 检查项
1. **Lint**：ESLint 无错误（零容忍）
2. **Type Check**：TypeScript 编译无错误
3. **Test**：单元测试覆盖率 >= 80%
4. **Build**：项目成功构建
5. **Security**：依赖安全检查（npm audit, Snyk）

### 本地预检查
```bash
# 提交前自动执行
npm run lint
npm run type-check
npm test
```

## 📦 依赖管理

### package.json 原则
- 固定版本（不使用 ^ 或 ~）
- 定期更新依赖（每周检查）
- 删除未使用的依赖

```json
{
  "dependencies": {
    "express": "4.18.2",    // ✅ 固定版本
    "lodash": "4.17.21"
  },
  "devDependencies": {
    "typescript": "5.0.0",
    "jest": "29.5.0"
  }
}
```

### 安全扫描
- 每周运行 `npm audit`
- 使用 Dependabot 自动 PR 更新
- 高危漏洞必须 24 小时内修复

## 🏗️ 项目结构标准

```
my-service/
├── src/
│   ├── controllers/
│   ├── services/
│   ├── repositories/
│   ├── models/
│   ├── middleware/
│   ├── utils/
│   ├── config/
│   └── index.ts
├── tests/
│   ├── unit/
│   ├── integration/
│   └── fixtures/
├── .github/
│   └── workflows/
├── docker/
│   ├── Dockerfile
│   └── docker-compose.yml
├── docs/
│   ├── API.md
│   └── DEPLOYMENT.md
├── scripts/
│   ├── db-migrate.sh
│   └── backup.sh
├── .env.example
├── .gitignore
├── package.json
├── tsconfig.json
├── eslint.config.js
├── jest.config.js
├── README.md
└── CHANGELOG.md
```

## 🔄 CI/CD 流水线

### GitHub Actions 工作流
```yaml
name: CI

on:
  pull_request:
    branches: [main, develop]
  push:
    branches: [main]

jobs:
  lint:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-node@v3
      - run: npm ci
      - run: npm run lint

  test:
    needs: lint
    runs-on: ubuntu-latest
    services:
      postgres:
        image: postgres:15
        env:
          POSTGRES_PASSWORD: test
        options: >-
          --health-cmd pg_isready
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-node@v3
      - run: npm ci
      - run: npm test
      - run: npm run test:coverage

  build:
    needs: test
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-node@v3
      - run: npm ci
      - run: npm run build
      - uses: actions/upload-artifact@v3
        with:
          name: dist
          path: dist/
```

## 📊 监控与告警

### 必须指标
- 请求成功率（>= 99.9%）
- 响应时间 P95（< 500ms）
- 错误率（< 0.1%）
- 系统负载（CPU/Memory）

### 日志集中
- 所有日志输出到 stdout/stderr
- 使用结构化 JSON 格式
- 集中收集到日志平台（ELK/Datadog）

## 🗄️ 数据库迁移

### 迁移工具
- 使用 Prisma Migrate 或 Knex.js
- 迁移文件必须可逆（up/down）
- 迁移文件纳入版本控制

### 迁移流程
```bash
# 1. 创建迁移
npx prisma migrate dev --name add_user_table

# 2. 测试迁移
npx prisma migrate deploy

# 3. PR 中必须包含迁移文件
```

## 🔒 安全要求

### 密钥管理
- 使用环境变量或密钥管理服务（AWS Secrets Manager/HashiCorp Vault）
- 禁止在代码中硬编码密钥
- 定期轮换密钥（每 90 天）

### 依赖安全
- 每周执行 `npm audit`
- 使用 Snyk 或 Dependabot
- 高危漏洞立即修复

## 📈 性能基准

### API 性能目标
- P50 响应时间：< 100ms
- P95 响应时间：< 300ms
- P99 响应时间：< 500ms

### 数据库性能
- 慢查询阈值：> 1000ms
- 连接池大小：根据实例规格调整
- 索引覆盖率 > 90%

## 🚨 事故响应

### 严重等级
- **P0**: 服务完全不可用（立即响应，< 15min）
- **P1**: 核心功能受损（1 小时内响应）
- **P2**: 非核心功能问题（4 小时内响应）
- **P3**: 轻微问题（24 小时内响应）

### 事故报告
事故结束后 24 小时内提交：
- 时间线（Timeline）
- 根因分析（RCA）
- 改进措施（Action Items）
- 预防方案（Prevention）

---

## 📞 联系与支持

- **代码评审**: 至少 1 名核心团队成员 approval
- **架构咨询**: 技术负责人 @your-team
- **紧急问题**: 值班工程师 @pagerduty

---

最后更新: 2024-01-15 | 版本: 1.0.0