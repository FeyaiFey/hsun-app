from contextlib import asynccontextmanager
from fastapi import FastAPI, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.exceptions import RequestValidationError
from sqlalchemy.exc import SQLAlchemyError
from jose import JWTError

from app.api.v1.endpoints import auth
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

# 注册路由
app.include_router(auth.router, prefix="/api/v1/auth", tags=["Auth"])

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
