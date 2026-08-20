# Meeting Audio Converter

tl;dv Desktop에서 생성된 WebM 회의 녹음 파일을 클로바노트에서 사용할 수 있는 M4A 파일로 변환하는 Windows 프로그램입니다.

## 기능

- WebM → M4A (AAC 128kbps)
- 여러 WebM 파일 일괄 변환
- WebM 파일 드래그 앤 드롭
- 원본 WebM과 같은 폴더에 M4A 생성
- 로컬 PC에서만 변환
- FFmpeg 사용

## 개발 환경

- Python 3.14
- Tkinter
- tkinterdnd2
- FFmpeg
- PyInstaller

## 개발 PC에서 실행

```cmd
python -m pip install -r requirements.txt
python meeting_audio_converter.py
```

개발 테스트 시에는 FFmpeg가 PATH에 있거나 `ffmpeg.exe`를 이 프로젝트 폴더에 둡니다.

## EXE 빌드

```cmd
python -m PyInstaller --onefile --noconsole --collect-all tkinterdnd2 meeting_audio_converter.py
```

빌드 후 `dist` 폴더의 EXE를 확인합니다.

배포 방식과 FFmpeg 라이선스/재배포 조건은 별도로 검토합니다.
