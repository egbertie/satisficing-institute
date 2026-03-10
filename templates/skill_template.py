#!/usr/bin/env python3
"""
Skill开发模板 V1.0
33位AI小伙伴统一使用此模板开发Skill

使用方法:
1. 复制此文件到 skills/{your-skill-name}/
2. 替换所有 {占位符}
3. 实现核心功能
4. 添加测试用例
"""

import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass, asdict

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


@dataclass
class SkillResult:
    """Skill执行结果标准格式"""
    success: bool
    data: Any = None
    error: str = ""
    metadata: Dict = None
    timestamp: str = None
    
    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}
        if self.timestamp is None:
            self.timestamp = datetime.now().isoformat()
    
    def to_dict(self) -> Dict:
        return asdict(self)


class {SkillClassName}:
    """
    {Skill名称} V1.0
    
    一句话描述: {在此填写Skill的核心功能描述}
    
    核心功能:
    1. {功能1描述}
    2. {功能2描述}
    3. {功能3描述}
    
    作者: {AI小伙伴姓名} ({AI-ID})
    创建时间: {YYYY-MM-DD}
    版本: 1.0.0
    """
    
    VERSION = "1.0.0"
    SKILL_NAME = "{skill-name}"
    
    def __init__(self, workspace_path: str = "/root/.openclaw/workspace"):
        """
        初始化Skill
        
        Args:
            workspace_path: 工作空间路径
        """
        self.workspace = Path(workspace_path)
        self.skill_dir = self.workspace / "skills" / self.SKILL_NAME
        self.config_file = self.skill_dir / "config.json"
        self.data_dir = self.workspace / "data" / self.SKILL_NAME
        self.cache_dir = self.workspace / "cache" / self.SKILL_NAME
        
        # 创建必要目录
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        
        # 加载配置
        self.config = self._load_config()
        
        # 初始化统计
        self.stats = self._init_stats()
        
        logger.info(f"{self.SKILL_NAME} V{self.VERSION} 初始化完成")
    
    def _load_config(self) -> Dict:
        """
        加载配置文件
        
        Returns:
            配置字典
        """
        default_config = {
            "version": self.VERSION,
            "enabled": True,
            "debug": False,
            # 在此添加默认配置项
            "param1": "default_value",
            "param2": 100,
        }
        
        if self.config_file.exists():
            try:
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    user_config = json.load(f)
                    default_config.update(user_config)
                    logger.info("已加载用户配置")
            except Exception as e:
                logger.warning(f"加载配置文件失败: {e}, 使用默认配置")
        else:
            # 创建默认配置文件
            self._save_config(default_config)
            logger.info("已创建默认配置文件")
        
        return default_config
    
    def _save_config(self, config: Dict):
        """保存配置到文件"""
        try:
            self.skill_dir.mkdir(parents=True, exist_ok=True)
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=2, ensure_ascii=False)
        except Exception as e:
            logger.error(f"保存配置失败: {e}")
    
    def _init_stats(self) -> Dict:
        """初始化统计信息"""
        return {
            "total_processed": 0,
            "successful": 0,
            "failed": 0,
            "start_time": datetime.now().isoformat(),
        }
    
    def process(self, input_data: Dict) -> SkillResult:
        """
        主处理函数 - 实现Skill核心逻辑
        
        Args:
            input_data: 输入数据，格式如下:
                {
                    "field1": "value1",
                    "field2": "value2",
                    # 根据具体Skill定义
                }
        
        Returns:
            SkillResult: 标准结果格式
        """
        try:
            logger.info(f"开始处理: {input_data}")
            self.stats["total_processed"] += 1
            
            # ===== 在此处实现核心逻辑 =====
            
            # 1. 输入验证
            if not self._validate_input(input_data):
                return SkillResult(
                    success=False,
                    error="输入数据验证失败"
                )
            
            # 2. 预处理
            processed_data = self._preprocess(input_data)
            
            # 3. 核心处理 (在此实现主要功能)
            result_data = self._core_process(processed_data)
            
            # 4. 后处理
            final_data = self._postprocess(result_data)
            
            # ================================
            
            self.stats["successful"] += 1
            
            logger.info("处理完成")
            
            return SkillResult(
                success=True,
                data=final_data,
                metadata={
                    "processed_at": datetime.now().isoformat(),
                    "version": self.VERSION,
                    # 添加其他元数据
                }
            )
            
        except Exception as e:
            logger.error(f"处理失败: {e}", exc_info=True)
            self.stats["failed"] += 1
            
            return SkillResult(
                success=False,
                error=str(e),
                metadata={
                    "error_type": type(e).__name__,
                    "failed_at": datetime.now().isoformat(),
                }
            )
    
    def _validate_input(self, input_data: Dict) -> bool:
        """
        验证输入数据
        
        Args:
            input_data: 输入数据
        
        Returns:
            是否通过验证
        """
        # 实现输入验证逻辑
        if not isinstance(input_data, dict):
            logger.error("输入必须是字典类型")
            return False
        
        # 检查必需字段
        # required_fields = ["field1", "field2"]
        # for field in required_fields:
        #     if field not in input_data:
        #         logger.error(f"缺少必需字段: {field}")
        #         return False
        
        return True
    
    def _preprocess(self, data: Dict) -> Dict:
        """
        数据预处理
        
        Args:
            data: 原始数据
        
        Returns:
            预处理后的数据
        """
        # 实现预处理逻辑
        return data
    
    def _core_process(self, data: Dict) -> Any:
        """
        核心处理逻辑 - 必须实现
        
        Args:
            data: 预处理后的数据
        
        Returns:
            处理结果
        """
        # ===== 在此处实现核心功能 =====
        
        # 示例: 简单返回处理后的数据
        result = {
            "input": data,
            "processed": True,
            "timestamp": datetime.now().isoformat(),
        }
        
        return result
    
    def _postprocess(self, data: Any) -> Any:
        """
        结果后处理
        
        Args:
            data: 核心处理结果
        
        Returns:
            后处理后的结果
        """
        # 实现后处理逻辑
        return data
    
    def batch_process(self, input_list: List[Dict]) -> List[SkillResult]:
        """
        批量处理
        
        Args:
            input_list: 输入数据列表
        
        Returns:
            结果列表
        """
        logger.info(f"开始批量处理: {len(input_list)} 条数据")
        
        results = []
        for i, input_data in enumerate(input_list, 1):
            logger.info(f"处理 [{i}/{len(input_list)}]")
            result = self.process(input_data)
            results.append(result)
        
        logger.info(f"批量处理完成: {len(results)} 条")
        return results
    
    def get_stats(self) -> Dict:
        """
        获取统计信息
        
        Returns:
            统计字典
        """
        stats = self.stats.copy()
        stats["success_rate"] = (
            stats["successful"] / max(stats["total_processed"], 1) * 100
        )
        stats["uptime"] = (
            datetime.now() - datetime.fromisoformat(stats["start_time"])
        ).total_seconds()
        return stats
    
    def health_check(self) -> Dict:
        """
        健康检查
        
        Returns:
            健康状态
        """
        return {
            "status": "healthy",
            "skill_name": self.SKILL_NAME,
            "version": self.VERSION,
            "config_valid": bool(self.config),
            "directories": {
                "skill_dir": self.skill_dir.exists(),
                "data_dir": self.data_dir.exists(),
                "cache_dir": self.cache_dir.exists(),
            },
            "timestamp": datetime.now().isoformat(),
        }
    
    def export_result(self, result: SkillResult, filepath: str):
        """
        导出结果到文件
        
        Args:
            result: Skill结果
            filepath: 输出文件路径
        """
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(result.to_dict(), f, indent=2, ensure_ascii=False)
            logger.info(f"结果已导出: {filepath}")
        except Exception as e:
            logger.error(f"导出结果失败: {e}")


