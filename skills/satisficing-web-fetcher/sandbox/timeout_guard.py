#!/usr/bin/env python3
"""
超时守护

功能：
1. 监控操作执行时间
2. 超时时强制终止
3. 防止长时间挂起
"""

import signal
import threading
import time
from typing import Optional, Type, Callable
from contextlib import ContextDecorator
from types import FrameType


class TimeoutError(Exception):
    """超时异常"""
    pass


class TimeoutGuard(ContextDecorator):
    """
    超时守护上下文管理器
    
    使用示例：
        with TimeoutGuard(timeout=30):
            # 可能耗时的操作
            result = long_running_operation()
    """
    
    def __init__(self, timeout: float, callback: Optional[Callable] = None):
        """
        Args:
            timeout: 超时时间(秒)
            callback: 超时时的回调函数
        """
        self.timeout = timeout
        self.callback = callback
        self._original_handler = None
        self._timer: Optional[threading.Timer] = None
        self._timed_out = threading.Event()
    
    def __enter__(self):
        """启动超时监控"""
        self._timed_out.clear()
        
        # 使用信号处理(仅主线程)或线程计时器
        if threading.current_thread() is threading.main_thread():
            self._original_handler = signal.signal(signal.SIGALRM, self._signal_handler)
            signal.alarm(int(self.timeout))
        else:
            self._timer = threading.Timer(self.timeout, self._timeout_handler)
            self._timer.start()
        
        return self
    
    def __exit__(self, exc_type: Optional[Type[BaseException]], 
                 exc_val: Optional[BaseException], 
                 exc_tb: Optional[FrameType]) -> bool:
        """停止超时监控"""
        # 取消超时
        if threading.current_thread() is threading.main_thread():
            signal.alarm(0)
            if self._original_handler:
                signal.signal(signal.SIGALRM, self._original_handler)
        else:
            if self._timer:
                self._timer.cancel()
        
        # 如果是超时异常，可以选择抑制或转换
        if exc_type is TimeoutError:
            return False  # 不抑制异常
        
        return False
    
    def _signal_handler(self, signum: int, frame: Optional[FrameType]):
        """信号处理函数"""
        self._timed_out.set()
        if self.callback:
            self.callback()
        raise TimeoutError(f"Operation timed out after {self.timeout} seconds")
    
    def _timeout_handler(self):
        """线程超时处理函数"""
        self._timed_out.set()
        if self.callback:
            self.callback()
        # 在线程中无法直接抛出异常到主线程
        # 这里设置标志，主线程需要主动检查
    
    def is_timed_out(self) -> bool:
        """检查是否已超时"""
        return self._timed_out.is_set()


def with_timeout(timeout: float, default_return: Optional[Any] = None):
    """
    函数装饰器：为函数添加超时控制
    
    使用示例：
        @with_timeout(timeout=30, default_return=None)
        def fetch_data():
            # 可能耗时的操作
            return data
    """
    def decorator(func: Callable) -> Callable:
        def wrapper(*args, **kwargs):
            result = [default_return]
            exception = [None]
            
            def target():
                try:
                    result[0] = func(*args, **kwargs)
                except Exception as e:
                    exception[0] = e
            
            thread = threading.Thread(target=target)
            thread.daemon = True
            thread.start()
            thread.join(timeout)
            
            if thread.is_alive():
                raise TimeoutError(f"Function {func.__name__} timed out after {timeout} seconds")
            
            if exception[0]:
                raise exception[0]
            
            return result[0]
        
        return wrapper
    return decorator
