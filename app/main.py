from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.v1.endpoints import auth
from app.utils.response import ResponseMiddleware
from app.core.exceptions import exception_handler
from app.core.monitor import start_metrics_server
from app.core.logger import logger

@asynccontextmanager
async def lifespan(app: FastAPI):
    # 启动事件
    try:
        start_metrics_server()
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

# 响应中间件
app.add_middleware(ResponseMiddleware)

# 路由
app.include_router(auth.router, prefix="/api/auth", tags=["Auth"])

# 异常处理器
app.add_exception_handler(Exception, exception_handler)

@app.get("/")
async def read_root():
    return {"message": "Welcome to the FastAPI application!"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
