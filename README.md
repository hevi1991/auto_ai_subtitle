# auto ai subtitle translator

## 简介
ai字幕生成，字幕翻译 基于openai/whisper、~~translate~~、ffmpeg，自动为视频生成翻译过后的srt字幕文件，支持自定义各种语言

## 功能
1.基于视频中的语音直接生成字幕文件  
2.翻译字幕文件

## 使用方法
安装 `ffmpeg`

安装依赖 `pip install -r requirements.txt`

拷贝一份`config.example.yaml`命名为`config.yaml`，将配置信息填入

执行 `python main.py`
