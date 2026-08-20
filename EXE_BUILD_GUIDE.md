# EXE Build Guide

## Version 0.1.3

This build adds Windows EXE metadata:

- Company: GALA IT팀
- Product: 회의 음성 파일 변환기
- File description: 회의 음성 WebM → M4A 변환 프로그램
- File version: 0.1.3
- Product version: 0.1.3

## Required files

Put these files in the project folder:

- meeting_audio_converter.py
- version_info.txt
- meeting_audio_converter.ico
- requirements.txt

FFmpeg is used at runtime and should remain outside Git.

## Build

Install dependencies:

```cmd
python -m pip install -r requirements.txt
python -m pip install pyinstaller
```

Then run:

```cmd
build_exe.bat
```

Or:

```cmd
python -m PyInstaller --clean --onefile --noconsole --name "회의음성변환기" --icon "meeting_audio_converter.ico" --version-file "version_info.txt" --collect-all tkinterdnd2 meeting_audio_converter.py
```

The result is:

```text
dist/
└─ 회의음성변환기.exe
```

Runtime distribution remains:

```text
회의음성변환기_배포/
├─ 회의음성변환기.exe
└─ ffmpeg.exe
```
