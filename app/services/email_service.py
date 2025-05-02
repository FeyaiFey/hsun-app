import aiosmtplib
import imaplib
import ssl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication
import base64
from typing import List, Optional, Dict, Any, Union
from datetime import datetime
import contextlib
import re

from app.core.config import settings
from app.core.logger import logger
from app.schemas.email import (
    EmailSendRequest,
    EmailSendResponse,
    EmailTemplate,
    EmailTemplateCreate,
    EmailTemplateUpdate,
    EmailAttachment
)
from app.crud.email import email as crud_email
from app.crud.user import user as crud_user
from app.crud.e10 import CRUDE10
from app.core.exceptions import CustomException, BusinessException, ValidationException

class EmailService:
    """邮件服务类"""
    
    def __init__(self):
        # 默认值，将在发送邮件时根据用户信息覆盖
        self.smtp_host = None
        self.smtp_port = None
        self.smtp_user = None
        self.smtp_password = None
        self.smtp_use_ssl = True  # 默认使用 SSL
        self.imap_host = None     # IMAP服务器
        self.imap_port = 993      # 默认IMAP SSL端口
        self.imap_use_ssl = True  # 默认使用SSL
        self.timeout = 30         # 默认超时时间（秒）
        
    async def send_email(self, email_data: EmailSendRequest, db = None, user_id: int = None) -> EmailSendResponse:
        """发送邮件
        
        Args:
            email_data: 邮件数据
            db: 数据库会话
            user_id: 用户ID
            save_to_sent_folder: 是否将邮件保存到发件箱，默认为True
        """
        try:
            # 设置邮箱配置
            self._setup_email_config(db, user_id)
            
            # 构建邮件内容
            message, subject = await self._build_email_message(email_data, db)
            
            # 发送邮件
            success, error_msg, message_id = await self._send_email_via_smtp(message)
            if not success:
                return EmailSendResponse(
                    success=False,
                    error=error_msg
                )

            logger.info(f"邮件发送成功: {subject}")
            return EmailSendResponse(
                success=True,
                message_id=message_id if isinstance(message_id, str) else str(message_id)
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
    
    async def send_assyorder_email(self, email_data: EmailSendRequest, db = None, user_id: int = None)-> EmailSendResponse:
        try:
            # 设置邮箱配置
            self._setup_email_config(db, user_id)

            if not email_data.attachments:
                e10 = CRUDE10()
                excel_data = e10.export_assy_orders(db)

                if excel_data:
                    # 将bytes数据包装成附件格式
                    current_time = datetime.now().strftime("%Y%m%d_%H%M%S")
                    filename = f"封装单_{current_time}.xlsx"
                    email_data.attachments = [EmailAttachment(
                        filename=filename,
                        content=base64.b64encode(excel_data).decode('utf-8'),
                        content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                    )]
            
            # 构建邮件内容
            message, subject = await self._build_email_message(email_data, db)
            
            # 发送邮件
            success, error_msg, message_id = await self._send_email_via_smtp(message)
            if not success:
                return EmailSendResponse(
                    success=False,
                    error=error_msg
                )

            logger.info(f"邮件发送成功: {subject}")
            return EmailSendResponse(
                success=True,
                message_id=message_id if isinstance(message_id, str) else str(message_id)
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
    
    def _setup_email_config(self, db, user_id: int = None):
        """设置邮箱配置"""
        # 如果提供了 user_id 和 db，则使用用户的邮箱配置
        if db and user_id:
            user_email_info = crud_user.get_user_email_info(db, user_id)
            if user_email_info:
                self.imap_host = user_email_info.IMAP_SERVER
                self.smtp_host = user_email_info.SMTP_SERVER
                self.smtp_port = user_email_info.SMTP_PORT
                self.smtp_user = user_email_info.EMAIL
                self.smtp_password = user_email_info.PASSWORD
                
                # SSL配置
                if hasattr(user_email_info, 'SMTP_USE_SSL'):
                    self.smtp_use_ssl = bool(user_email_info.SMTP_USE_SSL)
                    
                # IMAP配置
                if hasattr(user_email_info, 'IMAP_PORT'):
                    self.imap_port = user_email_info.IMAP_PORT
                if hasattr(user_email_info, 'IMAP_USE_SSL'):
                    self.imap_use_ssl = bool(user_email_info.IMAP_USE_SSL)
                
                # 超时设置
                if hasattr(user_email_info, 'TIMEOUT'):
                    self.timeout = user_email_info.TIMEOUT
            else:
                logger.warning(f"未找到用户邮箱信息，将使用系统默认配置")

        # 确保 SMTP 配置已设置，如果未通过用户配置设置，则使用系统默认配置
        if not all([self.smtp_host, self.smtp_port, self.smtp_user, self.smtp_password]):
            self.smtp_host = settings.SMTP_HOST
            self.smtp_port = settings.SMTP_PORT
            self.smtp_user = settings.SMTP_USER
            self.smtp_password = settings.SMTP_PASSWORD
            
            # 默认IMAP配置
            self.imap_host = getattr(settings, 'IMAP_HOST', settings.SMTP_HOST)
            self.imap_port = getattr(settings, 'IMAP_PORT', 993)
            
            # SSL配置
            self.smtp_use_ssl = getattr(settings, 'SMTP_USE_SSL', True)
            self.imap_use_ssl = getattr(settings, 'IMAP_USE_SSL', True)
            
            # 超时设置
            self.timeout = getattr(settings, 'SMTP_TIMEOUT', 30)
            
    async def _build_email_message(self, email_data: EmailSendRequest, db = None) -> tuple:
        """构建邮件消息对象
        
        返回一个元组：(邮件对象, 邮件主题)
        """
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
                    
        return message, subject
        
    async def _send_email_via_smtp(self, message) -> tuple:
        """通过SMTP发送邮件
        
        返回元组：(成功标志, 错误信息, 消息ID)
        """
        try:
            # 创建安全上下文
            context = ssl.create_default_context()
            
            # 记录连接信息
            logger.info(f"正在连接SMTP服务器: {self.smtp_host}:{self.smtp_port} (SSL: {self.smtp_use_ssl})")
            
            # 初始化SMTP参数
            smtp_kwargs = {}
            
            # 根据是否使用SSL选择不同的连接方式
            if self.smtp_use_ssl:
                # 使用SMTP_SSL类似于smtplib.SMTP_SSL的连接方式
                client = aiosmtplib.SMTP(
                    hostname=self.smtp_host,
                    port=self.smtp_port,
                    use_tls=False,
                    tls_context=context
                )
                # 直接连接到SSL端口
                await client.connect(
                    timeout=self.timeout,
                    hostname=self.smtp_host, 
                    port=self.smtp_port,
                    tls_context=context,
                    use_tls=True,
                    start_tls=False
                )
            else:
                # 不使用SSL的常规连接
                client = aiosmtplib.SMTP(
                    hostname=self.smtp_host,
                    port=self.smtp_port
                )
                await client.connect(timeout=self.timeout)
            
            # 登录
            await client.login(self.smtp_user, self.smtp_password)
            logger.info(f"SMTP登录成功: {self.smtp_user}")
            
            # 发送邮件
            send_result = await client.send_message(message)
            
            # 关闭连接
            await client.quit()
            
            # 从元组中提取消息ID或使用消息的Message-ID
            message_id = None
            if isinstance(send_result, tuple) and len(send_result) > 1:
                message_id = send_result[1]  # 取元组的第二个元素作为消息ID
            else:
                message_id = message.get("Message-ID", str(send_result))
                
            return True, None, message_id
                
        except aiosmtplib.SMTPException as e:
            error_msg = f"邮件服务器错误: {str(e)}"
            logger.error(f"SMTP错误: {str(e)}")
            return False, error_msg, None
        except Exception as e:
            error_msg = f"发送邮件时发生错误: {str(e)}"
            logger.error(error_msg)
            return False, error_msg, None
    
    def _connect_to_imap(self):
        """连接到IMAP服务器，处理不同的连接方式"""
        try:
            if self.imap_use_ssl:
                try:
                    return imaplib.IMAP4_SSL(self.imap_host, self.imap_port, timeout=self.timeout)
                except Exception as ssl_error:
                    # SSL连接失败，尝试非SSL连接
                    logger.warning(f"SSL连接IMAP服务器失败: {str(ssl_error)}，尝试非SSL连接")
                    self.imap_use_ssl = False
                    return imaplib.IMAP4(self.imap_host, 143, timeout=self.timeout)  # 使用标准非SSL端口
            else:
                return imaplib.IMAP4(self.imap_host, 143, timeout=self.timeout)
        except Exception as e:
            logger.error(f"连接IMAP服务器失败: {str(e)}")
            return None
            
    def _get_imap_folders(self, imap) -> List[str]:
        """获取IMAP文件夹列表"""
        try:
            result, mailboxes = imap.list()
            if result == 'OK':
                return [folder.decode().split(' "/" ')[1].strip('"') for folder in mailboxes]
            return []
        except Exception as e:
            logger.error(f"获取IMAP文件夹失败: {str(e)}")
            return []

    def _render_template(self, template: EmailTemplate, variables: Dict[str, Any]) -> str:
        """渲染邮件模板内容，使用简单的变量替换而非Jinja2"""
        try:
            content = template.content
            # 使用正则表达式查找并替换模板变量
            # 支持 {{ variable }} 格式的变量
            for key, value in variables.items():
                pattern = r"{{\s*" + key + r"\s*}}"
                content = re.sub(pattern, str(value), content)
            return content
        except Exception as e:
            logger.error(f"渲染模板失败: {str(e)}")
            raise BusinessException(f"渲染模板失败: {str(e)}")
            
    def _render_template_string(self, template_str: str, variables: Dict[str, Any]) -> str:
        """渲染模板字符串，用于处理主题等短文本"""
        try:
            result = template_str
            # 使用正则表达式查找并替换模板变量
            for key, value in variables.items():
                pattern = r"{{\s*" + key + r"\s*}}"
                result = re.sub(pattern, str(value), result)
            return result
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