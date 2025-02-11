from enum import Enum, IntEnum
from typing import Literal

class ErrorCode(str, Enum):
    """业务错误代码枚举"""
    # 通用错误
    SUCCESS = "SUCCESS"                           # 成功
    FAILED = "FAILED"                            # 失败
    PARAM_ERROR = "PARAM_ERROR"                  # 参数错误
    SYSTEM_ERROR = "SYSTEM_ERROR"                # 系统错误
    
    # 认证相关错误
    TOKEN_INVALID = "TOKEN_INVALID"              # Token无效
    TOKEN_EXPIRED = "TOKEN_EXPIRED"              # Token过期
    TOKEN_REQUIRED = "TOKEN_REQUIRED"            # 需要Token
    PERMISSION_DENIED = "PERMISSION_DENIED"      # 权限不足
    
    # 用户相关错误
    USER_NOT_FOUND = "USER_NOT_FOUND"           # 用户不存在
    USER_ALREADY_EXISTS = "USER_ALREADY_EXISTS"  # 用户已存在
    PASSWORD_ERROR = "PASSWORD_ERROR"            # 密码错误
    ACCOUNT_LOCKED = "ACCOUNT_LOCKED"           # 账号被锁定
    
    # 资源相关错误
    RESOURCE_NOT_FOUND = "RESOURCE_NOT_FOUND"    # 资源不存在
    RESOURCE_ALREADY_EXISTS = "RESOURCE_EXISTS"   # 资源已存在
    RESOURCE_EXPIRED = "RESOURCE_EXPIRED"        # 资源已过期
    
    # 数据库相关错误
    DB_ERROR = "DB_ERROR"                        # 数据库错误
    DB_CONNECTION_ERROR = "DB_CONNECTION_ERROR"  # 数据库连接错误
    DB_DUPLICATE_KEY = "DB_DUPLICATE_KEY"       # 唯一键冲突
    
    # 文件相关错误
    FILE_NOT_FOUND = "FILE_NOT_FOUND"           # 文件不存在
    FILE_TOO_LARGE = "FILE_TOO_LARGE"           # 文件太大
    FILE_TYPE_ERROR = "FILE_TYPE_ERROR"         # 文件类型错误

class HttpStatusCode(IntEnum):
    """HTTP状态码枚举"""
    Continue = 100
    SwitchingProtocols = 101
    Processing = 102
    EarlyHints = 103
    Ok = 200
    Created = 201
    Accepted = 202
    NonAuthoritativeInformation = 203
    NoContent = 204
    ResetContent = 205
    PartialContent = 206
    MultiStatus = 207
    AlreadyReported = 208
    ImUsed = 226
    MultipleChoices = 300
    MovedPermanently = 301
    Found = 302
    SeeOther = 303
    NotModified = 304
    UseProxy = 305
    Unused = 306
    TemporaryRedirect = 307
    PermanentRedirect = 308
    BadRequest = 400
    Unauthorized = 401
    PaymentRequired = 402
    Forbidden = 403
    NotFound = 404
    MethodNotAllowed = 405
    NotAcceptable = 406
    ProxyAuthenticationRequired = 407
    RequestTimeout = 408
    Conflict = 409
    Gone = 410
    LengthRequired = 411
    PreconditionFailed = 412
    PayloadTooLarge = 413
    UriTooLong = 414
    UnsupportedMediaType = 415
    RangeNotSatisfiable = 416
    ExpectationFailed = 417
    ImATeapot = 418
    MisdirectedRequest = 421
    UnprocessableEntity = 422
    Locked = 423
    FailedDependency = 424
    TooEarly = 425
    UpgradeRequired = 426
    PreconditionRequired = 428
    TooManyRequests = 429
    RequestHeaderFieldsTooLarge = 431
    UnavailableForLegalReasons = 451
    InternalServerError = 500
    NotImplemented = 501
    BadGateway = 502
    ServiceUnavailable = 503
    GatewayTimeout = 504
    HttpVersionNotSupported = 505
    VariantAlsoNegotiates = 506
    InsufficientStorage = 507
    LoopDetected = 508
    NotExtended = 510
    NetworkAuthenticationRequired = 511

# HTTP 方法类型
HttpMethod = Literal[
    'get', 'GET',
    'delete', 'DELETE',
    'head', 'HEAD',
    'options', 'OPTIONS',
    'post', 'POST',
    'put', 'PUT',
    'patch', 'PATCH'
]

# 响应类型
ResponseType = Literal[
    'arraybuffer',
    'blob',
    'document',
    'json',
    'text',
    'stream',
    'formdata'
]

# 响应编码类型
ResponseEncoding = Literal[
    'utf-8', 'UTF-8',
    'utf8', 'UTF8',
    'ascii', 'ASCII',
    'binary', 'BINARY',
    'base64', 'BASE64',
    'latin1', 'LATIN1'
]

def get_status_text(status_code: int) -> str:
    """获取HTTP状态码对应的文本描述
    
    Args:
        status_code: HTTP状态码
        
    Returns:
        str: 状态码描述文本
    """
    try:
        return HttpStatusCode(status_code).name.replace('_', ' ')
    except ValueError:
        return "Unknown Status"

def get_error_message(error_code: ErrorCode) -> str:
    """获取错误代码对应的默认消息
    
    Args:
        error_code: 错误代码
        
    Returns:
        str: 错误消息
    """
    error_messages = {
        ErrorCode.SUCCESS: "操作成功",
        ErrorCode.FAILED: "操作失败",
        ErrorCode.PARAM_ERROR: "参数错误",
        ErrorCode.SYSTEM_ERROR: "系统错误",
        ErrorCode.TOKEN_INVALID: "无效的访问令牌",
        ErrorCode.TOKEN_EXPIRED: "访问令牌已过期",
        ErrorCode.TOKEN_REQUIRED: "需要访问令牌",
        ErrorCode.PERMISSION_DENIED: "权限不足",
        ErrorCode.USER_NOT_FOUND: "用户不存在",
        ErrorCode.USER_ALREADY_EXISTS: "用户已存在",
        ErrorCode.PASSWORD_ERROR: "密码错误",
        ErrorCode.ACCOUNT_LOCKED: "账号已被锁定",
        ErrorCode.RESOURCE_NOT_FOUND: "资源不存在",
        ErrorCode.RESOURCE_ALREADY_EXISTS: "资源已存在",
        ErrorCode.RESOURCE_EXPIRED: "资源已过期",
        ErrorCode.DB_ERROR: "数据库错误",
        ErrorCode.DB_CONNECTION_ERROR: "数据库连接错误",
        ErrorCode.DB_DUPLICATE_KEY: "数据已存在",
        ErrorCode.FILE_NOT_FOUND: "文件不存在",
        ErrorCode.FILE_TOO_LARGE: "文件大小超出限制",
        ErrorCode.FILE_TYPE_ERROR: "不支持的文件类型"
    }
    return error_messages.get(error_code, "未知错误") 