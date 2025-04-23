from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlmodel import Session
from typing import List
from app.core.deps import get_db, get_current_user
from app.schemas.email import (
    EmailSendRequest,
    EmailSendResponse,
    EmailTemplateCreate,
    EmailTemplateUpdate,
    EmailTemplate
)
from app.services.email_service import email_service
from app.crud.email import email as crud_email
from app.core.logger import logger
from app.models.user import User
from app.core.response import CustomResponse
from app.core.exceptions import ValidationException, NotFoundException, BusinessException
from app.core.error_codes import ErrorCode

router = APIRouter()

@router.post("/send")
async def send_email(
    email_data: EmailSendRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """发送邮件
    
    使用当前登录用户的邮箱配置发送邮件，支持模板和自定义主题
    """
    try:
        # 基本验证
        if not email_data.to or len(email_data.to) == 0:
            raise ValidationException("收件人不能为空")
            
        # 如果使用模板，验证模板是否存在
        if email_data.template_id:
            template = await crud_email.get_template(db, email_data.template_id)
            if not template:
                raise NotFoundException(f"模板不存在 (ID: {email_data.template_id})")
                
            # 如果没有内容，则必须使用模板
            if not email_data.content and not template:
                raise ValidationException("邮件内容不能为空")
                
        # 如果不使用模板，则必须提供内容
        elif not email_data.content:
            raise ValidationException("不使用模板时，邮件内容不能为空")
        
        # 如果不使用模板主题，则必须提供主题
        if not email_data.use_template_subject and not email_data.subject and not email_data.template_id:
            raise ValidationException("邮件主题不能为空")
            
        # 发送邮件
        result = await email_service.send_email(
            email_data=email_data,
            db=db,
            user_id=current_user.id
        )
        
        if not result.success:
            raise BusinessException(result.error)
            
        return CustomResponse.success(data=result, message="邮件发送成功")
        
    except (ValidationException, NotFoundException, BusinessException):
        raise
    except Exception as e:
        logger.error(f"发送邮件失败: {str(e)}")
        raise BusinessException(f"发送邮件失败: {str(e)}")

@router.post("/templates")
async def create_template(
    template: EmailTemplateCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """创建邮件模板"""
    try:
        result = await crud_email.create_template(db, template)
        return CustomResponse.success(data=result, message="模板创建成功")
    except Exception as e:
        logger.error(f"创建模板失败: {str(e)}")
        raise BusinessException(f"创建模板失败: {str(e)}")

@router.get("/templates")
async def list_templates(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """获取邮件模板列表"""
    try:
        result = await crud_email.list_templates(db)
        return CustomResponse.success(data=result)
    except Exception as e:
        logger.error(f"获取模板列表失败: {str(e)}")
        raise BusinessException(f"获取模板列表失败: {str(e)}")

@router.get("/templates/{template_id}")
async def get_template(
    template_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """获取单个邮件模板"""
    try:
        template = await crud_email.get_template(db, template_id)
        if not template:
            raise NotFoundException("模板不存在")
        return CustomResponse.success(data=template)
    except NotFoundException:
        raise
    except Exception as e:
        logger.error(f"获取模板失败: {str(e)}")
        raise BusinessException(f"获取模板失败: {str(e)}")

@router.put("/templates/{template_id}")
async def update_template(
    template_id: int,
    template: EmailTemplateUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """更新邮件模板"""
    try:
        # 检查模板是否存在
        existing_template = await crud_email.get_template(db, template_id)
        if not existing_template:
            raise NotFoundException("模板不存在")
            
        result = await crud_email.update_template(db, template_id, template)
        return CustomResponse.success(data=result, message="模板更新成功")
    except NotFoundException:
        raise
    except Exception as e:
        logger.error(f"更新模板失败: {str(e)}")
        raise BusinessException(f"更新模板失败: {str(e)}")

@router.delete("/templates/{template_id}")
async def delete_template(
    template_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """删除邮件模板"""
    try:
        # 检查模板是否存在
        existing_template = await crud_email.get_template(db, template_id)
        if not existing_template:
            raise NotFoundException("模板不存在")
            
        await crud_email.delete_template(db, template_id)
        return CustomResponse.success(message="模板已删除")
    except NotFoundException:
        raise
    except Exception as e:
        logger.error(f"删除模板失败: {str(e)}")
        raise BusinessException(f"删除模板失败: {str(e)}") 