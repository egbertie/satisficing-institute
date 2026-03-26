#!/usr/bin/env python3
"""
Workspace Health Scanner - 工作空间健康度扫描器
扫描四个维度：结构、时效、引用、安全
"""

import os
import json
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Any

class WorkspaceHealthScanner:
    """工作空间健康度扫描器"""
    
    DIMENSIONS = {
        'structure': 0.25,
        'freshness': 0.25,
        'reference': 0.25,
        'security': 0.25
    }
    
    CORE_FILES = [
        'MEMORY.md',
        'HEARTBEAT.md',
        'skill.json',
        'AGENTS.md',
        'SOUL.md',
        'USER.md'
    ]
    
    def __init__(self, workspace_path: str = '/root/.openclaw/workspace'):
        self.workspace = Path(workspace_path)
        self.issues = []
        self.recommendations = []
    
    def scan(self, dimensions: List[str] = None) -> Dict[str, Any]:
        """执行健康度扫描"""
        if dimensions is None:
            dimensions = list(self.DIMENSIONS.keys())
        
        scores = {}
        
        if 'structure' in dimensions:
            scores['structure'] = self._scan_structure()
        
        if 'freshness' in dimensions:
            scores['freshness'] = self._scan_freshness()
        
        if 'reference' in dimensions:
            scores['reference'] = self._scan_references()
        
        if 'security' in dimensions:
            scores['security'] = self._scan_security()
        
        # 计算总分
        total_score = sum(
            scores.get(dim, 0) * weight 
            for dim, weight in self.DIMENSIONS.items()
        )
        
        return {
            'timestamp': datetime.now().isoformat(),
            'total_score': round(total_score, 1),
            'dimension_scores': scores,
            'grade': self._get_grade(total_score),
            'issues': self.issues,
            'recommendations': self.recommendations,
            'scan_summary': self._generate_summary(scores)
        }
    
    def _scan_structure(self) -> float:
        """扫描结构健康度"""
        score = 100
        
        # 检查核心文件
        for file in self.CORE_FILES:
            if not (self.workspace / file).exists():
                self.issues.append({
                    'level': 'critical',
                    'dimension': 'structure',
                    'message': f'核心文件缺失: {file}'
                })
                score -= 15
        
        # 检查空目录
        empty_dirs = self._find_empty_dirs()
        if empty_dirs:
            self.issues.append({
                'level': 'warning',
                'dimension': 'structure',
                'message': f'发现 {len(empty_dirs)} 个空目录'
            })
            score -= min(len(empty_dirs) * 2, 10)
        
        # 检查重复文件
        duplicates = self._find_duplicates()
        if duplicates:
            self.issues.append({
                'level': 'info',
                'dimension': 'structure',
                'message': f'发现 {len(duplicates)} 组重复文件'
            })
            score -= min(len(duplicates), 5)
        
        return max(score, 0)
    
    def _scan_freshness(self) -> float:
        """扫描时效健康度"""
        score = 100
        now = datetime.now()
        
        # 检查文档更新
        endangered = []
        zombie = []
        
        for md_file in self.workspace.rglob('*.md'):
            if 'archive' in str(md_file):
                continue
            
            mtime = datetime.fromtimestamp(md_file.stat().st_mtime)
            days_old = (now - mtime).days
            
            if days_old > 90:
                zombie.append(md_file.name)
            elif days_old > 30:
                endangered.append(md_file.name)
        
        if zombie:
            self.issues.append({
                'level': 'warning',
                'dimension': 'freshness',
                'message': f'发现 {len(zombie)} 个僵尸文档(90天未更新)'
            })
            score -= min(len(zombie) * 2, 20)
        
        if endangered:
            self.issues.append({
                'level': 'info',
                'dimension': 'freshness',
                'message': f'发现 {len(endangered)} 个濒危文档(30天未更新)'
            })
            score -= min(len(endangered), 10)
        
        return max(score, 0)
    
    def _scan_references(self) -> float:
        """扫描引用健康度"""
        score = 100
        # 简化实现，实际应检查文档间链接
        return score
    
    def _scan_security(self) -> float:
        """扫描安全健康度"""
        score = 100
        
        # 检查.env文件权限
        env_file = self.workspace / '.env'
        if env_file.exists():
            stat = env_file.stat()
            if stat.st_mode & 0o044:  # 其他用户可读
                self.issues.append({
                    'level': 'critical',
                    'dimension': 'security',
                    'message': '.env文件权限过于开放'
                })
                score -= 20
        
        return max(score, 0)
    
    def _find_empty_dirs(self) -> List[Path]:
        """查找空目录"""
        empty = []
        for path in self.workspace.rglob('*'):
            if path.is_dir() and not any(path.iterdir()):
                empty.append(path)
        return empty
    
    def _find_duplicates(self) -> List[List[Path]]:
        """查找重复文件（简化实现）"""
        return []  # 实际实现需要文件哈希对比
    
    def _get_grade(self, score: float) -> Dict[str, str]:
        """根据分数评定等级"""
        if score >= 90:
            return {'grade': 'A', 'status': 'healthy', 'emoji': '🟢'}
        elif score >= 80:
            return {'grade': 'B', 'status': 'good', 'emoji': '🟢'}
        elif score >= 70:
            return {'grade': 'C', 'status': 'fair', 'emoji': '🟡'}
        elif score >= 60:
            return {'grade': 'D', 'status': 'poor', 'emoji': '🟠'}
        else:
            return {'grade': 'F', 'status': 'critical', 'emoji': '🔴'}
    
    def _generate_summary(self, scores: Dict[str, float]) -> str:
        """生成扫描摘要"""
        lines = ["健康度扫描摘要:"]
        for dim, score in scores.items():
            lines.append(f"  - {dim}: {score}分")
        lines.append(f"  - 问题数: {len(self.issues)}")
        return "\n".join(lines)
    
    def generate_report(self, result: Dict[str, Any]) -> str:
        """生成健康度报告"""
        report_lines = [
            "# 工作空间健康度报告",
            f"生成时间: {result['timestamp']}",
            "",
            f"## 总体评分: {result['total_score']}分 {result['grade']['emoji']}",
            "",
            "## 各维度评分",
            "| 维度 | 得分 | 权重 | 加权分 |",
            "|------|------|------|--------|",
        ]
        
        for dim, score in result['dimension_scores'].items():
            weight = self.DIMENSIONS[dim]
            weighted = score * weight
            report_lines.append(f"| {dim} | {score} | {weight*100:.0f}% | {weighted:.1f} |")
        
        report_lines.extend([
            "",
            "## 发现的问题",
        ])
        
        for issue in result['issues']:
            emoji = {'critical': '🔴', 'warning': '🟡', 'info': '🟢'}.get(issue['level'], '⚪')
            report_lines.append(f"{emoji} [{issue['dimension']}] {issue['message']}")
        
        return "\n".join(report_lines)


def main():
    """命令行入口"""
    import sys
    
    scanner = WorkspaceHealthScanner()
    
    # 解析参数
    task = 'daily-scan'
    if len(sys.argv) > 1:
        task = sys.argv[1]
    
    if task == 'daily-scan':
        result = scanner.scan()
    elif task == 'deep-scan':
        result = scanner.scan()  # 深度扫描可扩展
    else:
        print(f"未知任务: {task}")
        sys.exit(1)
    
    # 输出报告
    report = scanner.generate_report(result)
    print(report)
    
    # 保存结果
    output_dir = Path('/root/.openclaw/workspace/reports/health')
    output_dir.mkdir(parents=True, exist_ok=True)
    
    timestamp = datetime.now().strftime('%Y%m%d-%H%M%S')
    output_file = output_dir / f'health-report-{timestamp}.md'
    output_file.write_text(report)
    
    print(f"\n报告已保存: {output_file}")


if __name__ == '__main__':
    main()
