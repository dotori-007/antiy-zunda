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
- 💭 **순백색 모던 말풍선(Speech Bubble) UI**: 발화 시 캐릭터 머리 위에 깔끔한 화이트 팝업 말풍선 출력 (설정 창에서 `💭 만화 말풍선` / `📝 하단 자막` / `❌ 숨김` 3가지 모드 선택 가능).
- 👀 **실시간 마우스 시선 & 고개 추적**: 전역 및 로컬 마우스 커서 위치를 실시간 추적하여 눈동자(`ParamEyeBallX/Y`)와 고개(`ParamAngleX/Y/Z`)가 따라 움직이며, 장시간 미조작 시 부드럽게 정면 응시.
- ⚡ **PC 리소스 과부하 자동 감지 경고**: CPU 또는 RAM 점유율이 90%를 초과할 경우 즌다몬이 놀란 표정으로 음성 경고를 출력하여 시스템 보호 유도.
- 🗣️ **VOICEVOX 기반 고품질 음성 합성**: 한국어 문장을 자체 규칙 기반 음소 엔진(`hangul_to_kana.py`)을 거쳐 즌다몬 음성(ID: 3)으로 초고속 합성 및 재생합니다.
- 👄 **Web Audio 실시간 립싱크 (Lip-Sync)**: `AnalyserNode` 주파수 분석을 통해 발화 음성에 맞춰 실시간으로 입 모양(`ParamMouthOpenY`)을 정밀하게 동기화합니다.
- ⚙️ **실시간 연동 독립 환경설정 창**: 화면을 가리지 않는 독립된 전용 윈도우(`Ctrl + P` 또는 `Ctrl + ,`)를 통해 표정, 배율, 캔버스 크기, 말풍선 모드, 과부하 경고를 실시간으로 조작할 수 있습니다.
- 🤖 **Antigravity CLI 완벽 연동**: `/zundamon` 명령어를 통해 AI 에이전트가 즌다몬 페르소나(`~인 것이다`)로 대화하며 화면 속 즌다몬의 음성으로 직접 대답합니다.

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

