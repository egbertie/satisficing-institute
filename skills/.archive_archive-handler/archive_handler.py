#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Archive Handler - 安全通用压缩文件处理工具
版本: 1.0.0
作者: Satisficing Institute
"""

import os
import sys
import subprocess
import tarfile
import zipfile
import argparse
from pathlib import Path
from typing import List, Dict, Tuple, Optional
import shutil

# 安全配置
MAX_SINGLE_FILE_SIZE = 100 * 1024 * 1024  # 100MB
MAX_TOTAL_EXTRACT_SIZE = 1024 * 1024 * 1024  # 1GB
BLOCKED_PATHS = [
    '/etc/', '/usr/', '/bin/', '/sbin/', '/lib', '/opt/',
    '/var/', '/sys/', '/proc/', '/dev/', '/boot/',
    'C:\\Windows', 'C:\\Program Files', 'C:\\System',
]
SUSPICIOUS_EXTENSIONS = ['.exe', '.bat', '.cmd', '.sh', '.dll', '.so', '.dylib']


class SecurityError(Exception):
    """安全违规异常"""
    pass


def check_path_traversal(file_path: str) -> bool:
    """检查路径遍历攻击"""
    normalized = os.path.normpath(file_path)
    return '..' in normalized.split(os.sep)


def check_blocked_path(abs_path: str) -> bool:
    """检查是否是系统敏感路径"""
    abs_path = os.path.abspath(abs_path)
    for blocked in BLOCKED_PATHS:
        if abs_path.startswith(blocked):
            return True
    return False


def get_archive_type(file_path: str) -> str:
    """识别压缩包格式"""
    ext = file_path.lower()
    if ext.endswith('.zip'):
        return 'zip'
    elif ext.endswith('.rar'):
        return 'rar'
    elif ext.endswith(('.7z', '.7zip')):
        return '7z'
    elif ext.endswith(('.tar.gz', '.tgz')):
        return 'tar.gz'
    elif ext.endswith(('.tar.bz2', '.tbz2')):
        return 'tar.bz2'
    elif ext.endswith(('.tar.xz', '.txz')):
        return 'tar.xz'
    elif ext.endswith('.tar'):
        return 'tar'
    else:
        return 'unknown'


def is_tool_available(tool: str) -> bool:
    """检查系统是否有指定工具"""
    return shutil.which(tool) is not None


def preview_archive(file_path: str) -> Dict:
    """
    安全预览压缩包内容
    返回: {
        'format': str,
        'files': List[Dict],
        'total_size': int,
        'risk_level': str,  # safe, caution, danger
        'warnings': List[str]
    }
    """
    result = {
        'format': get_archive_type(file_path),
        'files': [],
        'total_size': 0,
        'risk_level': 'safe',
        'warnings': []
    }
    
    if result['format'] == 'unknown':
        result['warnings'].append(f"无法识别的压缩格式: {file_path}")
        result['risk_level'] = 'danger'
        return result
    
    try:
        if result['format'] == 'zip':
            result = _preview_zip(file_path, result)
        elif result['format'].startswith('tar'):
            result = _preview_tar(file_path, result)
        elif result['format'] == 'rar':
            result = _preview_rar(file_path, result)
        elif result['format'] == '7z':
            result = _preview_7z(file_path, result)
    except Exception as e:
        result['warnings'].append(f"预览失败: {str(e)}")
        result['risk_level'] = 'danger'
    
    # 评估风险等级
    for f in result['files']:
        # 检查可执行文件
        if any(f['name'].lower().endswith(ext) for ext in SUSPICIOUS_EXTENSIONS):
            result['warnings'].append(f"发现可执行文件: {f['name']}")
            if result['risk_level'] == 'safe':
                result['risk_level'] = 'caution'
        
        # 检查超大文件
        if f['size'] > MAX_SINGLE_FILE_SIZE:
            result['warnings'].append(f"超大文件: {f['name']} ({f['size']/1024/1024:.1f}MB)")
            result['risk_level'] = 'danger'
        
        # 检查路径遍历
        if check_path_traversal(f['name']):
            result['warnings'].append(f"可疑路径: {f['name']}")
            result['risk_level'] = 'danger'
    
    return result


def _preview_zip(file_path: str, result: Dict) -> Dict:
    """预览 ZIP 文件"""
    with zipfile.ZipFile(file_path, 'r') as zf:
        for info in zf.infolist():
            result['files'].append({
                'name': info.filename,
                'size': info.file_size,
                'compressed': info.compress_size,
                'is_dir': info.is_dir()
            })
            result['total_size'] += info.file_size
    return result


def _preview_tar(file_path: str, result: Dict) -> Dict:
    """预览 TAR 及其压缩变体"""
    mode = 'r'
    if result['format'] == 'tar.gz':
        mode = 'r:gz'
    elif result['format'] == 'tar.bz2':
        mode = 'r:bz2'
    elif result['format'] == 'tar.xz':
        mode = 'r:xz'
    
    with tarfile.open(file_path, mode) as tf:
        for member in tf.getmembers():
            result['files'].append({
                'name': member.name,
                'size': member.size,
                'compressed': 0,
                'is_dir': member.isdir()
            })
            result['total_size'] += member.size
    return result


def _preview_rar(file_path: str, result: Dict) -> Dict:
    """预览 RAR 文件（依赖 unrar）"""
    if not is_tool_available('unrar'):
        result['warnings'].append("未安装 unrar，无法预览 RAR 文件")
        result['risk_level'] = 'danger'
        return result
    
    try:
        output = subprocess.check_output(
            ['unrar', 'l', '-v', file_path],
            stderr=subprocess.DEVNULL,
            text=True
        )
        # 简单解析 unrar 输出
        lines = output.split('\n')
        for line in lines:
            if line.strip() and not line.startswith(('UNRAR', '---', '评论', '卷')):
                parts = line.split()
                if len(parts) >= 3 and parts[-2].isdigit():
                    size = int(parts[-2])
                    name = ' '.join(parts[1:-2])
                    result['files'].append({
                        'name': name,
                        'size': size,
                        'compressed': 0,
                        'is_dir': False
                    })
                    result['total_size'] += size
    except Exception as e:
        result['warnings'].append(f"RAR 预览失败: {str(e)}")
    
    return result


def _preview_7z(file_path: str, result: Dict) -> Dict:
    """预览 7z 文件（依赖 7z）"""
    tool = '7z' if is_tool_available('7z') else '7za'
    if not is_tool_available(tool):
        result['warnings'].append("未安装 7z/p7zip，无法预览 7z 文件")
        result['risk_level'] = 'danger'
        return result
    
    try:
        output = subprocess.check_output(
            [tool, 'l', file_path],
            stderr=subprocess.DEVNULL,
            text=True
        )
        lines = output.split('\n')
        for line in lines:
            if line.strip() and line[0].isdigit():
                parts = line.split()
                if len(parts) >= 6:
                    size = int(parts[3]) if parts[3].isdigit() else 0
                    name = parts[5]
                    result['files'].append({
                        'name': name,
                        'size': size,
                        'compressed': 0,
                        'is_dir': name.endswith('/')
                    })
                    result['total_size'] += size
    except Exception as e:
        result['warnings'].append(f"7z 预览失败: {str(e)}")
    
    return result


def extract_archive(file_path: str, output_dir: Optional[str] = None) -> Tuple[bool, str]:
    """
    安全解压压缩包
    返回: (是否成功, 消息)
    """
    if not os.path.exists(file_path):
        return False, f"文件不存在: {file_path}"
    
    # 先预览检查
    preview = preview_archive(file_path)
    
    if preview['risk_level'] == 'danger':
        return False, f"安全风险阻止解压:\n" + '\n'.join(f"  - {w}" for w in preview['warnings'])
    
    if preview['total_size'] > MAX_TOTAL_EXTRACT_SIZE:
        return False, f"总解压尺寸过大: {preview['total_size']/1024/1024:.1f}MB > {MAX_TOTAL_EXTRACT_SIZE/1024/1024}MB"
    
    # 确定输出目录
    if output_dir is None:
        base_name = os.path.splitext(os.path.basename(file_path))[0]
        output_dir = f"./extracted_{base_name}"
    
    output_dir = os.path.abspath(output_dir)
    
    # 安全检查输出路径
    if check_blocked_path(output_dir):
        return False, f"禁止写入系统路径: {output_dir}"
    
    # 创建输出目录
    os.makedirs(output_dir, exist_ok=True)
    
    try:
        fmt = preview['format']
        
        if fmt == 'zip':
            return _extract_zip(file_path, output_dir)
        elif fmt.startswith('tar'):
            return _extract_tar(file_path, output_dir, fmt)
        elif fmt == 'rar':
            return _extract_rar(file_path, output_dir)
        elif fmt == '7z':
            return _extract_7z(file_path, output_dir)
        else:
            return False, f"不支持的格式: {fmt}"
            
    except Exception as e:
        return False, f"解压失败: {str(e)}"


def _extract_zip(file_path: str, output_dir: str) -> Tuple[bool, str]:
    """安全解压 ZIP"""
    with zipfile.ZipFile(file_path, 'r') as zf:
        for info in zf.infolist():
            # 安全检查
            if check_path_traversal(info.filename):
                return False, f"路径遍历风险: {info.filename}"
            
            target_path = os.path.join(output_dir, info.filename)
            target_path = os.path.abspath(target_path)
            
            if not target_path.startswith(os.path.abspath(output_dir)):
                return False, f"路径逃逸风险: {info.filename}"
            
            if check_blocked_path(target_path):
                return False, f"禁止写入系统路径: {target_path}"
        
        # 执行解压
        zf.extractall(output_dir)
    
    return True, f"成功解压到: {output_dir}"


def _extract_tar(file_path: str, output_dir: str, fmt: str) -> Tuple[bool, str]:
    """安全解压 TAR 及其变体"""
    mode = 'r'
    if fmt == 'tar.gz':
        mode = 'r:gz'
    elif fmt == 'tar.bz2':
        mode = 'r:bz2'
    elif fmt == 'tar.xz':
        mode = 'r:xz'
    
    with tarfile.open(file_path, mode) as tf:
        for member in tf.getmembers():
            # 安全检查
            if check_path_traversal(member.name):
                return False, f"路径遍历风险: {member.name}"
            
            target_path = os.path.join(output_dir, member.name)
            target_path = os.path.abspath(target_path)
            
            if not target_path.startswith(os.path.abspath(output_dir)):
                return False, f"路径逃逸风险: {member.name}"
            
            if check_blocked_path(target_path):
                return False, f"禁止写入系统路径: {target_path}"
            
            # 检查符号链接
            if member.issym() or member.islnk():
                return False, f"禁止解压符号链接: {member.name}"
        
        # 执行解压
        tf.extractall(output_dir)
    
    return True, f"成功解压到: {output_dir}"


def _extract_rar(file_path: str, output_dir: str) -> Tuple[bool, str]:
    """解压 RAR（依赖 unrar）"""
    if not is_tool_available('unrar'):
        return False, "未安装 unrar，请先安装: apt-get install unrar"
    
    try:
        subprocess.run(
            ['unrar', 'x', '-o+', file_path, output_dir + '/'],
            check=True,
            capture_output=True,
            text=True
        )
        return True, f"成功解压到: {output_dir}"
    except subprocess.CalledProcessError as e:
        return False, f"unrar 执行失败: {e.stderr}"


def _extract_7z(file_path: str, output_dir: str) -> Tuple[bool, str]:
    """解压 7z（依赖 7z/p7zip）"""
    tool = '7z' if is_tool_available('7z') else '7za'
    if not is_tool_available(tool):
        return False, "未安装 7z/p7zip，请先安装: apt-get install p7zip-full"
    
    try:
        subprocess.run(
            [tool, 'x', file_path, f'-o{output_dir}'],
            check=True,
            capture_output=True,
            text=True
        )
        return True, f"成功解压到: {output_dir}"
    except subprocess.CalledProcessError as e:
        return False, f"7z 执行失败: {e.stderr}"


def format_preview(result: Dict) -> str:
    """格式化预览结果为可读文本"""
    lines = []
    lines.append(f"📦 压缩包格式: {result['format'].upper()}")
    lines.append(f"📊 文件总数: {len(result['files'])}")
    lines.append(f"📏 总大小: {result['total_size']/1024/1024:.2f} MB")
    lines.append("")
    
    # 风险等级
    risk_emoji = {'safe': '✅', 'caution': '⚠️', 'danger': '❌'}
    risk_text = {'safe': '安全', 'caution': '需谨慎', 'danger': '高风险'}
    lines.append(f"🔒 安全评估: {risk_emoji.get(result['risk_level'], '?')} {risk_text.get(result['risk_level'], result['risk_level'])}")
    
    if result['warnings']:
        lines.append("\n⚠️ 警告:")
        for w in result['warnings']:
            lines.append(f"  - {w}")
    
    # 文件列表（前20个）
    lines.append(f"\n📁 文件列表 (前20个):")
    for i, f in enumerate(result['files'][:20], 1):
        size_str = f"{f['size']/1024:.1f}KB" if f['size'] < 1024*1024 else f"{f['size']/1024/1024:.2f}MB"
        dir_mark = "📂" if f['is_dir'] else "📄"
        lines.append(f"  {i}. {dir_mark} {f['name']} ({size_str})")
    
    if len(result['files']) > 20:
        lines.append(f"  ... 还有 {len(result['files']) - 20} 个文件")
    
    return '\n'.join(lines)


def main():
    parser = argparse.ArgumentParser(
        description='Archive Handler - 安全通用压缩文件处理工具'
    )
    parser.add_argument('action', choices=['preview', 'extract', 'info'],
                       help='操作: preview=预览, extract=解压, info=显示信息')
    parser.add_argument('file', help='压缩包路径')
    parser.add_argument('output', nargs='?', help='解压目标目录（可选）')
    parser.add_argument('--max-size', type=int, default=MAX_SINGLE_FILE_SIZE,
                       help=f'单文件最大尺寸（默认{MAX_SINGLE_FILE_SIZE}字节）')
    
    args = parser.parse_args()
    
    if args.action == 'preview':
        result = preview_archive(args.file)
        print(format_preview(result))
        sys.exit(0 if result['risk_level'] != 'danger' else 1)
    
    elif args.action == 'extract':
        success, msg = extract_archive(args.file, args.output)
        print(msg)
        sys.exit(0 if success else 1)
    
    elif args.action == 'info':
        print("Archive Handler v1.0.0")
        print("支持的格式: ZIP, RAR, 7z, TAR, TAR.GZ, TAR.BZ2, TAR.XZ")
        print("")
        print("已安装工具:")
        tools = ['unzip', 'tar', 'unrar', '7z', '7za']
        for tool in tools:
            status = "✅" if is_tool_available(tool) else "❌"
            print(f"  {status} {tool}")
        sys.exit(0)


if __name__ == '__main__':
    main()
