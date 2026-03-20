#!/usr/bin/env python3
"""
FFmpeg Batch Processor
批处理视频文件
"""

import os
import sys
import json
import argparse
import subprocess
from pathlib import Path
from datetime import datetime

PRESETS = {
    "youtube": {
        "resolution": "1920x1080",
        "aspect": "16:9",
        "crf": 23,
        "description": "YouTube 1080p"
    },
    "tiktok": {
        "resolution": "1080x1920",
        "aspect": "9:16",
        "crf": 23,
        "description": "抖音/竖屏 1080p"
    },
    "instagram": {
        "resolution": "1080x1080",
        "aspect": "1:1",
        "crf": 23,
        "description": "Instagram 方形"
    },
    "web": {
        "resolution": "1280x720",
        "aspect": "16:9",
        "crf": 28,
        "description": "网页视频 720p"
    },
    "mobile": {
        "resolution": "854x480",
        "aspect": "16:9",
        "crf": 28,
        "description": "移动端 480p"
    }
}


class BatchProcessor:
    def __init__(self, preset, input_dir, output_dir=None):
        self.preset = preset
        self.input_dir = Path(input_dir)
        self.output_dir = Path(output_dir) if output_dir else Path("output") / datetime.now().strftime("%Y%m%d")
        self.config = PRESETS.get(preset, PRESETS["web"])
        self.logs = []
        
    def ensure_dirs(self):
        """确保输出目录存在"""
        self.output_dir.mkdir(parents=True, exist_ok=True)
        (self.output_dir / "converted").mkdir(exist_ok=True)
        (self.output_dir / "logs").mkdir(exist_ok=True)
        (self.output_dir / "failed").mkdir(exist_ok=True)
        
    def get_video_files(self):
        """获取输入目录中的所有视频文件"""
        video_extensions = {".mp4", ".avi", ".mkv", ".mov", ".webm", ".flv", ".wmv"}
        files = []
        for ext in video_extensions:
            files.extend(self.input_dir.glob(f"*{ext}"))
            files.extend(self.input_dir.glob(f"*{ext.upper()}"))
        return sorted(set(files))
    
    def process_file(self, input_file):
        """处理单个文件"""
        base_name = input_file.stem
        output_file = self.output_dir / "converted" / f"{base_name}_{self.preset}.mp4"
        
        width, height = self.config["resolution"].split("x")
        crf = self.config["crf"]
        
        cmd = [
            "ffmpeg", "-y", "-hide_banner",
            "-i", str(input_file),
            "-vf", f"scale={width}:{height}:force_original_aspect_ratio=decrease,pad={width}:{height}:(ow-iw)/2:(oh-ih)/2:black",
            "-c:v", "libx264",
            "-crf", str(crf),
            "-preset", "medium",
            "-c:a", "aac",
            "-b:a", "128k",
            str(output_file)
        ]
        
        print(f"🔄 处理: {input_file.name}")
        
        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=300
            )
            
            if result.returncode == 0:
                # 获取文件大小
                original_size = input_file.stat().st_size
                new_size = output_file.stat().st_size
                
                print(f"   ✅ 完成: {output_file.name}")
                print(f"   📊 大小: {self.human_size(original_size)} → {self.human_size(new_size)}")
                
                return {
                    "file": input_file.name,
                    "status": "success",
                    "output": output_file.name,
                    "original_size": original_size,
                    "new_size": new_size
                }
            else:
                raise Exception(result.stderr)
                
        except Exception as e:
            print(f"   ❌ 失败: {e}")
            # 移动失败文件
            failed_file = self.output_dir / "failed" / input_file.name
            return {
                "file": input_file.name,
                "status": "failed",
                "error": str(e)
            }
    
    @staticmethod
    def human_size(size_bytes):
        """将字节转换为人类可读格式"""
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size_bytes < 1024.0:
                return f"{size_bytes:.1f} {unit}"
            size_bytes /= 1024.0
        return f"{size_bytes:.1f} TB"
    
    def run(self):
        """运行批处理"""
        print("=" * 50)
        print(f"🎬 FFmpeg 批处理器")
        print(f"预设: {self.preset} ({self.config['description']})")
        print(f"输入: {self.input_dir}")
        print(f"输出: {self.output_dir}")
        print("=" * 50)
        
        self.ensure_dirs()
        
        files = self.get_video_files()
        if not files:
            print("❌ 未找到视频文件")
            return
        
        print(f"\n📁 找到 {len(files)} 个视频文件\n")
        
        results = []
        for i, file in enumerate(files, 1):
            print(f"[{i}/{len(files)}] ", end="")
            result = self.process_file(file)
            results.append(result)
            print()
        
        # 保存日志
        log_file = self.output_dir / "logs" / "batch_log.json"
        with open(log_file, 'w') as f:
            json.dump({
                "timestamp": datetime.now().isoformat(),
                "preset": self.preset,
                "config": self.config,
                "total": len(files),
                "success": sum(1 for r in results if r["status"] == "success"),
                "failed": sum(1 for r in results if r["status"] == "failed"),
                "results": results
            }, f, indent=2)
        
        # 打印总结
        success_count = sum(1 for r in results if r["status"] == "success")
        failed_count = len(results) - success_count
        
        print("=" * 50)
        print("📊 批处理完成")
        print(f"   成功: {success_count}")
        print(f"   失败: {failed_count}")
        print(f"   日志: {log_file}")
        print("=" * 50)


def main():
    parser = argparse.ArgumentParser(description="FFmpeg Batch Video Processor")
    parser.add_argument("--preset", choices=list(PRESETS.keys()), default="web",
                       help="处理预设")
    parser.add_argument("--input", "-i", required=True,
                       help="输入目录")
    parser.add_argument("--output", "-o",
                       help="输出目录 (默认: output/YYYYMMDD)")
    
    args = parser.parse_args()
    
    processor = BatchProcessor(args.preset, args.input, args.output)
    processor.run()


if __name__ == "__main__":
    main()
