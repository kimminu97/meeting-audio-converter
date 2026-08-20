# Meeting Audio Converter

**GALA IT팀 | Version 0.1.3**

tl;dv에서 생성된 WebM 회의 녹음 파일을 M4A로 변환하는 Windows용 GUI 프로그램입니다.

회의 녹음 파일을 AI 회의록 서비스에서 활용하기 위해 필요한 파일 변환 과정을 간소화하는 것을 목적으로 개발했습니다.

---

## 1. 프로젝트 개요

### 개발 배경

기존에는 WebM 파일을 다른 서비스에서 활용하기 위해 FFmpeg 명령어를 직접 실행해야 했습니다.

일반 사용자가 FFmpeg를 설치하고 CMD에서 명령어를 입력하는 과정은 불편하기 때문에, 파일을 선택하거나 드래그 앤 드롭하는 것만으로 변환할 수 있는 GUI 프로그램을 개발했습니다.

### 목표

```text
WebM 파일
   ↓
Meeting Audio Converter
   ↓
M4A 파일
   ↓
AI 회의록 서비스 업로드
```

개발자가 아닌 사용자도 별도의 명령어 없이 사용할 수 있도록 하는 것이 목표입니다.

---

## 2. 주요 기능

- WebM → M4A 변환
- AAC 128kbps 출력
- WebM 파일 Drag & Drop
- 여러 파일 일괄 변환
- 파일 선택 방식 지원
- 원본 WebM 파일 유지
- 동일한 M4A 파일 존재 시 덮어쓰기 방지
- 변환 결과 폴더 바로 열기
- FFmpeg 오류 및 파일 오류 처리
- Windows GUI 제공
- Windows EXE 형태로 패키징
- EXE에 회사명, 제품명, 버전 정보 적용

---

## 3. 기술 스택

| 구분 | 기술 |
|---|---|
| Language | Python 3.14 |
| GUI | Tkinter |
| Drag & Drop | tkinterdnd2 |
| 변환 | FFmpeg |
| EXE 패키징 | PyInstaller |
| 버전 관리 | Git / GitHub |
| OS | Windows |

---

## 4. 프로그램 구조

```text
WebM 파일
    ↓
Python GUI
    ↓
FFmpeg
    ↓
AAC 128kbps
    ↓
M4A 파일
```

변환 과정은 사용자 PC에서 수행하며, 회의 녹음 파일을 별도의 온라인 변환 서버로 전송하지 않습니다.

---

## 5. 개발 과정

### ① FFmpeg 변환 검증

먼저 FFmpeg를 이용하여 WebM 파일을 M4A로 변환할 수 있는지 확인했습니다.

### ② Python GUI 구현

FFmpeg 명령어를 직접 입력하지 않아도 되도록 Tkinter 기반 GUI를 구현했습니다.

### ③ 사용자 편의성 개선

파일 선택뿐 아니라 Drag & Drop을 지원하고, 여러 파일을 한 번에 변환할 수 있도록 개선했습니다.

### ④ 예외 처리

FFmpeg 미설치, 잘못된 파일 형식, 중복 파일, 변환 실패 등의 상황을 처리했습니다.

### ⑤ Windows EXE 패키징

PyInstaller를 이용하여 Python 개발환경이 없는 사용자도 실행할 수 있는 Windows EXE 형태로 패키징했습니다.

EXE 파일명은 `회의음성변환기.exe`로 설정했습니다.

또한 Windows 파일 속성에 다음 정보를 표시하도록 구성했습니다.

```text
회사       : GALA IT팀
제품 이름  : 회의 음성 파일 변환기
파일 설명  : 회의 음성 WebM → M4A 변환 프로그램
파일 버전  : 0.1.3
제품 버전  : 0.1.3
```

---

## 6. 실행 방법

개발 환경에서 필요한 라이브러리를 설치합니다.

```cmd
python -m pip install -r requirements.txt
```

프로그램을 실행합니다.

```cmd
python meeting_audio_converter.py
```

FFmpeg는 프로그램과 같은 폴더에 `ffmpeg.exe`를 두거나 시스템 PATH에 등록합니다.

---

## 7. EXE 빌드

PyInstaller를 사용하여 Windows 실행파일을 생성할 수 있습니다.

```cmd
python -m PyInstaller --clean --onefile --noconsole --name "회의음성변환기" --icon "meeting_audio_converter.ico" --version-file "version_info.txt" --collect-all tkinterdnd2 meeting_audio_converter.py
```

빌드 결과:

```text
dist/
└── 회의음성변환기.exe
```

EXE 실행 시 FFmpeg가 필요하므로 현재 배포 방식은 다음과 같습니다.

```text
회의음성변환기_0.1.3/
├── 회의음성변환기.exe
└── ffmpeg.exe
```

두 파일을 같은 폴더에 두고 `회의음성변환기.exe`를 실행합니다.

※ 실제 배포 시 FFmpeg의 라이선스 및 재배포 조건을 확인합니다.

---

## 8. 프로젝트 상태

### 완료

- [x] WebM → M4A 변환
- [x] GUI 구현
- [x] Drag & Drop
- [x] 다중 파일 변환
- [x] 오류 처리
- [x] GitHub 소스 관리
- [x] 버전 관리
- [x] Windows EXE 빌드
- [x] EXE 아이콘 적용
- [x] EXE 회사/제품/버전 정보 적용
- [x] EXE + FFmpeg 실제 변환 테스트

### 예정

- [ ] 사내 사용자 테스트
- [ ] 사용자 매뉴얼 작성
- [ ] Version 1.0.0 정식 배포

---

## 9. Version

| Version | 주요 변경 |
|---|---|
| 0.1.0 | 초기 기능 및 GUI 구현 |
| 0.1.1 | UI Footer 수정 |
| 0.1.2 | Footer 레이아웃 개선 및 버전 정보 표시 |
| 0.1.3 | Windows EXE 빌드 설정, 아이콘 및 파일 버전 정보 추가 |

---

## 10. 프로젝트 목적

개발자가 직접 처리해야 했던 파일 변환 작업을 일반 사용자도 쉽게 사용할 수 있는 프로그램으로 전환하여, 회의 녹음 파일을 AI 회의록 서비스에 활용하는 과정을 단순화하는 것을 목표로 합니다.
