from contextlib import asynccontextmanager
from fastapi import FastAPI, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from app.api.v1.endpoints import auth
from app.utils.response import ResponseMiddleware
from app.core.exceptions import exception_handler, get_error_response
from app.core.monitor import MetricsManager
from app.core.logger import logger
from app.schemas.response import IResponse
from app.core.error_codes import HttpStatusCode, ErrorCode

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

# 响应中间件
app.add_middleware(ResponseMiddleware)

# 路由
app.include_router(auth.router, prefix="/api/v1/auth", tags=["Auth"])

# 异常处理器
app.add_exception_handler(Exception, exception_handler)

# 添加验证错误处理器
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request, exc: RequestValidationError):
    """处理请求数据验证错误"""
    errors = []
    for error in exc.errors():
        field = error.get("loc", ["unknown"])[-1]
        msg = error.get("msg", "验证错误")
        errors.append(f"{field}: {msg}")
    
    error_message = "; ".join(errors)
    
    return JSONResponse(
        status_code=HttpStatusCode.BadRequest,
        content=get_error_response(
            status_code=HttpStatusCode.BadRequest,
            message=error_message,
            error_code=ErrorCode.ERR_BAD_REQUEST
        )
    )

@app.get("/")
async def read_root():
    return IResponse(
        code=HttpStatusCode.Ok,
        data={"message": "Welcome to the FastAPI application!"}
    )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
