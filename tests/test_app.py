"""
Unit tests for GitHub Trending App
"""

import unittest
import json
from pathlib import Path
from datetime import datetime, timedelta
from unittest.mock import patch, MagicMock

# Add parent directory to path
import sys
sys.path.insert(0, str(Path(__file__).parent.parent))

from cache import CacheManager, CacheEntry
from i18n import I18n, TRANSLATIONS
from scraper import TrendingRepo
from scheduler import Scheduler, ScheduleType


class TestCacheManager(unittest.TestCase):
    """测试缓存管理器"""
    
    def setUp(self):
        self.cache_dir = Path(__file__).parent / "test_cache"
        self.cache = CacheManager(self.cache_dir)
        self.cache.clear()
    
    def tearDown(self):
        self.cache.clear()
        if self.cache_dir.exists():
            self.cache_dir.rmdir()
    
    def test_generate_key(self):
        """测试缓存键生成"""
        key1 = self.cache._generate_key("weekly", None)
        key2 = self.cache._generate_key("weekly", None)
        key3 = self.cache._generate_key("daily", None)
        
        self.assertEqual(key1, key2)  # 相同参数应生成相同键
        self.assertNotEqual(key1, key3)  # 不同参数应生成不同键
    
    def test_set_and_get(self):
        """测试缓存设置和获取"""
        test_data = [{"name": "test", "stars": 100}]
        
        # 设置缓存
        result = self.cache.set("weekly", None, test_data)
        self.assertTrue(result)
        
        # 获取缓存
        cached = self.cache.get("weekly", None)
        self.assertIsNotNone(cached)
        self.assertEqual(len(cached), 1)
        self.assertEqual(cached[0]["name"], "test")
    
    def test_cache_expiry(self):
        """测试缓存过期"""
        test_data = [{"name": "test"}]
        
        # 设置缓存
        self.cache.set("daily", "python", test_data)
        
        # 手动修改过期时间
        key = self.cache._generate_key("daily", "python")
        cache_file = self.cache_dir / f"{key}.json"
        
        with open(cache_file, 'r') as f:
            entry = CacheEntry(**json.load(f))
        
        # 修改为已过期
        entry.expires_at = (datetime.now() - timedelta(hours=1)).isoformat()
        
        with open(cache_file, 'w') as f:
            json.dump(vars(entry), f)
        
        # 获取应返回 None
        cached = self.cache.get("daily", "python")
        self.assertIsNone(cached)
    
    def test_clear_cache(self):
        """测试清除缓存"""
        self.cache.set("weekly", None, [{"test": 1}])
        self.cache.set("daily", "python", [{"test": 2}])
        
        count = self.cache.clear()
        self.assertEqual(count, 2)
        
        # 确认已清除
        cached = self.cache.get("weekly", None)
        self.assertIsNone(cached)


class TestI18n(unittest.TestCase):
    """测试国际化模块"""
    
    def setUp(self):
        self.i18n = I18n()
    
    def test_default_language(self):
        """测试默认语言"""
        self.assertEqual(self.i18n.get_language(), "zh")
    
    def test_set_language(self):
        """测试切换语言"""
        self.i18n.set_language("en")
        self.assertEqual(self.i18n.get_language(), "en")
        
        self.i18n.set_language("zh")
        self.assertEqual(self.i18n.get_language(), "zh")
    
    def test_invalid_language(self):
        """测试无效语言"""
        original = self.i18n.get_language()
        self.i18n.set_language("fr")  # 无效语言
        self.assertEqual(self.i18n.get_language(), original)  # 应保持不变
    
    def test_translation(self):
        """测试翻译功能"""
        self.i18n.set_language("zh")
        self.assertEqual(self.i18n.t("app_title"), "GitHub Trending 周报生成器")
        
        self.i18n.set_language("en")
        self.assertEqual(self.i18n.t("app_title"), "GitHub Trending Weekly Report Generator")
    
    def test_missing_key(self):
        """测试缺失的翻译键"""
        result = self.i18n.t("nonexistent_key")
        self.assertEqual(result, "nonexistent_key")
    
    def test_language_change_callback(self):
        """测试语言切换回调"""
        callback_called = [False]
        
        def callback():
            callback_called[0] = True
        
        self.i18n.on_language_change(callback)
        self.i18n.set_language("en")
        
        self.assertTrue(callback_called[0])


