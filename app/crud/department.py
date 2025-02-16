from typing import List, Optional, Dict, Any
from sqlmodel import Session, select, func
from app.models.department import Department
from app.schemas.department import DepartmentList, DepartmentItem, DepartmentListResponse, DepartmentTableListResponse
from app.models.user import User
from sqlalchemy.orm import aliased

class CRUDDepartment:
    """部门CRUD操作类"""
    
    def __init__(self, model: Department):
        self.model = model

    def get(self, db: Session, id: Any) -> Optional[Department]:
        """根据ID获取记录"""
        return db.get(self.model, id)

    def get_multi(
        self,
        db: Session,
        *,
        skip: int = 0,
        limit: int = 100,
        order_by: Optional[str] = None
    ) -> List[Department]:
        """获取多条记录"""
        query = select(self.model)
        if order_by:
            query = query.order_by(order_by)
        return db.exec(query.offset(skip).limit(limit)).all()

    def get_all(self, db: Session) -> List[Department]:
        """获取所有部门"""
        return db.exec(select(Department)).all()
    
    def get_department_tree_list(self, db: Session) -> DepartmentListResponse:
        """获取树形结构的部门列表
        
        Args:
            db: 数据库会话
            
        Returns:
            DepartmentListResponse: 树形结构的部门列表
        """
        # 获取所有部门
        departments = self.get_all(db)
        
        # 构建部门字典，用于快速查找
        dept_dict: Dict[int, Department] = {dept.id: dept for dept in departments}
        
        # 构建树形结构
        def build_tree(parent_id: Optional[int] = None) -> List[DepartmentItem]:
            items = []
            for dept in departments:
                if dept.parent_id == parent_id:
                    children = build_tree(dept.id)
                    item = DepartmentItem(
                        id=str(dept.id),
                        department_name=dept.department_name,
                        children=children if children else None
                    )
                    items.append(item)
            return items
        
        # 构建根级部门列表
        root_departments = build_tree(None)
        
        # 返回最终结果
        return DepartmentListResponse(list=root_departments)
    
    def get_department_table_list(
        self,
        db: Session,
        *,
        skip: int = 0,
        limit: int = 10,
        department_name: str = None,
        status: int = None,
        order_by: str = None
    ) -> DepartmentTableListResponse:
        """获取部门表格列表数据
        
        Args:
            db: 数据库会话
            skip: 跳过记录数
            limit: 限制记录数
            department_name: 部门名称过滤
            status: 状态过滤
            order_by: 排序字段
            
        Returns:
            DepartmentTableListResponse: 部门表格数据和总记录数
        """
        # 构建基础查询，使用别名进行自连接
        Department_parent = aliased(Department)
        query = (
            select(Department, Department_parent.department_name.label("parent_department_name"))
            .outerjoin(Department_parent, Department.parent_id == Department_parent.id)
        )
        
        # 应用过滤条件
        if department_name:
            query = query.where(Department.department_name.like(f"%{department_name}%"))
        if status is not None:
            query = query.where(Department.status == status)
            
        # 获取总记录数
        total_query = select(func.count()).select_from(query.subquery())
        total = db.exec(total_query).first()
        
        # 应用排序
        if order_by:
            order_field = getattr(Department, order_by.lstrip("-"), None)
            if order_field:
                query = query.order_by(
                    order_field.desc() if order_by.startswith("-") else order_field
                )
        else:
            query = query.order_by(Department.id)
            
        # 应用分页
        query = query.offset(skip).limit(limit)
        results = db.exec(query).all()
        
        # 转换为响应列表
        department_list = [
            DepartmentList(
                id=result[0].id,
                pid=result[0].parent_id,
                department_name=result[0].department_name,
                parent_department=result[1],  # 父部门名称
                status=result[0].status,
                created_at=result[0].created_at.strftime("%Y-%m-%d %H:%M:%S")
            ) for result in results
        ]
        
        return DepartmentTableListResponse(
            list=department_list,
            total=total or 0
        )

    def create(self, db: Session, *, obj_in: dict) -> Department:
        """创建记录"""
        db_obj = self.model(**obj_in)
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def update(self, db: Session, *, db_obj: Department, obj_in: dict) -> Department:
        """更新记录"""
        for field, value in obj_in.items():
            setattr(db_obj, field, value)
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def remove(self, db: Session, *, id: Any) -> Department:
        """删除记录"""
        obj = db.get(self.model, id)
        db.delete(obj)
        db.commit()
        return obj

    def exists(self, db: Session, *, id: Any) -> bool:
        """检查记录是否存在"""
        obj = db.get(self.model, id)
        return obj is not None

department = CRUDDepartment(Department) 