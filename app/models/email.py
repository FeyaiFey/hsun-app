from datetime import datetime
from sqlmodel import SQLModel, Field

class EmailTemplate(SQLModel, table=True):
    """邮件模板模型"""
    __tablename__ = "huaxinAdmin_email_templates"
    
    id: int = Field(default=None, primary_key=True)
    name: str = Field(..., description="模板名称")
    subject: str = Field(..., description="邮件主题")
    content: str = Field(..., description="邮件内容")
    variables: str = Field(default="[]", description="模板变量列表(JSON格式)")
    created_at: datetime = Field(default_factory=datetime.now, description="创建时间")
    updated_at: datetime = Field(default_factory=datetime.now, description="更新时间") 
    is_active: bool = Field(default=True, description="是否启用")
    category: str = Field(default="system", description="模板分类")
    description: str = Field(default="", description="模板描述")
