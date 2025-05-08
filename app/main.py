from contextlib import asynccontextmanager
from fastapi import FastAPI, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.exceptions import RequestValidationError
from sqlalchemy.exc import SQLAlchemyError
from jose import JWTError
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from starlette.middleware.sessions import SessionMiddleware
from app.core.config import settings

from app.api.v1.endpoints import auth, department, purchase, user, role, assy, params, stock, report, email, sale
from app.core.monitor import MetricsManager
from app.core.logger import logger
from app.core.exceptions import CustomException
from app.core.exception_handlers import (
    custom_exception_handler,
    validation_exception_handler,
    database_exception_handler,
    jwt_exception_handler,
    general_exception_handler
)

@asynccontextmanager
async def lifespan(app: FastAPI):
    # 启动事件
    try:
        metrics = MetricsManager()
        metrics.start_metrics_server()
        logger.info("应用启动成功")
    except Exception as e:
        logger.error(f"应用启动失败: {str(e)}")
    yield
    # 关闭事件
    logger.info("应用关闭")

app = FastAPI(
    title="HSUN-BACKEND-API",
    version="1.0.0",
    lifespan=lifespan
)

# CORS中间件
app.add_middleware(
    CORSMiddleware,
    allow_origins=['*'],
    allow_credentials=True,
    allow_methods=['*'],
    allow_headers=['*'],
)

# 安全中间件
app.add_middleware(TrustedHostMiddleware, allowed_hosts=["*"])
app.add_middleware(GZipMiddleware, minimum_size=1000)
app.add_middleware(
    SessionMiddleware,
    secret_key=settings.SECRET_KEY,
    session_cookie="session",
    max_age=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
    same_site="lax",
    https_only=False
)

# 挂载静态文件路径
app.mount("/static", StaticFiles(directory="static"), name="static")

# 注册路由
app.include_router(auth.router, prefix="/api/v1/auth", tags=["Auth"])
app.include_router(department.router, prefix="/api/v1/department", tags=["Department"])
app.include_router(user.router, prefix="/api/v1/user", tags=["User"])
app.include_router(role.router, prefix="/api/v1/role", tags=["Role"])
app.include_router(assy.router, prefix="/api/v1/assy", tags=["Assy"])
app.include_router(purchase.router, prefix="/api/v1/purchase", tags=["Purchase"])
app.include_router(params.router, prefix="/api/v1/params", tags=["Params"])
app.include_router(stock.router, prefix="/api/v1/stock", tags=["Stock"])
app.include_router(report.router, prefix="/api/v1/report", tags=["Report"])
app.include_router(email.router, prefix="/api/v1/email", tags=["Email"])
app.include_router(sale.router, prefix="/api/v1/sale", tags=["Sale"])
# 注册异常处理器
app.add_exception_handler(CustomException, custom_exception_handler)
app.add_exception_handler(RequestValidationError, validation_exception_handler)
app.add_exception_handler(SQLAlchemyError, database_exception_handler)
app.add_exception_handler(JWTError, jwt_exception_handler)
app.add_exception_handler(Exception, general_exception_handler)

@app.get("/")
async def read_root():
    """健康检查接口"""
    return {"status": "ok", "message": "Service is running"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
