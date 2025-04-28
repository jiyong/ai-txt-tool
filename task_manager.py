import os
import redis
import logging
from typing import Optional, Dict, List
from enum import Enum
import asyncio
from datetime import datetime

class TaskStatus(Enum):
    DOING = "doing"
    SUCCESS = "success"
    FAIL = "fail"

class TaskManager:
    def __init__(self):
        self.redis_host = os.getenv('REDIS_HOST', 'localhost')
        self.redis_port = int(os.getenv('REDIS_PORT', 6379))
        self.redis_db = int(os.getenv('REDIS_DB', 0))
        self.redis_password = os.getenv('REDIS_PASSWORD')
        
        # 创建Redis连接
        self.redis = redis.Redis(
            host=self.redis_host,
            port=self.redis_port,
            db=self.redis_db,
            password=self.redis_password,
            decode_responses=True
        )
        
        # 测试Redis连接
        try:
            self.redis.ping()
            logging.info("Redis连接成功")
        except redis.AuthenticationError:
            logging.error("Redis认证失败，请检查密码配置")
            raise
        except redis.ConnectionError:
            logging.error("Redis连接失败，请检查主机和端口配置")
            raise
        except Exception as e:
            logging.error(f"Redis连接出错: {str(e)}")
            raise
            
        self.lock = asyncio.Lock()
        
    def _get_task_key(self, product_code: str, task_type: str) -> str:
        """生成任务状态键"""
        return f"book-processor::{product_code}::{task_type}"
        
    def _get_file_lock_key(self, product_code: str) -> str:
        """生成文件锁键"""
        return f"book-processor::{product_code}::file-lock"
        
    async def update_task_status(self, product_code: str, task_type: str, status: TaskStatus, message: str = "") -> None:
        """更新任务状态"""
        key = self._get_task_key(product_code, task_type)
        data = {
            "status": status.value,
            "message": message,
            "updated_at": datetime.now().isoformat()
        }
        self.redis.hmset(key, data)
        
    async def get_task_status(self, product_code: str, task_type: str) -> Dict:
        """获取任务状态"""
        key = self._get_task_key(product_code, task_type)
        data = self.redis.hgetall(key)
        return data if data else {"status": "not_found"}
        
    async def acquire_file_lock(self, product_code: str) -> bool:
        """获取文件锁"""
        key = self._get_file_lock_key(product_code)
        return bool(self.redis.set(key, "1", nx=True, ex=3600))  # 1小时过期
        
    async def release_file_lock(self, product_code: str) -> None:
        """释放文件锁"""
        key = self._get_file_lock_key(product_code)
        self.redis.delete(key)
        
    async def check_all_tasks_completed(self, product_code: str, task_types: List[str]) -> bool:
        """检查所有任务是否完成"""
        for task_type in task_types:
            status = await self.get_task_status(product_code, task_type)
            if status.get("status") not in [TaskStatus.SUCCESS.value, TaskStatus.FAIL.value]:
                return False
        return True
        
    async def wait_for_tasks_completion(self, product_code: str, task_types: List[str], timeout: int = 3600) -> bool:
        """等待所有任务完成"""
        start_time = datetime.now()
        while (datetime.now() - start_time).seconds < timeout:
            if await self.check_all_tasks_completed(product_code, task_types):
                return True
            await asyncio.sleep(1)
        return False

# 创建全局任务管理器实例
task_manager = TaskManager() 