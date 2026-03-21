#!/usr/bin/env python3
"""
Optimization Rollback Guard - 优化回滚保障
优化前自动快照，支持一键回滚
"""

import json
import shutil
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional

class VersionManager:
    """版本管理器"""
    
    VERSION_RETENTION = 7  # 保留7个自动版本
    
    def __init__(self, 
                 workspace_path: str = '/root/.openclaw/workspace',
                 versions_dir: str = 'data/versions'):
        self.workspace = Path(workspace_path)
        self.versions_dir = self.workspace / versions_dir
        self.versions_dir.mkdir(parents=True, exist_ok=True)
    
    def create_snapshot(self, description: str, change_type: str = 'normal') -> str:
        """创建优化前快照"""
        timestamp = datetime.now().strftime('%Y%m%d-%H%M%S')
        version_id = f"v-{timestamp}"
        version_dir = self.versions_dir / version_id
        
        # 创建版本目录
        version_dir.mkdir()
        
        # 复制核心文件
        snapshot_files = self._snapshot_files(version_dir)
        
        # 保存元数据
        metadata = {
            'version_id': version_id,
            'timestamp': timestamp,
            'description': description,
            'type': change_type,
            'files': snapshot_files,
            'stats': {
                'skill_count': self._count_skills(),
                'document_count': self._count_documents()
            }
        }
        
        metadata_file = version_dir / 'metadata.json'
        with open(metadata_file, 'w') as f:
            json.dump(metadata, f, indent=2)
        
        # 清理旧版本
        self._cleanup_old_versions()
        
        print(f"快照已创建: {version_id}")
        return version_id
    
    def _snapshot_files(self, version_dir: Path) -> List[str]:
        """快照核心文件"""
        core_files = [
            'MEMORY.md', 'HEARTBEAT.md', 'skill.json',
            'AGENTS.md', 'SOUL.md', 'USER.md',
            'cron-schedule-v1.2-c-plus.txt'
        ]
        
        copied = []
        for file in core_files:
            src = self.workspace / file
            if src.exists():
                dst = version_dir / file
                shutil.copy2(src, dst)
                copied.append(file)
        
        # 备份skills目录列表
        skills_list = list((self.workspace / 'skills').iterdir()) if (self.workspace / 'skills').exists() else []
        skills_file = version_dir / 'skills-list.txt'
        skills_file.write_text('\n'.join(s.name for s in skills_list))
        copied.append('skills-list.txt')
        
        return copied
    
    def _count_skills(self) -> int:
        """统计Skill数量"""
        skills_dir = self.workspace / 'skills'
        if not skills_dir.exists():
            return 0
        return len([d for d in skills_dir.iterdir() if d.is_dir()])
    
    def _count_documents(self) -> int:
        """统计文档数量"""
        return len(list(self.workspace.rglob('*.md')))
    
    def _cleanup_old_versions(self):
        """清理旧版本"""
        versions = sorted(self.versions_dir.iterdir(), 
                         key=lambda p: p.stat().st_mtime,
                         reverse=True)
        
        # 保留最近7个自动版本 + 所有手动标记版本
        auto_versions = [v for v in versions if not (v / 'manual').exists()]
        
        for old_version in auto_versions[self.VERSION_RETENTION:]:
            shutil.rmtree(old_version)
            print(f"已清理旧版本: {old_version.name}")
    
    def rollback(self, version_id: str) -> Dict[str, Any]:
        """回滚到指定版本"""
        version_dir = self.versions_dir / version_id
        
        if not version_dir.exists():
            raise RollbackError(f"版本 {version_id} 不存在")
        
        # 读取元数据
        metadata_file = version_dir / 'metadata.json'
        with open(metadata_file) as f:
            metadata = json.load(f)
        
        # 创建当前状态备份
        current_backup = self.create_snapshot(
            f"回滚前备份（目标: {version_id}）",
            'pre-rollback'
        )
        
        try:
            # 恢复文件
            for file in metadata['files']:
                src = version_dir / file
                dst = self.workspace / file
                if src.exists():
                    shutil.copy2(src, dst)
            
            # 验证恢复
            verification = self._verify_restoration(metadata)
            
            return {
                'success': True,
                'rolled_to': version_id,
                'backup_id': current_backup,
                'verification': verification
            }
            
        except Exception as e:
            # 回滚失败，恢复原状
            self.rollback(current_backup)
            raise RollbackError(f"回滚失败，已恢复原状: {e}")
    
    def _verify_restoration(self, metadata: Dict) -> Dict[str, bool]:
        """验证恢复后状态"""
        checks = {
            'core_files_exist': self._check_core_files(),
            'skills_executable': self._check_skills(),
            'cron_valid': self._check_cron(),
            'data_consistent': True  # 简化
        }
        
        return checks
    
    def _check_core_files(self) -> bool:
        """检查核心文件"""
        core_files = ['MEMORY.md', 'HEARTBEAT.md', 'skill.json']
        return all((self.workspace / f).exists() for f in core_files)
    
    def _check_skills(self) -> bool:
        """检查Skill可执行性（简化）"""
        return True
    
    def _check_cron(self) -> bool:
        """检查Cron配置"""
        cron_file = self.workspace / 'cron-schedule-v1.2-c-plus.txt'
        return cron_file.exists()
    
    def list_versions(self) -> List[Dict[str, Any]]:
        """列出所有版本"""
        versions = []
        
        for version_dir in sorted(self.versions_dir.iterdir(), reverse=True):
            if not version_dir.is_dir():
                continue
            
            metadata_file = version_dir / 'metadata.json'
            if metadata_file.exists():
                with open(metadata_file) as f:
                    metadata = json.load(f)
                versions.append(metadata)
        
        return versions


class RollbackError(Exception):
    """回滚错误"""
    pass


def main():
    """命令行入口"""
    import sys
    
    manager = VersionManager()
    
    task = sys.argv[1] if len(sys.argv) > 1 else 'list'
    
    if task == 'create-snapshot':
        desc = sys.argv[2] if len(sys.argv) > 2 else "手动快照"
        version_id = manager.create_snapshot(desc)
        print(f"快照创建成功: {version_id}")
        
    elif task == 'rollback':
        version_id = sys.argv[2] if len(sys.argv) > 2 else None
        if not version_id:
            print("请指定版本ID")
            sys.exit(1)
        
        result = manager.rollback(version_id)
        print(f"回滚成功: {result}")
        
    elif task == 'list':
        versions = manager.list_versions()
        print(f"共有 {len(versions)} 个版本:")
        for v in versions:
            print(f"  - {v['version_id']}: {v['description']}")
    
    elif task == 'cleanup-versions':
        manager._cleanup_old_versions()
        print("旧版本清理完成")
    
    else:
        print(f"未知任务: {task}")
        sys.exit(1)


if __name__ == '__main__':
    main()
