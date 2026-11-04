# 🌱 즌다몬 데스크톱 Live2D 컴패니언 (antiy-zunda)

[![Python](https://img.shields.io/badge/Python-3.10%2B-blue?logo=python)](https://python.org)
[![Platform](https://img.shields.io/badge/Platform-Windows%2010%20%2F%2011-0078D6?logo=windows)](https://microsoft.com)
[![Live2D](https://img.shields.io/badge/Live2D-Cubism%204-green)](https://www.live2d.com/)
[![VOICEVOX](https://img.shields.io/badge/VOICEVOX-Zundamon%20(ずんだもん)-success)](https://voicevox.hiroshiba.jp/)
[![Antigravity](https://img.shields.io/badge/Antigravity%20CLI-Ready-brightgreen)](https://github.com)

Windows 바탕화면 위에 상주하는 투명 **Live2D 즌다몬(ずんだもん) 데스크톱 마스코트**이자, **Google DeepMind Antigravity CLI AI 에이전트 연동용 실시간 음성/립싱크 컴패니언**입니다.

---

## ✨ 주요 기능 (Features)

- 🪟 **완전 투명 데스크톱 오버레이**: Windows DWM Glass 프레임 투명화를 통해 배경 없는 투명 윈도우로 화면 위에 자연스럽게 상주합니다.
- 👀 **전체 화면 실시간 마우스 추적**: 모니터 전체 영역의 마우스 커서 위치를 실시간으로 추적하여 시선과 고개를 자연스럽게 회전합니다.
- 🗣️ **VOICEVOX 기반 고품질 음성 합성**: 한국어 문장을 자체 규칙 기반 음소 엔진(`hangul_to_kana.py`)을 거쳐 즌다몬 음성(ID: 3)으로 합성 및 재생합니다.
- 👄 **Web Audio 실시간 립싱크 (Lip-Sync)**: `AnalyserNode` 주파수 분석을 통해 발화 음성에 맞춰 실시간으로 입 모양(`ParamMouthOpenY`)을 정밀하게 동기화합니다.
- 💬 **실시간 음성 자막**: 발화 음성에 맞춘 텍스트 자막 출력 (단축키 `Ctrl + U`로 ON/OFF 토글, 글자 크기 조절 지원).
- 🤖 **Antigravity CLI 완벽 연동**: `/zundamon` 명령어를 통해 AI 에이전트가 즌다몬 페르소나로 대화하며 화면 속 즌다몬의 음성으로 직접 대답합니다.
- ⌨️ **단축키 및 환경설정**: 표정 9종 변경, 모델 확대/축소, 캔버스 크기 조절, 마우스 드래그 이동 및 설정 패널을 지원합니다.

---

## 🚀 빠른 시작 (Quick Start)

### 1. 저장소 복제 (Clone)
```bash
git clone https://github.com/dotori-007/antiy-zunda.git
cd antiy-zunda
```

### 2. 원클릭 환경 설치 (Setup)
폴더 내 `setup.bat`를 실행합니다:
```cmd
setup.bat
```
> `setup.bat`는 아래 작업을 자동으로 수행합니다:
> 1. Python 라이브러리(`bottle`, `pywebview`, `pythonnet`) 자동 설치
> 2. Windows 작업 스케줄러(`ZundamonMascot`) 백그라운드 작업 등록
> 3. 현재 PC의 Antigravity CLI 스킬 폴더(`%USERPROFILE%\.gemini\config\skills\zundamon\SKILL.md`)에 자동 바인딩

### 3. VOICEVOX 엔진 설치
* [VOICEVOX 공식 홈페이지](https://voicevox.hiroshiba.jp/)에서 무료 설치 프로그램을 다운로드하여 설치해 두시면, 마스코트 기동 시 백그라운드에서 자동으로 감지하여 실행합니다.

---

## 🎮 조작법 및 단축키 (Controls & Shortcuts)

마스코트 창을 클릭하여 활성화한 상태에서 아래 조작 및 단축키를 사용할 수 있습니다:

| 분류 | 조작 / 단축키 | 기능 설명 |
| :--- | :--- | :--- |
| **마우스 조작** | `마우스 좌클릭 드래그` | 화면 내 원하는 위치로 마스코트 창 이동 |
| **표정 변경** | `Ctrl + 1 ~ 9` | 미소, 활짝, 부끄, 깜짝, 삐짐, 시무룩, 졸림, 초롱, 신남 표정 전환 |
| | `Ctrl + 0` | 기본 표정 및 배율 초기 상태 리셋 |
| **크기 및 배율** | `Ctrl + + / -` | 캐릭터 모델 배율 확대 / 축소 (±0.1) |
| | `Ctrl + [ / ]` | 캔버스 창 크기 조절 (±50px) |
| **자막 및 설정** | `Ctrl + U` | 자막 표시 ON / OFF 토글 |
| | `Ctrl + P` 또는 `Ctrl + ,` | 상세 설정 패널 (캔버스 크기 프리셋, 표정 선택, 자막 크기 조절) |

---

## 🤖 Antigravity CLI 연동 가이드

`setup.bat` 실행 후, Antigravity CLI에서 다음과 같이 부르면 즉시 활성화됩니다:

```text
> /zundamon
```

에이전트는 즌다몬의 페르소나를 장착하고 모든 답변을 한국어 `~인 것이다` 종결어미로 변환하며, 내부적으로 아래 발화 스트림 명령을 내려 데스크톱 즌다몬의 음성 및 립싱크로 답변합니다:

```powershell
python speak.py "알겠는 것이다! 즌다몬이 찾아온 것이다!"
```

---

## 📁 프로젝트 구조 (Repository Structure)

```text
antiy-zunda/
├── model/                     # 내장 Live2D Cubism 4 모델 에셋
│   ├── zundamon.moc3
│   ├── zundamon.model3.json
│   ├── zundamon.2048/
│   ├── expressions/
│   └── motions/
├── static/                    # 코어 웹 런타임 라이브러리
│   ├── pixi.min.js
│   ├── cubism4.min.js
│   └── live2dcubismcore.min.js
├── skill/                     # Antigravity CLI 스킬 템플릿
│   └── SKILL.template.md
├── app.py                     # Bottle 백엔드 서버 & PyWebView 투명 윈도우
├── index.html                 # 렌더링 캔버스, 트래킹, 립싱크, 자막 UI
├── hangul_to_kana.py          # 한국어 -> 일본어 가타카나 발음 변환 규칙 엔진
├── speak.py                   # 실시간 음성 발화 CLI 클라이언트
├── start_zundamon.bat         # 콘솔 기동 배치 파일
├── start_zundamon.vbs         # 무음 백그라운드 실행기
├── setup.bat                  # 신규 PC 자동 설치 배치 파일
├── setup.ps1                  # 신규 PC 자동 설치 파워셸 스크립트
├── requirements.txt           # Python 필수 패키지 목록
├── .gitignore                 # Git 제외 파일 목록
└── README.md                  # 저장소 안내 문서
```

---

## 📄 라이선스 및 크레딧 (Credits & License)

- **Character & Voice**: [Tohoku Zunko Project (東北ずん子・ずんだもんプロジェクト)](https://zunko.jp/) / [VOICEVOX: ずんだもん](https://voicevox.hiroshiba.jp/)
- **Live2D Cubism**: Live2D Inc.
- **License**: MIT License (캐릭터 음성 및 모델 사용 시 캐릭터 공식 가이드라인을 준수해 주세요)
