# 🌱 Antiy-Zunda — Desktop Live2D Zundamon Companion

[![Python](https://img.shields.io/badge/Python-3.10%2B-blue?logo=python)](https://python.org)
[![Platform](https://img.shields.io/badge/Platform-Windows%2010%20%2F%2011-0078D6?logo=windows)](https://microsoft.com)
[![Live2D](https://img.shields.io/badge/Live2D-Cubism%204-green)](https://www.live2d.com/)
[![VOICEVOX](https://img.shields.io/badge/VOICEVOX-Zundamon%20(%E3%81%9A%E3%82%93%E3%81%A0%E3%82%82%E3%82%93)-success)](https://voicevox.hiroshiba.jp/)
[![Antigravity](https://img.shields.io/badge/Antigravity%20CLI-Ready-brightgreen)](https://github.com)

A transparent **Live2D Zundamon (ずんだもん) desktop mascot** that resides on your Windows desktop, functioning as a **real-time voice synthesis and lipsync companion for Google DeepMind Antigravity CLI and AI coding agents**.

---

## ✨ Features

- 🎭 **Real-Time Emotion Engine**: Analyzes conversation context and keywords in real time to match 8 core emotional states (Tears/Error, Shock/Pale, Pout/Cheeks, Cheer/Hooray, Boast/Smug, Thinking/Diagnosis, Love/Touched, Chop Action), synchronizing Live2D expressions, body motions, and VOICEVOX voice tones (Sweet, Normal, Tsundere, Pitch, Intonation).
- 🪟 **Fully Transparent Desktop Overlay**: Implements Windows DWM Glass frame transparency for a borderless, transparent desktop mascot floating seamlessly above apps.
- 💭 **Pure White Modern Speech Bubble UI**: Displays pop-up speech bubbles above character's head during speech (supports 3 display modes: `💭 Comic Bubble`, `📝 Bottom Subtitle`, `❌ Hidden`).
- 👀 **Real-Time Mouse Cursor & Head Tracking**: Tracks global and local mouse cursor coordinates to dynamically adjust eye gaze (`ParamEyeBallX/Y`) and head orientation (`ParamAngleX/Y/Z`), gently returning to center when idle.
- ⚡ **Automated Resource Overload Alert**: Voice and expression alert triggered when CPU or RAM usage exceeds 90% to protect system stability (toggleable in settings).
- 🗣️ **VOICEVOX Neural Speech Synthesis**: Transliterates Korean inputs into Japanese phonetic kana via a dedicated phoneme engine (`hangul_to_kana.py`) for ultra-fast, natural Zundamon speech synthesis.
- 🎚️ **Real-Time Voice Parameter Controls**: Sliders and presets for Speed, Intonation, Pitch, Volume, and Pause duration in the settings window.
- ⏱️ **Optimized Speech Tempo & Pauses**: Compressed mora pause intervals for crisp, non-lagging Korean phonetic speech.
- 👄 **Web Audio Real-Time Lip-Sync**: Uses `AnalyserNode` frequency spectrum analysis to drive mouth movement parameters (`ParamMouthOpenY`) in real time.
- ⚙️ **4-Tab Modern Settings Window (`Ctrl + ,`)**: Dedicated configuration window featuring `✨ Emotion Test`, `🎭 Character & Display`, `💬 Subtitle & Dialogue`, and `🎙️ Voice & Lip-Sync Test`.
- 🛡️ **Chromium WebView2 Cache-Busting**: Strict no-cache headers and timestamp query parameters (`?_v=...`) guarantee immediate UI refresh upon configuration changes.
- 🤖 **Antigravity CLI Integration**: Responds via `/zundamon` slash command with Zundamon persona (`~noda`, `~nanoda`) and speaks directly through the desktop mascot.
- 🪶 **Ultra-Lightweight Background Footprint**: Minimized background threads with memory consumption hovering around 50MB, allowing seamless multitasking during development and gaming.

---

## 🚀 Quick Start

### 1. Clone the Repository
```bash
git clone https://github.com/dotori-007/antiy-zunda.git
cd antiy-zunda
```

### 2. One-Click Setup
Run `setup.bat` in the project root:
```cmd
setup.bat
```
> `setup.bat` automatically completes the following:
> 1. Installs required Python packages (`bottle`, `pywebview`, `pythonnet`)
> 2. Registers a Windows Task Scheduler background job (`ZundamonMascot`)
> 3. Binds the Antigravity CLI skill definition (`%USERPROFILE%\.gemini\config\skills\zundamon\SKILL.md`)

### 3. VOICEVOX Engine
* Download and install the free official engine from [VOICEVOX Official Site](https://voicevox.hiroshiba.jp/). The mascot automatically detects and connects to the local service upon launch.

---

## 🎮 Controls & Shortcuts

With the mascot window focused:

| Category | Shortcut / Action | Description |
| :--- | :--- | :--- |
| **Mouse Actions** | `Left/Right Click Drag` | Move mascot window freely across desktop |
| **Emotions** | `Ctrl + 1 ~ 9` | Toggle Smile, Grin, Shy, Surprised, Pout, Sad, Sleepy, Sparkle, Excited |
| | `Ctrl + 0` | Reset to default expression (preserves zoom level) |
| **Scale & Size** | `Ctrl + + / -` | Scale character model in 0.2 increments (0.4x ~ 3.0x) |
| | `Ctrl + [ / ]` | Adjust canvas window dimensions (±50px) |
| **Subtitles & Modes** | `Ctrl + U` | Toggle live subtitles ON / OFF |
| | `Ctrl + J` | Cycle subtitle display mode (Speech Bubble ↔ Bottom Subtitle ↔ Hidden) |
| **Settings** | `Ctrl + ,` | Open / close dedicated settings window (`Esc` or `Ctrl+,` to close inside settings) |

---

## 📁 Project Structure

```
antiy-zunda/
├── app.py                # Main desktop overlay window & HTTP API server
├── emotion_engine.py     # Real-time emotion keyword analysis & voice mapping
├── hangul_to_kana.py     # Korean-to-Kana phonetic transliteration engine
├── speak.py              # CLI speech synthesis trigger script
├── index.html            # Live2D Cubism canvas & transparent mascot UI
├── settings.html         # 4-tab configuration & control panel UI
├── setup.bat             # One-click Windows setup batch script
├── setup.ps1             # PowerShell installation script
├── start_zundamon.bat    # Mascot launcher script
├── start_zundamon.vbs    # Headless background launcher script
├── requirements.txt      # Python dependencies
├── model/                # Live2D Cubism model assets (.moc3, textures, motions)
├── static/               # Audio visualizer, fonts, and styling assets
└── skill/                # Antigravity CLI skill integration files
```

---

## 📄 License

This project is licensed under the [MIT License](LICENSE).  
Live2D character model and VOICEVOX voice library are subject to their respective terms of use (Tohoku Zunko / Zundamon guidelines).