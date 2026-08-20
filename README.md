# Meeting Audio Converter

GALA IT팀에서 사용하는 회의 음성 파일 변환 프로그램입니다.

## Version

0.1.2

## 기능

- WebM → M4A (AAC 128kbps)
- 여러 WebM 파일 일괄 변환
- WebM 파일 드래그 앤 드롭
- 원본 WebM과 같은 폴더에 M4A 생성
- 변환 폴더 열기
- 로컬 PC에서 변환

## 실행

```cmd
python -m pip install -r requirements.txt
python meeting_audio_converter.py
```

## EXE 빌드

```cmd
python -m PyInstaller --onefile --noconsole --collect-all tkinterdnd2 meeting_audio_converter.py
```

배포 시 FFmpeg의 라이선스 및 재배포 조건을 확인합니다.
