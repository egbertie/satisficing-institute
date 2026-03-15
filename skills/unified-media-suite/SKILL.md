---
name: unified-media-suite
description: Unified media processing suite for audio, video, and image operations. Replaces ffmpeg-video-editor, audio-handler, video-frames with single integrated interface. Use for: video editing, audio processing, format conversion, frame extraction, media compression.
triggers: ["video", "audio", "media", "ffmpeg", "convert", "edit", "剪辑", "视频"]
---

# Unified Media Suite

**统一媒体处理套件** - 整合音视频处理能力。

> 🎯 替代: ffmpeg-video-editor + audio-handler + video-frames

---

## 核心能力

| 功能模块 | 覆盖场景 |
|---------|---------|
| **视频编辑** | 剪辑、合并、转场、字幕、特效 |
| **音频处理** | 降噪、混音、格式转换、提取 |
| **格式转换** | 视频/音频/图片格式批量转换 |
| **帧操作** | 提取、生成GIF、缩略图 |
| **压缩优化** | 智能压缩、批量处理 |

---

## 快速开始

```bash
# 视频剪辑
media-suite video cut --input video.mp4 --start 00:01:30 --end 00:03:00 --output clip.mp4

# 合并视频
media-suite video merge --inputs "part1.mp4,part2.mp4" --output full.mp4

# 音频提取
media-suite audio extract --input video.mp4 --output audio.mp3

# 提取帧
media-suite frame extract --input video.mp4 --interval 5s --output frames/

# 格式转换
media-suite convert --input "*.mov" --format mp4 --output-dir ./converted/

# 批量压缩
media-suite compress --inputs "*.mp4" --quality medium --output ./compressed/
```

---

## 替代关系

| 原Skill | 新命令 |
|---------|--------|
| ffmpeg-video-editor | `media-suite video` |
| audio-handler | `media-suite audio` |
| video-frames | `media-suite frame` |

---

**自建替代计数**: +3
