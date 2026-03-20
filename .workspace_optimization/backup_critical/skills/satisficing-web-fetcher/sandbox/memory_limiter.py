#!/usr/bin/env python3
"""
内存限制器

功能：
1. 监控进程内存使用
2. 超过限制时自动终止
3. 防止内存泄漏导致的系统不稳定
"""

import psutil
import threading
import time
import signal
import os
from typing import Optional
from contextlib import ContextDecorator


class MemoryLimiter(ContextDecorator):
    """
    内存限制器上下文管理器
    
    使用示例：
        with MemoryLimiter(max_mb=2048):
            # 浏览器操作
            pass
    """
    
    def __init__(self, max_mb: int = 2048, check_interval: float = 1.0):
        """
        Args:
            max_mb: 最大内存限制(MB)
            check_interval: 检查间隔(秒)
        """
        self.max_mb = max_mb
        self.check_interval = check_interval
        self._monitor_thread: Optional[threading.Thread] = None
        self._should_stop = threading.Event()
        self._current_process = psutil.Process(os.getpid())
    
    def __enter__(self):
        """启动内存监控"""
        self._should_stop.clear()
        self._monitor_thread = threading.Thread(target=self._monitor_memory)
        self._monitor_thread.daemon = True
        self._monitor_thread.start()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """停止内存监控"""
        self._should_stop.set()
        if self._monitor_thread:
            self._monitor_thread.join(timeout=2)
    
    def _monitor_memory(self):
        """监控内存使用"""
        while not self._should_stop.is_set():
            try:
                # 获取当前进程及其子进程的内存使用
                total_mb = self._get_total_memory_mb()
                
                if total_mb > self.max_mb:
                    self._handle_memory_exceeded(total_mb)
                    
            except Exception:
                pass
            
            time.sleep(self.check_interval)
    
    def _get_total_memory_mb(self) -> float:
        """获取进程及其子进程的总内存使用(MB)"""
        total = 0
        try:
            # 当前进程
            total += self._current_process.memory_info().rss / 1024 / 1024
            
            # 子进程
            for child in self._current_process.children(recursive=True):
                try:
                    total += child.memory_info().rss / 1024 / 1024
                except psutil.NoSuchProcess:
                    pass
        except psutil.NoSuchProcess:
            pass
        
        return total
    
    def _handle_memory_exceeded(self, current_mb: float):
        """处理内存超限"""
        print(f"[MemoryLimiter] Memory limit exceeded: {current_mb:.0f}MB > {self.max_mb}MB")
        
        # 尝试终止浏览器子进程
        try:
            for child in self._current_process.children(recursive=True):
                try:
                    # 优先终止chromium/chrome进程
                    if 'chrome' in child.name().lower() or 'chromium' in child.name().lower():
                        child.terminate()
                        child.wait(timeout=3)
                except:
                    try:
                        child.kill()
                    except:
                        pass
        except:
            pass
        
        # 如果仍然超限，强制退出
        current_mb = self._get_total_memory_mb()
        if current_mb > self.max_mb * 1.2:  # 允许20%的缓冲
            print(f"[MemoryLimiter] Force terminating due to memory pressure")
            os.kill(os.getpid(), signal.SIGTERM)


def check_memory_limit(pid: Optional[int] = None, max_mb: int = 2048) -> bool:
    """
    检查指定进程的内存使用是否超限
    
    Args:
        pid: 进程ID，默认为当前进程
        max_mb: 最大内存限制(MB)
        
    Returns:
        bool: 是否超限
    """
    if pid is None:
        pid = os.getpid()
    
    try:
        proc = psutil.Process(pid)
        memory_mb = proc.memory_info().rss / 1024 / 1024
        
        # 包含子进程
        for child in proc.children(recursive=True):
            try:
                memory_mb += child.memory_info().rss / 1024 / 1024
            except psutil.NoSuchProcess:
                pass
        
        return memory_mb > max_mb
    except psutil.NoSuchProcess:
        return False