# ============================================================================
# 测试代码
# ============================================================================

def test_basic():
    """基础功能测试"""
    print("="*70)
    print("测试 {Skill名称} 基础功能")
    print("="*70)
    
    # 创建实例
    skill = {SkillClassName}()
    
    # 健康检查
    health = skill.health_check()
    print(f"\n健康检查: {health['status']}")
    
    # 测试处理
    test_input = {
        "test_field": "test_value",
        # 添加测试数据
    }
    
    result = skill.process(test_input)
    
    print(f"\n处理结果:")
    print(f"  成功: {result.success}")
    print(f"  数据: {result.data}")
    if result.error:
        print(f"  错误: {result.error}")
    
    # 统计
    print(f"\n统计:")
    stats = skill.get_stats()
    for key, value in stats.items():
        print(f"  {key}: {value}")
    
    print("\n测试完成!")


def test_batch():
    """批量处理测试"""
    print("="*70)
    print("测试 {Skill名称} 批量处理")
    print("="*70)
    
    skill = {SkillClassName}()
    
    test_inputs = [
        {"field": f"value_{i}"}
        for i in range(5)
    ]
    
    results = skill.batch_process(test_inputs)
    
    print(f"\n批量处理完成: {len(results)} 条")
    success_count = sum(1 for r in results if r.success)
    print(f"成功: {success_count}/{len(results)}")


if __name__ == "__main__":
    # 运行测试
    test_basic()
    print("\n")
    test_batch()
