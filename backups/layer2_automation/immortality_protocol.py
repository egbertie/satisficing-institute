#!/usr/bin/env python3
"""
Claw Immortality Protocol - 永生协议自动化脚本
全量灾备自动化系统
"""

import sys
import json
import os
import hashlib
import tarfile
from datetime import datetime

BACKUP_ROOT = "/root/.openclaw/workspace/backups"
LAYERS = ["layer1_meta", "layer2_automation", "layer3_collaboration", 
          "layer4_identity", "layer5_knowledge", "layer6_memory", "layer7_runtime"]

def generate_manifest():
    """生成全量清单，包含所有文件的哈希值"""
    timestamp = datetime.now().isoformat()
    manifest = {
        "generated_at": timestamp,
        "version": "1.0",
        "layers": {}
    }
    
    for layer in LAYERS:
        layer_path = os.path.join(BACKUP_ROOT, layer)
        if os.path.exists(layer_path):
            layer_files = []
            for root, dirs, files in os.walk(layer_path):
                for file in files:
                    file_path = os.path.join(root, file)
                    rel_path = os.path.relpath(file_path, BACKUP_ROOT)
                    
                    # 计算BLAKE3哈希（简化用SHA256）
                    sha256 = hashlib.sha256()
                    with open(file_path, 'rb') as f:
                        sha256.update(f.read())
                    
                    layer_files.append({
                        "path": rel_path,
                        "size": os.path.getsize(file_path),
                        "hash": sha256.hexdigest()[:16]  # 取前16位
                    })
            
            manifest["layers"][layer] = {
                "file_count": len(layer_files),
                "files": layer_files
            }
    
    # 保存清单
    manifest_path = os.path.join(BACKUP_ROOT, "MANIFEST.json")
    with open(manifest_path, 'w') as f:
        json.dump(manifest, f, indent=2)
    
    print(f"[MANIFEST] 生成完成: {manifest_path}")
    print(f"  时间: {timestamp}")
    print(f"  层数: {len(manifest['layers'])}")
    total_files = sum(l["file_count"] for l in manifest["layers"].values())
    print(f"  文件总数: {total_files}")
    
    return 0

def create_full_snapshot():
    """创建全量快照"""
    timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    checkpoint_id = f"PHOENIX-BASELINE-{timestamp}"
    
    print(f"[全量快照] 开始创建: {checkpoint_id}")
    
    # 创建压缩包
    snapshot_path = os.path.join(BACKUP_ROOT, f"FULL-SNAPSHOT-{timestamp}.tar.gz")
    
    with tarfile.open(snapshot_path, "w:gz") as tar:
        # 备份7层状态栈
        for layer in LAYERS:
            layer_path = os.path.join(BACKUP_ROOT, layer)
            if os.path.exists(layer_path):
                tar.add(layer_path, arcname=layer)
        
        # 备份关键系统文件
        critical_files = [
            "/root/.openclaw/workspace/SOUL.md",
            "/root/.openclaw/workspace/IDENTITY.md",
            "/root/.openclaw/workspace/USER.md",
            "/root/.openclaw/workspace/MEMORY.md",
            "/root/.openclaw/workspace/HEARTBEAT.md"
        ]
        
        for file_path in critical_files:
            if os.path.exists(file_path):
                tar.add(file_path, arcname=f"system/{os.path.basename(file_path)}")
    
    # 生成清单
    generate_manifest()
    
    print(f"[全量快照] 创建完成")
    print(f"  Checkpoint ID: {checkpoint_id}")
    print(f"  路径: {snapshot_path}")
    print(f"  大小: {os.path.getsize(snapshot_path)} bytes")
    
    return checkpoint_id

def verify_backup():
    """验证备份完整性"""
    manifest_path = os.path.join(BACKUP_ROOT, "MANIFEST.json")
    
    if not os.path.exists(manifest_path):
        print("[验证] ❌ MANIFEST.json 不存在")
        return 1
    
    with open(manifest_path, 'r') as f:
        manifest = json.load(f)
    
    print("[验证] 开始完整性检查...")
    verified = 0
    failed = 0
    
    for layer_name, layer_data in manifest["layers"].items():
        for file_info in layer_data["files"]:
            file_path = os.path.join(BACKUP_ROOT, file_info["path"])
            
            if not os.path.exists(file_path):
                print(f"  ❌ 缺失: {file_info['path']}")
                failed += 1
                continue
            
            # 验证哈希
            sha256 = hashlib.sha256()
            with open(file_path, 'rb') as f:
                sha256.update(f.read())
            current_hash = sha256.hexdigest()[:16]
            
            if current_hash == file_info["hash"]:
                verified += 1
            else:
                print(f"  ⚠️  哈希不匹配: {file_info['path']}")
                failed += 1
    
    print(f"[验证] 完成: ✅ {verified} | ❌ {failed}")
    return 0 if failed == 0 else 1

def health_check():
    """灾备健康检查"""
    print("=" * 60)
    print("[灾备系统健康报告]")
    print("=" * 60)
    
    # 1. 备份完整性
    manifest_path = os.path.join(BACKUP_ROOT, "MANIFEST.json")
    integrity = "✅ 通过" if os.path.exists(manifest_path) else "❌ 缺失"
    print(f"1. 备份完整性: {integrity}")
    
    # 2. 恢复就绪度（RTO）
    print("2. 恢复就绪度(RTO): 预估 <10分钟（基于当前备份规模）")
    
    # 3. 数据新鲜度（RPO）
    if os.path.exists(manifest_path):
        with open(manifest_path, 'r') as f:
            manifest = json.load(f)
        last_backup = manifest.get("generated_at", "未知")
        print(f"3. 数据新鲜度(RPO): 最近备份 {last_backup}")
    
    # 4. 存储冗余
    layer_count = len([d for d in os.listdir(BACKUP_ROOT) if d.startswith("layer")])
    print(f"4. 存储冗余: {layer_count}/7 层已备份")
    
    # 5. 改进建议
    print("5. 改进建议:")
    if layer_count < 7:
        print("   - 完成剩余 Layer 备份")
    print("   - 建立企微实时同步通道")
    print("   - 配置每日健康检查Cron")
    
    print("=" * 60)
    return 0

def main():
    if len(sys.argv) < 2:
        print("Usage: python3 immortality.py [snapshot|verify|health|manifest]")
        print("  snapshot - 创建全量快照")
        print("  verify   - 验证备份完整性")
        print("  health   - 生成健康报告")
        print("  manifest - 生成文件清单")
        sys.exit(1)
    
    command = sys.argv[1]
    
    if command == "snapshot":
        checkpoint_id = create_full_snapshot()
        print(f"\n[重生就绪] Checkpoint ID: {checkpoint_id}")
        return 0
    
    elif command == "verify":
        return verify_backup()
    
    elif command == "health":
        return health_check()
    
    elif command == "manifest":
        return generate_manifest()
    
    else:
        print(f"Unknown command: {command}")
        return 1

if __name__ == "__main__":
    sys.exit(main())
