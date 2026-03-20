#!/usr/bin/env python3
"""
浏览器进程控制器

负责：
1. 浏览器进程的启动和停止
2. 进程隔离
3. 资源清理
"""

import subprocess
import signal
import os
import psutil
from typing import Optional, List
from pathlib import Path


class BrowserController:
    """浏览器进程控制器"""
    
    def __init__(self):
        self._processes: List[subprocess.Popen] = []
        self._cleanup_hooks = []
    
    def start_browser(self, 
                      headless: bool = True,
                      extra_args: Optional[List[str]] = None) -> subprocess.Popen:
        """
        启动浏览器进程
        
        Args:
            headless: 是否无头模式
            extra_args: 额外的启动参数
            
        Returns:
            subprocess.Popen: 浏览器进程
        """
        # 实际实现应该使用playwright的底层控制
        # 这里提供控制接口的框架
        pass
    
    def kill_all(self):
        """强制终止所有浏览器进程"""
        for proc in self._processes:
            try:
                proc.terminate()
                proc.wait(timeout=5)
            except:
                try:
                    proc.kill()
                except:
                    pass
        
        # 清理僵尸进程
        self._cleanup_zombies()
    
    def _cleanup_zombies(self):
        """清理僵尸进程"""
        for proc in psutil.process_iter(['pid', 'name']):
            try:
                if 'chromium' in proc.info['name'].lower() or 'chrome' in proc.info['name'].lower():
                    # 检查是否是孤儿进程
                    if proc.parent() is None or proc.parent().pid == 1:
                        proc.terminate()
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                pass
    
    def register_cleanup_hook(self, hook):
        """注册清理钩子"""
        self._cleanup_hooks.append(hook)
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.kill_all()
        for hook in self._cleanup_hooks:
            try:
                hook()
            except:
                pass
