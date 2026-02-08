# Development Service Rules

version: 1.0.0
last_updated: 2024-01-15

## 📋 概述
本文档定义了服务端开发的标准规范，适用于所有后端服务模块。

## 🔧 技术栈要求

### 必需技术
- **语言**: TypeScript 5.0+
- **运行时**: Node.js 18+ (LTS)
- **框架**: Express.js 4.x 或 Fastify 4.x
- **数据库**: 根据项目选择（PostgreSQL/MySQL/MongoDB）

### 开发工具
- ESLint + Prettier（配置已提供）
- Jest 或 Vitest（单元测试）
- Supertest（API 集成测试）
- TypeDoc（文档生成）

## 📝 编码规范

### 1. 类型安全
- 所有函数必须有完整的 TypeScript 类型定义
- 禁止使用 `any` 类型（除非有明确注释说明原因）
- 接口和类型必须显式声明，不要使用类型推断

```typescript
// ✅ 正确
interface UserResponse {
  id: string;
  name: string;
  email: string;
}

function getUser(id: string): Promise<UserResponse> {
  // ...
}

// ❌ 禁止
function getUser(id) {
  return db.find(...);
}
```

### 2. 错误处理
- 所有异步操作必须有 try-catch
- 使用自定义错误类继承 `Error`
- API 错误必须返回统一格式

```typescript
class ServiceError extends Error {
  constructor(
    public code: string,
    public message: string,
    public statusCode: number = 500
  ) {
    super(message);
  }
}

// 统一错误响应中间件
app.use((err: Error, req: Request, res: Response, next: NextFunction) => {
  const status = err instanceof ServiceError ? err.statusCode : 500;
  res.status(status).json({
    success: false,
    error: {
      code: err instanceof ServiceError ? err.code : 'INTERNAL_ERROR',
      message: err.message,
    },
  });
});
```

### 3. 日志规范
- 使用结构化日志（JSON 格式）
- 必须包含：timestamp, level, service, traceId
- 敏感信息（密码、token）禁止记录

```typescript
import winston from 'winston';

const logger = winston.createLogger({
  format: winston.format.json(),
  transports: [new winston.transports.Console()],
});

// 使用示例
logger.info('User created', {
  userId: user.id,
  email: user.email,
  traceId: req.headers['x-trace-id'],
});
```

## 🏗️ 架构约束

### 分层架构
```
src/
├── controllers/     # 处理 HTTP 请求/响应
├── services/        # 业务逻辑
├── repositories/    # 数据访问层
├── models/          # 数据模型和类型
├── middleware/      # 中间件
├── utils/           # 工具函数
└── config/          # 配置文件
```

### 关键原则
1. **控制器层**：只做请求验证、调用 service、返回响应
2. **服务层**：核心业务逻辑，可独立于 HTTP 测试
3. **数据层**：所有数据库操作，禁止在 service 中直接查库
4. **禁止跨层调用**：如 controller 直接调用 repository

### 接口设计
- RESTful 设计原则
- 资源名使用复数（`/users` 而非 `/user`）
- 使用正确的 HTTP 方法（GET/POST/PUT/DELETE）
- API 版本控制：`/api/v1/users`

## 🔐 安全要求

### 认证与授权
- 所有 API 必须验证 JWT token（除公开接口）
- 实现 RBAC（基于角色的访问控制）
- 密码必须 bcrypt 哈希存储（cost factor >= 10）

### 数据保护
- 输入验证：使用 class-validator 或 zod
- SQL 注入防护：使用参数化查询/ORM
- XSS 防护：设置 CSP 头部
- 限流：使用 express-rate-limit

```typescript
// 输入验证示例
import { z } from 'zod';

const createUserSchema = z.object({
  name: z.string().min(2).max(100),
  email: z.string().email(),
  password: z.string().min(8),
});

// 在 controller 中
const validated = createUserSchema.parse(req.body);
```

## 🧪 测试要求

### 覆盖率目标
- 单元测试：业务逻辑 > 80%
- 集成测试：API 端点 > 70%
- E2E 测试：关键用户路径

### 测试结构
```
tests/
├── unit/
│   ├── services/
│   └── utils/
├── integration/
│   ├── api/
│   └── database/
└── fixtures/
    └── mocks.ts
```

### 测试最佳实践
- 使用 beforeEach/afterEach 清理测试数据
- Mock 外部依赖（邮件服务、支付网关等）
- 测试边界条件和错误场景

```typescript
describe('UserService', () => {
  let service: UserService;
  let mockRepo: jest.Mocked<UserRepository>;

  beforeEach(() => {
    mockRepo = {
      findById: jest.fn(),
      create: jest.fn(),
    };
    service = new UserService(mockRepo);
  });

  test('should throw error when user not found', async () => {
    mockRepo.findById.mockResolvedValue(null);
    
    await expect(service.getUser('invalid-id'))
      .rejects.toThrow(ServiceError);
  });
});
```

## 📊 性能要求

### 数据库
- 所有查询必须使用索引
- 复杂查询（>3 表 JOIN）需要 DBA 审核
- 分页：使用 cursor-based 分页，禁止 OFFSET

### 缓存策略
- 高频读取数据：Redis 缓存（TTL 根据场景）
- 缓存键格式：`{service}:{resource}:{id}`
- 缓存失效：写操作后主动清除相关缓存

## 🚀 部署规范

### 环境变量
```
# 必需
NODE_ENV=production|development|test
PORT=3000
DATABASE_URL=postgresql://...
JWT_SECRET=...
REDIS_URL=...

# 可选
LOG_LEVEL=info|debug|warn|error
RATE_LIMIT_WINDOW_MS=900000
RATE_LIMIT_MAX_REQUESTS=100
```

### 健康检查
必须实现 `/health` 端点：

```typescript
app.get('/health', async (req, res) => {
  const checks = {
    database: await checkDatabase(),
    redis: await checkRedis(),
    memory: process.memoryUsage().rss < 500_000_000, // 500MB
  };
  
  const healthy = Object.values(checks).every(Boolean);
  res.status(healthy ? 200 : 503).json({ status: healthy ? 'ok' : 'error', checks });
});
```

### Dockerfile 模板
```dockerfile
FROM node:18-alpine
WORKDIR /app
COPY package*.json ./
RUN npm ci --only=production
COPY . .
RUN npm run build
EXPOSE 3000
CMD ["node", "dist/index.js"]
```

## 📚 文档要求

### API 文档
- 使用 OpenAPI 3.0/Swagger
- 每个端点必须包含：
  - 描述
  - 请求参数（类型、必填、示例）
  - 响应格式（成功/错误）
  - 认证要求

```typescript
/**
 * @swagger
 * /users:
 *   post:
 *     summary: 创建新用户
 *     requestBody:
 *       required: true
 *       content:
 *         application/json:
 *           schema:
 *             type: object
 *             properties:
 *               name:
 *                 type: string
 *               email:
 *                 type: string
 *     responses:
 *       201:
 *         description: 用户创建成功
 */
```

### README 内容
- 项目简介
- 技术栈
- 本地开发环境搭建步骤
- 环境变量配置说明
- 数据库迁移脚本运行方法
- 测试运行命令
- 部署指南

---

## ⚠️ 禁止事项

- ❌ 禁止在生产环境使用 console.log
- ❌ 禁止硬编码敏感信息（密码、密钥）
- ❌ 禁止在 git 中提交 .env 文件
- ❌ 禁止在生产环境开启调试模式
- ❌ 禁止使用 eval() 或动态代码执行
- ❌ 禁止在服务端渲染前端模板（纯 API 服务）

---

最后更新: 2024-01-15 | 版本: 1.0.0