from typing import List, Optional
from pydantic import BaseModel, EmailStr, Field
from datetime import datetime

class EmailAttachment(BaseModel):
    """邮件附件模型"""
    filename: str = Field(..., description="文件名")
    content: str = Field(..., description="Base64编码的文件内容")
    content_type: str = Field(..., description="文件类型")

class EmailTemplate(BaseModel):
    """邮件模板模型"""
    id: int = Field(..., description="模板ID")
    name: str = Field(..., description="模板名称")
    subject: str = Field(..., description="邮件主题")
    content: str = Field(..., description="邮件内容")
    variables: List[str] = Field(default=[], description="模板变量列表")
    created_at: datetime = Field(..., description="创建时间")
    updated_at: datetime = Field(..., description="更新时间")

class EmailSendRequest(BaseModel):
    """发送邮件请求模型"""
    to: List[EmailStr] = Field(..., description="收件人列表")
    cc: Optional[List[EmailStr]] = Field(None, description="抄送人列表")
    bcc: Optional[List[EmailStr]] = Field(None, description="密送人列表")
    subject: Optional[str] = Field(None, description="邮件主题，如不提供且使用模板则使用模板主题")
    content: Optional[str] = Field(None, description="邮件内容，如使用模板可不提供")
    template_id: Optional[int] = Field(None, description="模板ID")
    template_vars: Optional[dict] = Field(None, description="模板变量")
    use_template_subject: Optional[bool] = Field(False, description="是否使用模板主题")
    attachments: Optional[List[EmailAttachment]] = Field(None, description="附件列表")

class EmailSendResponse(BaseModel):
    """发送邮件响应模型"""
    success: bool = Field(..., description="是否发送成功")
    message_id: Optional[str] = Field(None, description="邮件ID")
    error: Optional[str] = Field(None, description="错误信息")

class EmailTemplateCreate(BaseModel):
    """创建邮件模板请求模型"""
    name: str = Field(..., description="模板名称")
    subject: str = Field(..., description="邮件主题")
    content: str = Field(..., description="邮件内容")
    variables: List[str] = Field(default=[], description="模板变量列表")

class EmailTemplateUpdate(BaseModel):
    """更新邮件模板请求模型"""
    name: Optional[str] = Field(None, description="模板名称")
    subject: Optional[str] = Field(None, description="邮件主题")
    content: Optional[str] = Field(None, description="邮件内容")
    variables: Optional[List[str]] = Field(None, description="模板变量列表") 