### 3. VOICEVOX 엔진 준비
* [VOICEVOX 공식 홈페이지](https://voicevox.hiroshiba.jp/)에서 무료 설치 프로그램을 다운로드하여 설치해 두시면, 마스코트 기동 시 백그라운드에서 자동으로 감지하여 실행합니다.

---

## 🎮 조작법 및 단축키 (Controls & Shortcuts)

마스코트 창을 클릭하여 활성화한 상태에서 아래 조작 및 단축키를 사용할 수 있습니다:

| 분류 | 조작 / 단축키 | 기능 설명 |
| :--- | :--- | :--- |
| **마우스 조작** | `마우스 좌클릭 드래그` | 화면 내 원하는 위치로 마스코트 창 이동 |
| | `캐릭터 클릭` | 무작위 반응 모션 및 대사 발화 |
| **표정 변경** | `Ctrl + 1 ~ 9` | 미소, 활짝, 부끄, 깜짝, 삐짐, 시무룩, 졸림, 초롱, 신남 표정 전환 |
| | `Ctrl + 0` | 기본 표정 초기화 (배율 유지) |
| **크기 및 배율** | `Ctrl + + / -` | 캐릭터 모델 배율 0.2 단위 확대 / 축소 (0.4x ~ 3.0x) |
| | `Ctrl + [ / ]` | 캔버스 창 크기 조절 (±50px) |
| **자막 및 설정** | `Ctrl + U` | 자막 표시 ON / OFF 토글 |
| | `Ctrl + P` 또는 `Ctrl + ,` | 독립 환경설정 창 열기 / 맨 앞으로 활성화 |

---

## ⚙️ 독립 환경설정 창 (Settings Window)

`Ctrl + P` 또는 `Ctrl + ,` 단축키를 누르면 화면을 가리지 않는 전용 설정 윈도우가 열립니다. `BroadcastChannel`을 통해 설정 창에서 변경한 모든 내용이 Live2D 화면에 **즉시 실시간으로 반영**됩니다:

- 🎭 **캐릭터 스타일 / 표정 제어**: 9종 표정 스타일 칩 및 `↺ 기본 스타일로 초기화 (Ctrl + 0)`
- 🎛️ **정밀 파라미터 인스펙터**: 슬라이더 + 수치 박스 + ↺(리셋) 버튼 레이아웃
  - **캐릭터 배율**: `0.4x ~ 3.0x` (0.2 스텝), `+0.2 확대` / `-0.2 축소` / `1.0x 리셋`
  - **캔버스 크기**: 너비/높이 슬라이더 및 프리셋 (420×580 / 560×750 / 700×900)
  - **실시간 자막**: 10px~36px 슬라이더, ON/OFF 토글 스위치, 실시간 미리보기
- 💬 **발화 테스트 스크립트 셀**: `▶` 재생 버튼 + 텍스트 인풋으로 즉시 음성 합성 및 립싱크 출력

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

## 📝 최근 업데이트 내역 (Changelog)

### v1.3.0
- 💭 **순백색(Pure White) 모던 말풍선 UI 도입**: 캐릭터 상단에 깔끔한 화이트 팝업 말풍선과 꼬리표 출력, 대사 종료 후 1.2초간 부드럽게 유지 후 페이드아웃
- ⚡ **실시간 PC 시스템 리소스 과부하 감지 (`ResourceMonitor`)**: Windows 네이티브 API(`GetSystemTimes`, `GlobalMemoryStatusEx`) 기반 CPU/RAM 90% 초과 감지 시 자동 음성 경고
- 🛡️ **작업 스케줄러 유휴 종료 문제 해결**: PC 유휴 해제 시 마스코트가 강제 종료되던 `StopOnIdleEnd` 제약 제거 및 무제한 상주 정책 확립
- 👀 **시선 추적 최적화 및 상호작용 개선**: 전역/로컬 커서 부드러운 보간 추적 및 캐릭터 클릭/더블클릭 반응 동작 강화
- ⚙️ **설정 창 대사 표시 모드 칩 추가**: `💭 만화 말풍선` / `📝 하단 자막` / `❌ 숨김` 3가지 모드 즉시 전환 가능

### v1.2.1
- 🎨 **설정 창 UI 간소화 및 콤팩트화**: 상단 헤더 바와 캐릭터 배너 카드를 완전히 제거하여 여백 낭비 없는 580px 최적 뷰 제공
- 🧹 **UI 텍스트 전면 정돈**: 타이틀 및 UI 레이블에서 불필요한 명칭을 전면 제거하고 조작 컨트롤 중심으로 직관성 극대화
- 🎯 **3단 핵심 컨트롤 구성**: 9종 표정 스타일 칩 ➔ 정밀 파라미터 인스펙터(배율/너비/높이/자막) ➔ 립싱크 발화 테스트 셀

### v1.2.0
- ⚙️ **독립 환경설정 윈도우 분리 (`settings.html`)**: 화면 내부 모달을 걷어내고 `Ctrl + P` 단축키로 호출 가능한 독립 설정 창 구축
- 🔄 **초고속 실시간 양방향 연동**: `BroadcastChannel` 기반으로 지연 없이 실시간 설정 반영
- 🔍 **배율 조절 레이트 0.2 단위 정돈**: 0.4x ~ 3.0x 범위에서 0.2 배수로 단정하게 조작되도록 개선
- 🛡️ **배율 조작 시 초고배율 튐 버그 수정**: PixiJS 가변 렌더링 치수 대신 불변 원본 캔버스 치수(`modelBaseWidth/Height`)를 캐싱하여 배율 변경 시 튀거나 깜빡이는 현상 원천 차단
- 🎭 **표정 초기화 & 배율 초기화 분리**: 표정 초기화(`Ctrl + 0`) 시 사용자가 조절한 캐릭터 배율이 초기화되지 않도록 분리
- 💬 **자막 가독성 및 조작 개선**: 배경 박스 없는 깔끔한 단일 텍스트 + 소프트 드롭 섀도우 적용 및 `Ctrl + U` 토글 추가
- 📦 **완전 독립 포터블 패키징**: 외부 의존성 제거, 로컬 모델 번들링, 원클릭 `setup.bat` 환경 구성 및 작업 스케줄러 배터리 제약 해제

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
├── settings.html              # 실시간 연동 독립 환경설정 창 UI
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
