# FastAPI 用户认证系统

## 项目简介
这是一个基于FastAPI框架开发的用户认证系统，提供了用户登录等基础功能，使用SQL Server作为数据库存储。

## 功能特性
- 用户登录认证
- JWT Token验证
- 统一响应格式处理
- 全局异常处理

## 技术栈
### 后端框架
- FastAPI：高性能的Python Web框架
- SQLModel：SQL数据库ORM框架
- Pydantic：数据验证和序列化
- Python-Jose：JWT token处理
- PassLib：密码加密处理

### 数据库
- SQL Server
- PyODBC：SQL Server数据库驱动

### 开发工具
- Python 3.x
- uvicorn：ASGI服务器

## 项目结构
```
├── app/
│   ├── api/           # API路由
│   │   └── v1/       # API版本1
│   ├── core/         # 核心配置
│   ├── db/           # 数据库配置
│   ├── models/       # 数据模型
│   ├── schemas/      # Pydantic模型
│   ├── services/     # 业务逻辑
│   └── utils/        # 工具函数
├── .env              # 环境变量配置
└── README.md         # 项目文档
```

## 主要功能块
1. 用户认证模块
   - 用户登录
   - JWT Token生成
   - 密码加密验证

2. 响应处理
   - 统一响应格式
   - 全局异常处理
   - Token信息封装

## 环境要求
- Python 3.7+
- SQL Server
- ODBC Driver 18 for SQL Server

## 配置说明
项目使用.env文件进行配置管理，主要配置项包括：
- 数据库连接信息
- JWT密钥配置
- Token过期时间
- 邮件服务器配置

## API文档
启动服务后访问：http://localhost:8000/docs 查看Swagger API文档

## 快速开始
1. 克隆项目
```bash
git clone [项目地址]
```

2. 安装依赖
```bash
pip install -r requirements.txt
```

3. 配置.env文件
```bash
cp .env.example .env
# 编辑.env文件，填写相关配置
```

4. 启动服务
```bash
uvicorn app.main:app --reload
```

5. 访问API文档
浏览器打开 http://localhost:8000/docs

## 注意事项
- 请确保数据库连接信息正确
- 请妥善保管JWT密钥
- 请定期更新Token过期时间

## 开发计划
- [ ] 添加用户注册功能
- [ ] 实现权限管理
- [ ] 添加日志记录
- [ ] 完善单元测试

## API接口说明

### 认证相关接口 `/api/v1/auth`

#### 用户登录
- **接口**: POST `/api/v1/auth/login`
- **功能**: 用户登录并获取访问令牌
- **请求体**:
```json
{
    "email": "user@example.com",
    "password": "your_password"
}
```
- **响应格式**:
```json
{
    "code": 200,
    "data": {
        "email": "user@example.com",
        "nickname": "用户昵称",
        "department": "部门名称",
        "avatar_url": "头像URL",
        "token": "eyJhbGciOiJIUzI1NiIs..."
    }
}
```
- **错误响应**:
```json
{
    "code": 401,
    "data": "Invalid email or password"
}
```

### 响应状态码说明
| 状态码 | 说明 |
|--------|------|
| 200 | 请求成功 |
| 401 | 未授权（登录失败） |
| 403 | 禁止访问 |
| 404 | 资源不存在 |
| 500 | 服务器内部错误 |

### 统一响应格式
所有API响应都遵循以下格式：
```json
{
    "code": 200,           // 状态码
    "data": {             // 响应数据
        // 具体的响应内容
    }
}
```

### 认证机制
- 使用JWT (JSON Web Token) 进行身份验证
- Token通过Authorization header传递：`Authorization: Bearer <token>`
- Token有效期为30天（可在配置中修改）

### 请求限制
- 登录接口: 每IP每分钟最多尝试5次
- Token有效期: 30天
- 请求体大小限制: 1MB

### 调用示例

使用curl进行登录：
```bash
curl -X POST "http://localhost:8000/api/v1/auth/login" \
     -H "Content-Type: application/json" \
     -d '{"email": "user@example.com", "password": "your_password"}'
```

使用Python requests库：
```python
import requests

response = requests.post(
    'http://localhost:8000/api/v1/auth/login',
    json={
        'email': 'user@example.com',
        'password': 'your_password'
    }
)
print(response.json())
```