class TestTrendingRepo(unittest.TestCase):
    """测试 TrendingRepo 数据类"""
    
    def test_creation(self):
        """测试创建 TrendingRepo"""
        repo = TrendingRepo(
            rank=1,
            name="test-repo",
            full_name="user/test-repo",
            url="https://github.com/user/test-repo",
            description="A test repository",
            language="Python",
            language_color="#3572A5",
            stars_total=1000,
            stars_today=100,
            forks=50,
            built_by=["user1", "user2"]
        )
        
        self.assertEqual(repo.rank, 1)
        self.assertEqual(repo.name, "test-repo")
        self.assertEqual(repo.stars_today, 100)
        self.assertEqual(repo.topics, [])
    
    def test_to_dict(self):
        """测试转换为字典"""
        repo = TrendingRepo(
            rank=1,
            name="test",
            full_name="user/test",
            url="https://github.com/user/test",
            description="Test",
            language="Python",
            language_color="#3572A5",
            stars_total=100,
            stars_today=10,
            forks=5,
            built_by=[]
        )
        
        d = repo.to_dict()
        self.assertIsInstance(d, dict)
        self.assertEqual(d["name"], "test")
        self.assertEqual(d["stars_total"], 100)
    
    def test_from_dict(self):
        """测试从字典创建"""
        data = {
            'rank': 1,
            'name': 'test',
            'full_name': 'user/test',
            'url': 'https://github.com/user/test',
            'description': 'Test',
            'language': 'Python',
            'language_color': '#3572A5',
            'stars_total': 100,
            'stars_today': 10,
            'forks': 5,
            'built_by': [],
            'topics': [],
            'ai_summary': ''
        }
        
        repo = TrendingRepo.from_dict(data)
        self.assertEqual(repo.name, 'test')
        self.assertEqual(repo.stars_total, 100)


class TestScheduler(unittest.TestCase):
    """测试调度器"""
    
    def setUp(self):
        self.scheduler = Scheduler()
    
    def test_add_task(self):
        """测试添加任务"""
        def dummy_func():
            pass
        
        task_id = self.scheduler.add_task(
            name="test_task",
            func=dummy_func,
            schedule_type=ScheduleType.DAILY,
            time="09:00"
        )
        
        self.assertIsNotNone(task_id)
        tasks = self.scheduler.get_tasks()
        self.assertEqual(len(tasks), 1)
        self.assertEqual(tasks[0]["name"], "test_task")
    
    def test_remove_task(self):
        """测试移除任务"""
        def dummy_func():
            pass
        
        task_id = self.scheduler.add_task(
            name="test_task",
            func=dummy_func,
            schedule_type=ScheduleType.WEEKLY,
            time="10:00",
            day_of_week="monday"
        )
        
        result = self.scheduler.remove_task(task_id)
        self.assertTrue(result)
        self.assertEqual(len(self.scheduler.get_tasks()), 0)
    
    def test_next_run_daily(self):
        """测试每日任务的下次执行时间"""
        def dummy_func():
            pass
        
        task_id = self.scheduler.add_task(
            name="daily_task",
            func=dummy_func,
            schedule_type=ScheduleType.DAILY,
            time="09:00"
        )
        
        task = self.scheduler.get_tasks()[0]
        self.assertIsNotNone(task["next_run"])
        self.assertEqual(task["next_run"].hour, 9)
        self.assertEqual(task["next_run"].minute, 0)


if __name__ == "__main__":
    unittest.main(verbosity=2)
