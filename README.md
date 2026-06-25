# DayReel

**AI-powered daily vlog generation pipeline.**

[中文](#中文) | [English](#english)

---

## 中文

DayReel 是一个自动生成日常 Vlog 的开源引擎。它会读取本地视频素材，抽取关键帧交给通义千问进行视觉理解，自动生成标题、字幕和 Shotstack 模板 merge 字段，最后直接调用 Shotstack Render API 输出成片。

它适合用来把旅行片段、生活记录、活动素材或产品花絮快速整理成一个带标题、字幕、背景音乐和统一模板风格的短视频。

### 功能亮点

- 自动上传本地视频、音乐和关键帧到 S3，生成可供云端渲染访问的素材 URL
- 使用 Qwen VL 分析关键帧，生成视频摘要、情绪、风格、标题和副标题
- 使用 Qwen Text 为 Shotstack JSON 模板生成安全的 merge 替换计划
- 自动校验视频、图片、音频字段，避免把错误素材类型写入模板
- 支持 `manual_merge.json` 手动覆盖模板字段
- 自动修复中文字体渲染，默认使用 Noto Sans CJK
- 直接调用 Shotstack `/render` 接口，不依赖 Shotstack template id
- 输出分析结果、merge 结果、最终渲染 payload 和成片 URL

### 工作流程

```text
videos/*.mp4
  -> upload to S3
  -> extract keyframes with OpenCV
  -> upload keyframes and cover image
  -> Qwen VL analyzes visual content
  -> Qwen Text plans Shotstack merge fields
  -> resolve local Shotstack JSON template
  -> apply CJK font fallback
  -> POST Shotstack /render
  -> output/result.json
```

### 项目结构

```text
app/
  pipeline.py              Main render pipeline
  qwen_client.py           Qwen VL/Text API client
  uploader.py              S3 asset uploader
  keyframes.py             Video keyframe extractor
  merge_builder.py         Safe Shotstack merge builder
  template_loader.py       Shotstack JSON template loader
  font_manager.py          CJK font patcher
  shotstack_render.py      Shotstack render client

template/
  shotstack_edit.json      Local Shotstack JSON template

videos/                    Local source videos, ignored by Git
music/                     Optional local background music, ignored by Git
output/                    Generated runtime artifacts, ignored by Git
```

### 快速开始

1. 安装依赖：

```bash
pip install -r requirements.txt
```

2. 创建环境变量文件：

```bash
cp .env.example .env
```

Windows PowerShell 可以使用：

```powershell
Copy-Item .env.example .env
```

3. 编辑 `.env`，至少配置：

```env
AWS_ACCESS_KEY=your-aws-access-key
AWS_SECRET_KEY=your-aws-secret-key
AWS_REGION=us-east-2
S3_BUCKET=your-public-readable-bucket

SHOTSTACK_KEY=your-shotstack-key
SHOTSTACK_BASE_URL=https://api.shotstack.io/v1

QWEN_API_KEY=your-qwen-api-key
QWEN_BASE_URL=https://dashscope.aliyuncs.com/compatible-mode/v1
```

4. 放入素材：

```text
videos/your-video.mp4
music/bgm.mp3
```

`music/bgm.mp3` 是可选项。没有背景音乐时，DayReel 会使用模板默认值或留空。

5. 运行：

```bash
python main.py
```

6. 查看结果：

```text
output/qwen_analysis.json       Qwen 视觉分析结果
output/qwen_merge_plan.json     Qwen 生成的模板字段计划
output/merge.json               最终 merge 字段
output/render_payload.json      发送给 Shotstack 的完整 JSON
output/result.json              标题、成片 URL 和运行摘要
```

### 手动覆盖模板字段

如果你想强制指定标题、字幕、颜色或某个素材 URL，可以创建 `manual_merge.json`：

```json
{
  "Title": "今日高光瞬间",
  "Subtitle": "把生活片段剪成一支短片",
  "FONT_COLOR": "#000000"
}
```

也可以参考 `manual_merge.example.json`。

### Mock 模式

如果你暂时没有 Qwen API Key，可以在 `.env` 中启用：

```env
MOCK_QWEN=true
TEST_TITLE=今日高光瞬间
TEST_SUBTITLE=AI 自动生成的视频回忆
```

Mock 模式会跳过 Qwen 请求，但仍然需要 S3 和 Shotstack 配置来完成上传与渲染。

### 许可证

建议使用 MIT License。正式开源前可以添加 `LICENSE` 文件。

---

## English

DayReel is an open-source engine for generating daily vlog videos automatically. It takes local video clips, extracts keyframes, asks Qwen to understand the visual story, creates titles/subtitles and Shotstack merge fields, then renders the final video directly through the Shotstack Render API.

It is useful for turning travel clips, daily memories, event footage, or product behind-the-scenes material into a short video with consistent template styling, captions, background music, and AI-assisted storytelling.

### Features

- Uploads local videos, music, and extracted keyframes to S3 for cloud rendering
- Uses Qwen VL to analyze visual content and generate summaries, mood, style, titles, and subtitles
- Uses Qwen Text to plan safe Shotstack JSON merge replacements
- Validates video, image, and audio fields to prevent invalid asset mapping
- Supports `manual_merge.json` for explicit template overrides
- Applies a Chinese/Japanese/Korean font fallback for reliable CJK rendering
- Calls Shotstack `/render` directly without requiring a Shotstack template id
- Writes analysis, merge output, render payload, and final video URL to `output/`

### Pipeline

```text
videos/*.mp4
  -> upload to S3
  -> extract keyframes with OpenCV
  -> upload keyframes and cover image
  -> Qwen VL analyzes visual content
  -> Qwen Text plans Shotstack merge fields
  -> resolve local Shotstack JSON template
  -> apply CJK font fallback
  -> POST Shotstack /render
  -> output/result.json
```

### Project Structure

```text
app/
  pipeline.py              Main render pipeline
  qwen_client.py           Qwen VL/Text API client
  uploader.py              S3 asset uploader
  keyframes.py             Video keyframe extractor
  merge_builder.py         Safe Shotstack merge builder
  template_loader.py       Shotstack JSON template loader
  font_manager.py          CJK font patcher
  shotstack_render.py      Shotstack render client

template/
  shotstack_edit.json      Local Shotstack JSON template

videos/                    Local source videos, ignored by Git
music/                     Optional local background music, ignored by Git
output/                    Generated runtime artifacts, ignored by Git
```

### Quick Start

1. Install dependencies:

```bash
pip install -r requirements.txt
```

2. Create your environment file:

```bash
cp .env.example .env
```

On Windows PowerShell:

```powershell
Copy-Item .env.example .env
```

3. Edit `.env` and configure at least:

```env
AWS_ACCESS_KEY=your-aws-access-key
AWS_SECRET_KEY=your-aws-secret-key
AWS_REGION=us-east-2
S3_BUCKET=your-public-readable-bucket

SHOTSTACK_KEY=your-shotstack-key
SHOTSTACK_BASE_URL=https://api.shotstack.io/v1

QWEN_API_KEY=your-qwen-api-key
QWEN_BASE_URL=https://dashscope.aliyuncs.com/compatible-mode/v1
```

4. Add source media:

```text
videos/your-video.mp4
music/bgm.mp3
```

`music/bgm.mp3` is optional. If it is missing, DayReel will use the template default or leave the music field empty.

5. Run:

```bash
python main.py
```

6. Inspect generated artifacts:

```text
output/qwen_analysis.json       Qwen visual analysis
output/qwen_merge_plan.json     Qwen template field plan
output/merge.json               Final merge fields
output/render_payload.json      Full JSON payload sent to Shotstack
output/result.json              Title, rendered video URL, and run summary
```

### Manual Template Overrides

Create `manual_merge.json` when you need to force specific titles, subtitles, colors, or asset URLs:

```json
{
  "Title": "Daily Highlights",
  "Subtitle": "Turn life clips into a short story",
  "FONT_COLOR": "#000000"
}
```

You can also start from `manual_merge.example.json`.

### Mock Mode

If you do not have a Qwen API key yet, enable:

```env
MOCK_QWEN=true
TEST_TITLE=Daily Highlights
TEST_SUBTITLE=AI-generated video memories
```

Mock mode skips Qwen calls, but S3 and Shotstack are still required for uploading and rendering.

### License

MIT License is recommended. Add a `LICENSE` file before publishing a stable open-source release.
