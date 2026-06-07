"""
内置定时任务调度器
支持每日/每周自动执行
"""

import threading
import time as time_module
from datetime import datetime, timedelta
from typing import Callable, Optional
from dataclasses import dataclass
from enum import Enum

from config import SCHEDULE_TIME, SCHEDULE_DAY


class ScheduleType(Enum):
    """调度类型"""
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"


@dataclass
class ScheduleConfig:
    """调度配置"""
    schedule_type: ScheduleType
    time: str  # HH:MM format
    day_of_week: Optional[str] = None  # For weekly: monday, tuesday, etc.
    day_of_month: Optional[int] = None  # For monthly: 1-31
    enabled: bool = True


class Scheduler:
    """内置定时任务调度器"""
    
    def __init__(self):
        self._tasks = []
        self._running = False
        self._thread = None
        self._callbacks = []
    
    def add_task(self, 
                 name: str,
                 func: Callable,
                 schedule_type: ScheduleType,
                 time: str = SCHEDULE_TIME,
                 day_of_week: str = None,
                 day_of_month: int = None) -> str:
        """
        添加定时任务
        
        Args:
            name: 任务名称
            func: 要执行的函数
            schedule_type: 调度类型
            time: 执行时间 (HH:MM)
            day_of_week: 每周执行日 (monday, tuesday, etc.)
            day_of_month: 每月执行日 (1-31)
        
        Returns:
            任务 ID
        """
        task_id = f"{name}_{int(time_module.time() * 1000)}"
        
        config = ScheduleConfig(
            schedule_type=schedule_type,
            time=time,
            day_of_week=day_of_week,
            day_of_month=day_of_month
        )
        
        task = {
            'id': task_id,
            'name': name,
            'func': func,
            'config': config,
            'last_run': None,
            'next_run': self._calculate_next_run(config)
        }
        
        self._tasks.append(task)
        print(f"✅ 已添加定时任务: {name} ({schedule_type.value} at {time})")
        
        return task_id
    
    def remove_task(self, task_id: str) -> bool:
        """移除定时任务"""
        for i, task in enumerate(self._tasks):
            if task['id'] == task_id:
                removed = self._tasks.pop(i)
                print(f"🗑️ 已移除定时任务: {removed['name']}")
                return True
        return False
    
    def get_tasks(self) -> list:
        """获取所有任务列表"""
        return [{
            'id': t['id'],
            'name': t['name'],
            'type': t['config'].schedule_type.value,
            'time': t['config'].time,
            'enabled': t['config'].enabled,
            'last_run': t['last_run'],
            'next_run': t['next_run']
        } for t in self._tasks]
    
    def start(self):
        """启动调度器"""
        if self._running:
            print("⚠️ 调度器已在运行")
            return
        
        self._running = True
        self._thread = threading.Thread(target=self._run_loop, daemon=True)
        self._thread.start()
        print("🚀 调度器已启动")
    
    def stop(self):
        """停止调度器"""
        self._running = False
        if self._thread:
            self._thread.join(timeout=5)
        print("⏹️ 调度器已停止")
    
    def _run_loop(self):
        """调度器主循环"""
        while self._running:
            now = datetime.now()
            
            for task in self._tasks:
                if not task['config'].enabled:
                    continue
                
                if task['next_run'] and now >= task['next_run']:
                    self._execute_task(task)
                    task['last_run'] = now
                    task['next_run'] = self._calculate_next_run(task['config'])
            
            # 每分钟检查一次
            time_module.sleep(60)
    
    def _execute_task(self, task: dict):
        """执行任务"""
        print(f"⏰ 执行定时任务: {task['name']}")
        try:
            task['func']()
            print(f"✅ 任务完成: {task['name']}")
        except Exception as e:
            print(f"❌ 任务失败: {task['name']} - {e}")
    
    def _calculate_next_run(self, config: ScheduleConfig) -> Optional[datetime]:
        """计算下次执行时间"""
        now = datetime.now()
        hour, minute = map(int, config.time.split(':'))
        
        if config.schedule_type == ScheduleType.DAILY:
            # 每天执行
            next_run = now.replace(hour=hour, minute=minute, second=0, microsecond=0)
            if next_run <= now:
                next_run += timedelta(days=1)
            return next_run
        
        elif config.schedule_type == ScheduleType.WEEKLY:
            # 每周执行
            days = {
                'monday': 0, 'tuesday': 1, 'wednesday': 2,
                'thursday': 3, 'friday': 4, 'saturday': 5, 'sunday': 6
            }
            target_day = days.get(config.day_of_week.lower(), 0)
            days_ahead = target_day - now.weekday()
            if days_ahead < 0:
                days_ahead += 7
            next_run = now + timedelta(days=days_ahead)
            next_run = next_run.replace(hour=hour, minute=minute, second=0, microsecond=0)
            if next_run <= now:
                next_run += timedelta(weeks=1)
            return next_run
        
        elif config.schedule_type == ScheduleType.MONTHLY:
            # 每月执行
            target_day = config.day_of_month or 1
            if now.day >= target_day:
                # 下个月
                if now.month == 12:
                    next_run = now.replace(year=now.year + 1, month=1, day=target_day,
                                          hour=hour, minute=minute, second=0, microsecond=0)
                else:
                    next_run = now.replace(month=now.month + 1, day=target_day,
                                          hour=hour, minute=minute, second=0, microsecond=0)
            else:
                next_run = now.replace(day=target_day, hour=hour, minute=minute,
                                      second=0, microsecond=0)
            return next_run
        
        return None
    
    def on_task_complete(self, callback: Callable):
        """注册任务完成回调"""
        self._callbacks.append(callback)


# Singleton instance
scheduler = Scheduler()
