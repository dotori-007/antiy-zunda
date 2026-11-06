# 🌱 즌다몬 데스크톱 Live2D 컴패니언 (antiy-zunda)

[![Python](https://img.shields.io/badge/Python-3.10%2B-blue?logo=python)](https://python.org)
[![Platform](https://img.shields.io/badge/Platform-Windows%2010%20%2F%2011-0078D6?logo=windows)](https://microsoft.com)
[![Live2D](https://img.shields.io/badge/Live2D-Cubism%204-green)](https://www.live2d.com/)
[![VOICEVOX](https://img.shields.io/badge/VOICEVOX-Zundamon%20(ずんだもん)-success)](https://voicevox.hiroshiba.jp/)
[![Antigravity](https://img.shields.io/badge/Antigravity%20CLI-Ready-brightgreen)](https://github.com)

Windows 바탕화면 위에 상주하는 투명 **Live2D 즌다몬(ずんだもん) 데스크톱 마스코트**이자, **Google DeepMind Antigravity CLI AI 에이전트 연동용 실시간 음성/립싱크 컴패니언**입니다.

---

## ✨ 주요 기능 (Features)

- 🎭 **실시간 감정 대응 엔진 (Emotion Mapping Engine)**: 대사의 맥락과 감정 키워드를 AI가 실시간 분석하여 8대 감정(눈물/오류, 충격/새파람, 삐짐/볼빵빵, 환호/만세, 당당/허세, 생각/진단, 사랑/감동, 촙 액션)에 맞춰 **Live2D 표정, 전신 모션, VOICEVOX 목소리 톤(아마아마, 노멀, 츤츤, 피치, 억양)**을 전신 유기적으로 연동합니다.
- 🪟 **완전 투명 데스크톱 오버레이**: Windows DWM Glass 프레임 투명화를 통해 배경 없는 투명 윈도우로 화면 위에 자연스럽게 상주합니다.
- 💭 **순백색 모던 말풍선(Speech Bubble) UI**: 발화 시 캐릭터 머리 위에 깔끔한 화이트 팝업 말풍선 출력 (설정 창에서 `💭 만화 말풍선` / `📝 하단 자막` / `❌ 숨김` 3가지 모드 선택 가능).
- 👀 **실시간 마우스 시선 & 고개 추적**: 전역 및 로컬 마우스 커서 위치를 실시간 추적하여 눈동자(`ParamEyeBallX/Y`)와 고개(`ParamAngleX/Y/Z`)가 따라 움직이며, 장시간 미조작 시 부드럽게 정면 응시.
- ⚡ **PC 리소스 과부하 자동 감지 경고**: CPU 또는 RAM 점유율이 90%를 초과할 경우 즌다몬이 놀란 표정으로 음성 경고를 출력하여 시스템 보호 유도 (자막·대사 설정 탭에서 ON/OFF 가능).
- 🗣️ **VOICEVOX 기반 고품질 음성 합성**: 한국어 문장을 자체 규칙 기반 음소 엔진(`hangul_to_kana.py`)을 거쳐 즌다몬 음성으로 초고속 합성 및 재생합니다.
- 🎚️ **음성 파라미터 실시간 제어**: 화속(Speed), 억양(Intonation), 음높이(Pitch), 음량(Volume), 쉼표 간격(Pause)을 설정 창에서 슬라이더 및 프리셋으로 취향에 맞게 실시간 조절.
- ⏱️ **발화 템포 & 쉬는 시간 최적화**: 띄어쓰기 mora 휴지 기간을 압축하여 늘어짐 없는 경쾌한 한국어 발화 템포 확립.
- 👄 **Web Audio 실시간 립싱크 (Lip-Sync)**: `AnalyserNode` 주파수 분석을 통해 발화 음성에 맞춰 실시간으로 입 모양(`ParamMouthOpenY`)을 정밀하게 동기화합니다.
- ⚙️ **4대 탭 구조의 모던 환경설정 창 (`Ctrl + ,`)**: `✨ 감정표현 테스트`, `🎭 캐릭터 & 디스플레이`, `💬 자막 & 대사 설정`, `🎙️ 음성 & 립싱크 테스트` 4개 탭으로 완벽 재구조화된 독립 설정 창.
- 🛡️ **Chromium WebView2 캐시 버스터 & 안티캐시**: 엄격한 안티캐시 헤더와 실시간 타임스탬프 파라미터(`?_v=...`)로 설정 UI 변경 시 100% 즉시 반영 보장.
- 🤖 **Antigravity CLI 완벽 연동**: `/zundamon` 명령어를 통해 AI 에이전트가 즌다몬 페르소나(`~인 것이다`)로 대화하며 화면 속 즌다몬의 음성으로 직접 대답합니다.
- 🪶 **초경량 백그라운드 상주**: 불필요한 백그라운드 스레드를 제거하여 메모리 점유율을 50MB 수준으로 최소화, 개발 및 게임 중에도 부하 없이 상주 가능.

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
| **마우스 조작** | `마우스 좌클릭/우클릭 드래그` | 화면 내 원하는 위치로 마스코트 창 이동 (터치 반응은 비활성화) |
| **표정 변경** | `Ctrl + 1 ~ 9` | 미소, 활짝, 부끄, 깜짝, 삐짐, 시무룩, 졸림, 초롱, 신남 표정 전환 |
| | `Ctrl + 0` | 기본 표정 초기화 (배율 유지) |
| **크기 및 배율** | `Ctrl + + / -` | 캐릭터 모델 배율 0.2 단위 확대 / 축소 (0.4x ~ 3.0x) |
| | `Ctrl + [ / ]` | 캔버스 창 크기 조절 (±50px) |
| **자막 및 모드** | `Ctrl + U` | 실시간 자막 ON / OFF 토글 |
| | `Ctrl + J` | 자막 표시 형태 순환 전환 (말풍선 ↔ 하단 자막 ↔ 자막 숨김) |
| **환경설정 창** | `Ctrl + ,` | 독립 환경설정 창 토글 열기 / 닫기 (설정 창 내에서는 `Esc` 또는 `Ctrl+,`로 닫기) |

---

## ⚙️ 4대 탭 독립 환경설정 창 (Settings Window)

`Ctrl + ,` 단축키를 누르면 화면을 가리지 않는 `540 × 650` 크기의 전용 설정 윈도우가 열립니다. `BroadcastChannel`을 통해 설정 창에서 변경한 모든 내용이 Live2D 화면에 **즉시 실시간으로 반영**됩니다:

1. **✨ 감정표현 테스트 탭 (`#tab-emotions`)**:
   - **자유 대사 감정 분석 테스트**: 한국어 대사를 입력하고 AI 감정 엔진이 자동 감지하거나 드롭다운으로 수동 지정하여 즉시 시연
   - **8대 감정 원클릭 프리셋 카드**: 눈물/오류, 충격/새파람, 삐짐/볼빵빵, 환호/성공, 당당/허세, 생각/진단, 사랑/감동, 촙 액션을 카드 형태로 구성하여 `[▶ 재생]` 버튼으로 즉시 테스트
2. **🎭 캐릭터 & 디스플레이 탭 (`#tab-model`)**:
   - 9종 스타일/표정 제어 칩 및 초기화(`Ctrl + 0`)
   - **배율 (Scale)**: `0.4x ~ 3.0x` (0.2 스텝), `+0.2 확대` / `-0.2 축소` / `1.0x 리셋`
   - **너비/높이 (Width/Height)**: 캔버스 크기 슬라이더 및 프리셋 칩 (420, 560, 700, 850px / 580, 750, 900, 1100px)
3. **💬 자막 & 대사 설정 탭 (`#tab-subtitles`)**:
   - **컴패니언 자막 모드 활성화 스위치** (`Ctrl + J`)
   - **대사 표시 방식**: `💭 만화 말풍선` / `📝 하단 자막` / `❌ 숨김` 칩 선택
   - **글자 크기 (Font Size)**: 10px ~ 36px 슬라이더 및 12, 14, 17, 20px 프리셋 칩
   - **실시간 텍스트 표시 스위치** (`Ctrl + U`) 및 실시간 자막 미리보기 박스
   - **⚡ PC 리소스 과부하 자동 감지 경고 스위치**
4. **🎙️ 음성 & 립싱크 테스트 탭 (`#tab-voice`)**:
   - **실시간 음성 합성 & 립싱크 테스트 셀**: 대사 입력 인풋 + `▶` 재생 버튼으로 즉시 발화
   - **VOICEVOX 5대 음성 파라미터 제어**: 화속(0.5~2.0x), 억양(0.0~2.0), 음높이(-0.15~0.15), 음량(0.2~2.0), 쉼표 간격(0.10~1.50x) 슬라이더, 프리셋 칩 및 ↺(리셋) 버튼

---

## 🤖 Antigravity CLI 연동 가이드

`setup.bat` 실행 후, Antigravity CLI에서 다음과 같이 부르면 즉시 활성화됩니다:

```text
> /zundamon
```

에이전트는 즌다몬의 페르소나를 장착하고 모든 답변을 한국어 `~인 것이다` 종결어미로 변환하며, 내부적으로 아래 발화 스트림 명령을 내려 데스크톱 즌다몬의 음성 및 립싱크로 답변합니다:

```powershell
# 일반 자동 감정 분석 발화
python speak.py "알겠는 것이다! 즌다몬이 찾아온 것이다!"

# 감정 명시 발화 (--emotion 플래그)
python speak.py --emotion joy_cheer "모든 기능 개발에 대성공한 것이다! 만세!"
python speak.py --emotion crying "오류가 발생해서 너무 슬픈 것이다 ㅠㅠ"
```

---

## 📝 최근 업데이트 내역 (Changelog)

### v1.5.0
- 🎭 **실시간 감정 대응 엔진 (`emotion_engine.py`) 전면 구축**:
  - 한국어 텍스트 문맥/키워드 감정 분석을 통한 8대 감정 카테고리(`crying`, `panic`, `angry_pout`, `joy_cheer`, `smug_pride`, `thinking`, `love_shy`, `chop_action`) 자동 감지
  - 대사 감정에 대응하여 Live2D 표정(exp), 전신 모션(motion), VOICEVOX 목소리 스타일(1:아마아마, 3:노멀, 7:츤츤) 및 억양/피치/속도 실시간 동기화
  - 네이티브 `.exp3.json` 및 `.motion3.json` 모션 엔진 전환으로 반투명 잔상 및 신체 결손(귀/팔 사라짐) 버그 원천 차단
- ⚙️ **설정창 (Settings UI) 4대 탭 구조 전면 개편 (`settings.html`)**:
  - **`✨ 감정표현 테스트` 탭 (신설)**: 자유 대사 감정 분석 테스트 + 8대 감정 원클릭 프리셋 카드 즉시 재생
  - **`🎭 캐릭터 & 디스플레이` 탭 (슬림화)**: 배율(Scale), 너비(Width), 높이(Height) 슬라이더 및 표정 칩만 깔끔하게 유지
  - **`💬 자막 & 대사 설정` 탭 (통합)**: 자막 모드 활성화(Ctrl+J), 대사 표시 방식(말풍선/하단/숨김), 폰트 크기, 실시간 텍스트 토글(Ctrl+U), 실시간 미리보기 박스 및 **PC 리소스 과부하 자동 감지 경고 스위치** 통합
  - **`🎙️ 음성 & 립싱크 테스트` 탭 (병합)**: 실시간 음성 합성 & 립싱크 테스트 입력창 + VOICEVOX 5대 파라미터 제어(속도/억양/피치/볼륨/쉼표)를 하나의 탭으로 병합
- 🛡️ **Edge WebView2 안티캐시 강화 및 최적화 (`app.py`)**:
  - 엄격한 HTTP 캐시 제어 헤더 반환 (`Cache-Control: no-cache, no-store, must-revalidate, max-age=0`)
  - 창 생성 시 타임스탬프(`?_v=...`) 쿼리 스트링 부여로 Chromium 디스크 캐시 무효화
  - 설정창 크기를 `540 × 650`으로 넉넉하게 확장하여 가로 스크롤 없이 시원한 4대 탭 뷰 제공

### v1.4.1
- 🇰🇷 **자막 및 말풍선 한국어 원문 표시 보장 (버그 수정)**: VOICEVOX 음성 합성용 가타카나 텍스트가 화면 자막 및 말풍선에 노출되던 문제를 수정하여, 발화 시 한국어 원문이 100% 그대로 깔끔하게 출력되도록 파이프라인 분리
- 🗣️ **기본 폴백 발화 한국어화**: `speak.py`의 파라미터 미전달 시 기본 대사를 "보쿠는 즌다몬인 것이다!"로 한국어 통일

### v1.4.0
- 🎙️ **VOICEVOX 음성 파라미터 실시간 제어 UI 탑재**: 화속(Speed), 억양(Intonation), 음높이(Pitch), 음량(Volume), 쉼표 간격(Pause)을 설정 창(Ctrl + ,)에서 슬라이더 및 프리셋 칩으로 즉시 조정 가능
- ⏱️ **띄어쓰기 쉬는 시간 최적화**: 문장 띄어쓰기 mora 휴지 기간을 압축하여 늘어짐 없는 경쾌한 발화 템포 확립
- 🪶 **VR/Spotify 비주얼라이저 모드 제거 및 초경량화**: 미사용 백그라운드 스레드 및 대형 의존성 정리로 메모리 점유율을 54MB 수준으로 대폭 경량화
- ⌨️ **단축키 전면 정돈 & 토글 개선**: 설정 창 단축키를 Ctrl + , 전용으로 통합하고 설정 창 내부에서도 Esc 또는 Ctrl + , 입력 시 바로 닫히도록 개선

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
├── emotion_engine.py          # [신규] 8대 감정 자동 분석 및 음성/모션 매핑 엔진
├── index.html                 # 렌더링 캔버스, 트래킹, 립싱크, 자막 UI
├── settings.html              # 실시간 연동 4대 탭 독립 환경설정 창 UI
├── hangul_to_kana.py          # 한국어 -> 일본어 가타카나 발음 변환 규칙 엔진
├── speak.py                   # 실시간 감정 음성 발화 CLI 클라이언트
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
