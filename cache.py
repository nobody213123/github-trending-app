"""
Cache module for GitHub Trending App
Provides caching to avoid duplicate scraping
"""

import json
import hashlib
from pathlib import Path
from datetime import datetime, timedelta
from typing import Optional, List
from dataclasses import dataclass, asdict

from config import CACHE_DIR, CACHE_EXPIRY_HOURS


@dataclass
class CacheEntry:
    """Cache entry data"""
    key: str
    data: List[dict]
    created_at: str
    expires_at: str
    time_range: str
    language: Optional[str]


class CacheManager:
    """Manages caching for scraped data"""
    
    def __init__(self, cache_dir: Path = CACHE_DIR):
        self.cache_dir = cache_dir
        self.cache_dir.mkdir(parents=True, exist_ok=True)
    
    def _generate_key(self, time_range: str, language: Optional[str]) -> str:
        """Generate cache key from parameters"""
        key_data = f"{time_range}:{language or 'all'}"
        return hashlib.md5(key_data.encode()).hexdigest()
    
    def get(self, time_range: str, language: Optional[str] = None) -> Optional[List[dict]]:
        """
        Get cached data if available and not expired
        Returns list of repo dicts or None
        """
        key = self._generate_key(time_range, language)
        cache_file = self.cache_dir / f"{key}.json"
        
        if not cache_file.exists():
            return None
        
        try:
            with open(cache_file, 'r', encoding='utf-8') as f:
                entry = CacheEntry(**json.load(f))
            
            # Check expiry
            expires_at = datetime.fromisoformat(entry.expires_at)
            if datetime.now() > expires_at:
                # Cache expired, delete it
                cache_file.unlink()
                return None
            
            # Convert back to list of dicts
            return entry.data
            
        except Exception as e:
            print(f"Cache read error: {e}")
            return None
    
    def set(self, time_range: str, language: Optional[str], data: List[dict]) -> bool:
        """
        Store data in cache
        Returns True if successful
        """
        key = self._generate_key(time_range, language)
        cache_file = self.cache_dir / f"{key}.json"
        
        try:
            now = datetime.now()
            expires_at = now + timedelta(hours=CACHE_EXPIRY_HOURS)
            
            entry = CacheEntry(
                key=key,
                data=data,
                created_at=now.isoformat(),
                expires_at=expires_at.isoformat(),
                time_range=time_range,
                language=language
            )
            
            with open(cache_file, 'w', encoding='utf-8') as f:
                json.dump(asdict(f if False else entry), f, ensure_ascii=False, indent=2)
            
            return True
            
        except Exception as e:
            print(f"Cache write error: {e}")
            return False
    
    def clear(self) -> int:
        """
        Clear all cache files
        Returns number of files deleted
        """
        count = 0
        for cache_file in self.cache_dir.glob("*.json"):
            try:
                cache_file.unlink()
                count += 1
            except Exception:
                pass
        return count
    
    def get_cache_info(self) -> List[dict]:
        """
        Get information about all cached entries
        """
        info = []
        for cache_file in self.cache_dir.glob("*.json"):
            try:
                with open(cache_file, 'r', encoding='utf-8') as f:
                    entry = CacheEntry(**json.load(f))
                
                expires_at = datetime.fromisoformat(entry.expires_at)
                is_expired = datetime.now() > expires_at
                
                info.append({
                    "time_range": entry.time_range,
                    "language": entry.language,
                    "items": len(entry.data),
                    "created_at": entry.created_at,
                    "expires_at": entry.expires_at,
                    "is_expired": is_expired
                })
            except Exception:
                pass
        
        return info


# Singleton instance
cache = CacheManager()
