import aiosmtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication
import base64
from typing import List, Optional, Dict, Any
from datetime import datetime
import jinja2
from app.core.config import settings
from app.core.logger import logger
from app.schemas.email import (
    EmailSendRequest,
    EmailSendResponse,
    EmailTemplate,
    EmailTemplateCreate,
    EmailTemplateUpdate
)
from app.crud.email import email as crud_email
from app.crud.user import user as crud_user
from app.core.exceptions import CustomException, BusinessException, ValidationException

class EmailService:
    """邮件服务类"""
    
    def __init__(self):
        self.template_env = jinja2.Environment(
            loader=jinja2.FileSystemLoader("app/templates/email"),
            autoescape=True
        )
        # 默认值，将在发送邮件时根据用户信息覆盖
        self.smtp_host = None
        self.smtp_port = None
        self.smtp_user = None
        self.smtp_password = None
        self.smtp_use_tls = True  # 默认使用 TLS
        
    async def send_email(self, email_data: EmailSendRequest, db = None, user_id: int = None) -> EmailSendResponse:
        """发送邮件"""
        try:
            # 如果提供了 user_id 和 db，则使用用户的邮箱配置
            if db and user_id:
                user_email_info = crud_user.get_user_email_info(db, user_id)
                if user_email_info:
                    self.smtp_host = user_email_info.IMAP_SERVER
                    self.smtp_port = user_email_info.SMTP_PORT
                    self.smtp_user = user_email_info.EMAIL
                    self.smtp_password = user_email_info.PASSWORD
                else:
                    logger.warning(f"未找到用户邮箱信息，将使用系统默认配置")

            # 确保 SMTP 配置已设置
            if not all([self.smtp_host, self.smtp_port, self.smtp_user, self.smtp_password]):
                # 如果未通过用户配置设置，则使用系统默认配置
                self.smtp_host = settings.SMTP_HOST
                self.smtp_port = settings.SMTP_PORT
                self.smtp_user = settings.SMTP_USER
                self.smtp_password = settings.SMTP_PASSWORD

            # 处理主题和内容
            subject = email_data.subject
            content = email_data.content
            
            # 如果使用模板，处理内容和可能的主题
            if email_data.template_id and db:
                template = await self.get_template(db, email_data.template_id)
                if template:
                    # 渲染模板内容
                    content = self._render_template(template, email_data.template_vars or {})
                    
                    # 如果请求使用模板主题，或者没有提供自定义主题
                    if getattr(email_data, 'use_template_subject', False) or not subject:
                        # 渲染主题中的变量
                        subject = self._render_template_string(
                            template.subject, 
                            email_data.template_vars or {}
                        )
                        logger.info(f"使用模板主题: {subject}")

            # 构建邮件
            message = MIMEMultipart()
            message["From"] = self.smtp_user
            message["To"] = ", ".join(email_data.to)
            
            if email_data.cc:
                message["Cc"] = ", ".join(email_data.cc)
            if email_data.bcc:
                message["Bcc"] = ", ".join(email_data.bcc)
                
            message["Subject"] = subject

            # 添加邮件正文
            message.attach(MIMEText(content, "html"))

            # 处理附件
            if email_data.attachments:
                for attachment in email_data.attachments:
                    try:
                        file_content = base64.b64decode(attachment.content)
                        part = MIMEApplication(
                            file_content,
                            Name=attachment.filename
                        )
                        part['Content-Disposition'] = f'attachment; filename="{attachment.filename}"'
                        message.attach(part)
                    except Exception as e:
                        logger.error(f"处理附件失败: {attachment.filename}, 错误: {str(e)}")
                        raise BusinessException(f"处理附件失败: {attachment.filename}")

            # 连接SMTP服务器并发送邮件
            try:
                async with aiosmtplib.SMTP(
                    hostname=self.smtp_host,
                    port=self.smtp_port,
                    use_tls=self.smtp_use_tls
                ) as smtp:
                    await smtp.login(self.smtp_user, self.smtp_password)
                    await smtp.send_message(message)
            except aiosmtplib.SMTPException as e:
                logger.error(f"SMTP错误: {str(e)}")
                return EmailSendResponse(
                    success=False,
                    error=f"邮件服务器错误: {str(e)}"
                )

            logger.info(f"邮件发送成功: {subject}")
            return EmailSendResponse(
                success=True,
                message_id=message["Message-ID"]
            )

        except BusinessException as e:
            # 重新抛出业务异常
            raise
        except Exception as e:
            logger.error(f"发送邮件失败: {str(e)}")
            return EmailSendResponse(
                success=False,
                error=str(e)
            )

    def _render_template(self, template: EmailTemplate, variables: Dict[str, Any]) -> str:
        """渲染邮件模板内容"""
        try:
            template_obj = self.template_env.from_string(template.content)
            return template_obj.render(**variables)
        except Exception as e:
            logger.error(f"渲染模板失败: {str(e)}")
            raise BusinessException(f"渲染模板失败: {str(e)}")
            
    def _render_template_string(self, template_str: str, variables: Dict[str, Any]) -> str:
        """渲染模板字符串，用于处理主题等短文本"""
        try:
            template_obj = self.template_env.from_string(template_str)
            return template_obj.render(**variables)
        except Exception as e:
            logger.error(f"渲染模板字符串失败: {str(e)}")
            # 如果渲染失败，返回原始字符串
            return template_str

    async def get_template(self, db, template_id: int) -> Optional[EmailTemplate]:
        """获取邮件模板"""
        try:
            return await crud_email.get_template(db, template_id)
        except Exception as e:
            logger.error(f"获取模板失败: {str(e)}")
            raise BusinessException(f"获取模板失败: {str(e)}")

    async def create_template(self, db, template: EmailTemplateCreate) -> EmailTemplate:
        """创建邮件模板"""
        try:
            return await crud_email.create_template(db, template)
        except Exception as e:
            logger.error(f"创建模板失败: {str(e)}")
            raise BusinessException(f"创建模板失败: {str(e)}")

    async def update_template(self, db, template_id: int, template: EmailTemplateUpdate) -> EmailTemplate:
        """更新邮件模板"""
        try:
            return await crud_email.update_template(db, template_id, template)
        except Exception as e:
            logger.error(f"更新模板失败: {str(e)}")
            raise BusinessException(f"更新模板失败: {str(e)}")

    async def delete_template(self, db, template_id: int) -> bool:
        """删除邮件模板"""
        try:
            return await crud_email.delete_template(db, template_id)
        except Exception as e:
            logger.error(f"删除模板失败: {str(e)}")
            raise BusinessException(f"删除模板失败: {str(e)}")

    async def list_templates(self, db) -> List[EmailTemplate]:
        """获取模板列表"""
        try:
            return await crud_email.list_templates(db)
        except Exception as e:
            logger.error(f"获取模板列表失败: {str(e)}")
            raise BusinessException(f"获取模板列表失败: {str(e)}")

    async def send_template_email(
        self,
        db,
        to_email: List[str],
        template_id: int,
        template_vars: Optional[dict] = None,
        cc: Optional[List[str]] = None,
        bcc: Optional[List[str]] = None,
        attachments: Optional[List[dict]] = None,
        user_id: Optional[int] = None
    ) -> EmailSendResponse:
        """使用模板发送邮件"""
        try:
            # 获取模板
            template = await self.get_template(db, template_id)
            if not template:
                raise ValidationException(f"模板不存在 (ID: {template_id})")
                
            # 构建请求
            email_data = EmailSendRequest(
                to=to_email,
                cc=cc,
                bcc=bcc,
                subject=None,  # 使用模板主题
                content=None,  # 使用模板内容
                template_id=template_id,
                template_vars=template_vars or {},
                use_template_subject=True,
                attachments=attachments
            )
            
            # 发送邮件
            return await self.send_email(
                email_data=email_data,
                db=db,
                user_id=user_id
            )
        except ValidationException:
            raise
        except Exception as e:
            logger.error(f"使用模板发送邮件失败: {str(e)}")
            raise BusinessException(f"使用模板发送邮件失败: {str(e)}")

# 创建服务实例
email_service = EmailService() 