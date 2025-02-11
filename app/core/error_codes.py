from enum import Enum, IntEnum
from typing import Literal

class ErrorCode(str, Enum):
    """Axios 错误代码枚举"""
    ERR_FR_TOO_MANY_REDIRECTS = "ERR_FR_TOO_MANY_REDIRECTS"
    ERR_BAD_OPTION_VALUE = "ERR_BAD_OPTION_VALUE"
    ERR_BAD_OPTION = "ERR_BAD_OPTION"
    ERR_NETWORK = "ERR_NETWORK"
    ERR_DEPRECATED = "ERR_DEPRECATED"
    ERR_BAD_RESPONSE = "ERR_BAD_RESPONSE"
    ERR_BAD_REQUEST = "ERR_BAD_REQUEST"
    ERR_NOT_SUPPORT = "ERR_NOT_SUPPORT"
    ERR_INVALID_URL = "ERR_INVALID_URL"
    ERR_CANCELED = "ERR_CANCELED"
    ECONNABORTED = "ECONNABORTED"
    ETIMEDOUT = "ETIMEDOUT"
    ERR_UNAUTHORIZED = "ERR_UNAUTHORIZED"
    ERR_FORBIDDEN = "ERR_FORBIDDEN"
    ERR_NOT_FOUND = "ERR_NOT_FOUND"
    ERR_CONFLICT = "ERR_CONFLICT"
    ERR_INTERNAL_SERVER = "ERR_INTERNAL_SERVER"

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
    'patch', 'PATCH',
    'purge', 'PURGE',
    'link', 'LINK',
    'unlink', 'UNLINK'
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
    'ascii', 'ASCII',
    'ansi', 'ANSI',
    'binary', 'BINARY',
    'base64', 'BASE64',
    'base64url', 'BASE64URL',
    'hex', 'HEX',
    'latin1', 'LATIN1',
    'ucs-2', 'UCS-2',
    'ucs2', 'UCS2',
    'utf-8', 'UTF-8',
    'utf8', 'UTF8',
    'utf16le', 'UTF16LE'
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