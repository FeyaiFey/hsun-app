from typing import List, Optional
from sqlmodel import Session, select
import json
from datetime import datetime
from app.models.email import EmailTemplate
from app.schemas.email import EmailTemplateCreate, EmailTemplateUpdate
from app.core.logger import logger
from app.core.exceptions import CustomException

class CRUDEmail:
    """邮件CRUD操作类"""
    
    def __init__(self, model: EmailTemplate):
        self.model = model
        
    async def get_template(self, db: Session, template_id: int) -> Optional[EmailTemplate]:
        """获取邮件模板"""
        try:
            return db.get(self.model, template_id)
        except Exception as e:
            logger.error(f"获取邮件模板失败: {str(e)}")
            raise CustomException(f"获取邮件模板失败: {str(e)}")
            
    async def create_template(self, db: Session, template: EmailTemplateCreate) -> EmailTemplate:
        """创建邮件模板"""
        try:
            db_template = EmailTemplate(
                name=template.name,
                subject=template.subject,
                content=template.content,
                variables=json.dumps(template.variables)
            )
            db.add(db_template)
            db.commit()
            db.refresh(db_template)
            return db_template
        except Exception as e:
            logger.error(f"创建邮件模板失败: {str(e)}")
            raise CustomException(f"创建邮件模板失败: {str(e)}")
            
    async def update_template(self, db: Session, template_id: int, template: EmailTemplateUpdate) -> EmailTemplate:
        """更新邮件模板"""
        try:
            db_template = db.get(self.model, template_id)
            if not db_template:
                raise CustomException("模板不存在")
                
            update_data = template.model_dump(exclude_unset=True)
            if "variables" in update_data:
                update_data["variables"] = json.dumps(update_data["variables"])
                
            for field, value in update_data.items():
                setattr(db_template, field, value)
                
            db_template.updated_at = datetime.now()
            db.add(db_template)
            db.commit()
            db.refresh(db_template)
            return db_template
        except Exception as e:
            logger.error(f"更新邮件模板失败: {str(e)}")
            raise CustomException(f"更新邮件模板失败: {str(e)}")
            
    async def delete_template(self, db: Session, template_id: int) -> bool:
        """删除邮件模板"""
        try:
            db_template = db.get(self.model, template_id)
            if not db_template:
                raise CustomException("模板不存在")
                
            db.delete(db_template)
            db.commit()
            return True
        except Exception as e:
            logger.error(f"删除邮件模板失败: {str(e)}")
            raise CustomException(f"删除邮件模板失败: {str(e)}")
            
    async def list_templates(self, db: Session) -> List[EmailTemplate]:
        """获取模板列表"""
        try:
            query = select(self.model)
            return db.exec(query).all()
        except Exception as e:
            logger.error(f"获取模板列表失败: {str(e)}")
            raise CustomException(f"获取模板列表失败: {str(e)}")

# 创建CRUD实例
email = CRUDEmail(EmailTemplate) 