# auto ai subtitle translator

## 0909更新
新增指定whisper model功能，支持使用[huggingface](https://huggingface.co/collections/openai/whisper-release-6501bba2cf999715fd953013)下载的自定义model

## 简介
ai字幕生成，字幕翻译 基于openai/whisper、~~translate~~、ffmpeg，自动为视频生成翻译过后的srt字幕文件，支持自定义各种语言

## 功能
1.基于视频中的语音直接生成字幕文件  
2.翻译字幕文件

## 使用方法
安装 `ffmpeg`

安装依赖 `pip install -r requirements.txt`

将配置信息填入 `config.yaml`

执行 `python main.py`
