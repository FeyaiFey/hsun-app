import asyncio
import threading
import time
from typing import Optional
from app.core.config import settings
from app.core.logger import logger
from app.db.session import cleanup_expired_connections, active_connections, connection_lock


class DatabaseCleanupScheduler:
    """数据库连接清理调度器"""
    
    def __init__(self, cleanup_interval: int = 30):
        """
        初始化调度器
        
        Args:
            cleanup_interval: 清理间隔时间（秒），默认30秒
        """
        self.cleanup_interval = cleanup_interval
        self.is_running = False
        self.cleanup_thread: Optional[threading.Thread] = None
        self._stop_event = threading.Event()
    
    def start(self):
        """启动定时清理任务"""
        if self.is_running:
            logger.warning("数据库清理调度器已在运行")
            return
        
        self.is_running = True
        self._stop_event.clear()
        
        # 启动后台线程
        self.cleanup_thread = threading.Thread(
            target=self._cleanup_worker,
            daemon=True,
            name="DatabaseCleanupScheduler"
        )
        self.cleanup_thread.start()
        
        logger.info(f"数据库清理调度器已启动，清理间隔: {self.cleanup_interval}秒")
    
    def stop(self):
        """停止定时清理任务"""
        if not self.is_running:
            return
        
        self.is_running = False
        self._stop_event.set()
        
        if self.cleanup_thread and self.cleanup_thread.is_alive():
            self.cleanup_thread.join(timeout=5)
        
        logger.info("数据库清理调度器已停止")
    
    def _cleanup_worker(self):
        """清理工作线程"""
        logger.info("数据库清理工作线程已启动")
        
        while not self._stop_event.is_set():
            try:
                # 执行清理
                self._perform_cleanup()
                
                # 等待下一次清理
                self._stop_event.wait(self.cleanup_interval)
                
            except Exception as e:
                logger.error(f"数据库清理任务执行失败: {str(e)}")
                # 发生错误时等待一段时间再继续
                self._stop_event.wait(min(self.cleanup_interval, 60))
        
        logger.info("数据库清理工作线程已退出")
    
    def _perform_cleanup(self):
        """执行清理操作"""
        if not settings.DB_AUTO_DISCONNECT:
            return
        
        try:
            # 记录清理前的连接数
            before_count = len(active_connections)
            
            # 执行清理
            cleanup_expired_connections()
            
            # 记录清理后的连接数
            after_count = len(active_connections)
            cleaned_count = before_count - after_count
            
            if cleaned_count > 0:
                logger.info(f"定时清理完成，清理了 {cleaned_count} 个过期连接")
            
            # 记录连接状态统计
            self._log_connection_statistics()
            
        except Exception as e:
            logger.error(f"执行数据库连接清理失败: {str(e)}")
    
    def _log_connection_statistics(self):
        """记录连接统计信息"""
        try:
            current_time = time.time()
            total_connections = 0
            active_count = 0
            idle_count = 0
            expired_count = 0
            
            with connection_lock:
                total_connections = len(active_connections)
                
                for conn_id, conn_info in active_connections.items():
                    idle_duration = current_time - conn_info['last_activity']
                    
                    if idle_duration > settings.DB_MAX_EXECUTION_TIME:
                        expired_count += 1
                    elif idle_duration < 5:  # 5秒内有活动认为是活跃
                        active_count += 1
                    else:
                        idle_count += 1
            
            # 只在有连接时记录统计信息
            if total_connections > 0:
                logger.debug(
                    f"数据库连接统计 - 总计: {total_connections}, "
                    f"活跃: {active_count}, 空闲: {idle_count}, 过期: {expired_count}"
                )
                
                # 如果有过期连接，记录调试信息而不是警告
                if expired_count > 0:
                    logger.debug(f"发现 {expired_count} 个过期连接，将在下次清理时处理")
                    
        except Exception as e:
            logger.error(f"记录连接统计信息失败: {str(e)}")
    
    def force_cleanup(self):
        """强制执行一次清理"""
        try:
            logger.info("执行强制数据库连接清理")
            self._perform_cleanup()
        except Exception as e:
            logger.error(f"强制清理失败: {str(e)}")
    
    def get_status(self) -> dict:
        """获取调度器状态"""
        return {
            'is_running': self.is_running,
            'cleanup_interval': self.cleanup_interval,
            'auto_disconnect_enabled': settings.DB_AUTO_DISCONNECT,
            'thread_alive': self.cleanup_thread.is_alive() if self.cleanup_thread else False
        }


# 全局调度器实例
_scheduler_instance: Optional[DatabaseCleanupScheduler] = None


def get_cleanup_scheduler() -> DatabaseCleanupScheduler:
    """获取全局清理调度器实例"""
    global _scheduler_instance
    if _scheduler_instance is None:
        _scheduler_instance = DatabaseCleanupScheduler()
    return _scheduler_instance


def start_cleanup_scheduler():
    """启动全局清理调度器"""
    scheduler = get_cleanup_scheduler()
    scheduler.start()


def stop_cleanup_scheduler():
    """停止全局清理调度器"""
    scheduler = get_cleanup_scheduler()
    scheduler.stop() 