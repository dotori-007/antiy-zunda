import os
import sys
import time
import json
import random
import hashlib
import tempfile
import urllib.request
import urllib.parse
import threading
import subprocess
import ctypes
import traceback
from ctypes import wintypes
from bottle import Bottle, request, response, static_file, HTTPResponse
import webview




APP_DIR = os.path.dirname(os.path.abspath(__file__))
if APP_DIR not in sys.path:
    sys.path.insert(0, APP_DIR)

CRASH_LOG = os.path.join(APP_DIR, "crash.log")
def log_msg(msg):
    try:
        with open(CRASH_LOG, "a", encoding="utf-8") as f:
            f.write(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] {msg}\n")
    except Exception:
        pass

sys.excepthook = lambda t, v, tb: log_msg(f"Unhandled: {''.join(traceback.format_exception(t, v, tb))}")
threading.excepthook = lambda a: log_msg(f"Thread: {a.exc_type} {a.exc_value}\n{''.join(traceback.format_tb(a.exc_traceback))}")


WV2_STORAGE = os.path.join(tempfile.gettempdir(), "zundamon_wv2_data")
os.makedirs(WV2_STORAGE, exist_ok=True)

try:
    from hangul_to_kana import to_katakana
except Exception:
    def to_katakana(t): return t

try:
    from emotion_engine import analyze_emotion
except Exception as ee:
    log_msg(f"Failed to import emotion_engine: {ee}")
    def analyze_emotion(t, default_speaker=3):
        return {"key": "normal", "expression": "exp_smile", "motion": "mtnBody_yes", "params": {}, "speaker": default_speaker, "clean_text": t}
# Dynamic Model Directory Resolution
MODEL_DIR = os.path.join(APP_DIR, "model")
if not os.path.exists(MODEL_DIR):
    fallback_model = os.path.abspath(os.path.join(APP_DIR, "..", "zundamon_ja", "runtime"))
    if os.path.exists(fallback_model):
        MODEL_DIR = fallback_model

AUDIO_DIR = os.path.join(APP_DIR, "audio_cache")
VOICEVOX_URL = "http://127.0.0.1:50021"

def find_voicevox_engine():
    candidates = [
        os.path.join(APP_DIR, "vv-engine", "run.exe"),
        os.path.expandvars(r"%LOCALAPPDATA%\Programs\VOICEVOX\run.exe"),
        os.path.expandvars(r"%ProgramFiles%\VOICEVOX\run.exe"),
        os.path.abspath(os.path.join(APP_DIR, "..", "vv-engine", "run.exe")),
        os.path.expandvars(r"%USERPROFILE%\Downloads\voicevox-0.25.1-x64.nsis\vv-engine\run.exe"),
        r"C:\Users\kshja\Downloads\voicevox-0.25.1-x64.nsis\vv-engine\run.exe"
    ]
    for p in candidates:
        if os.path.exists(p):
            return p
    return None

os.makedirs(AUDIO_DIR, exist_ok=True)

try:
    user32 = ctypes.windll.user32
    user32.GetCursorPos.argtypes = [ctypes.c_void_p]
    user32.IsWindow.argtypes = [wintypes.HWND]
    user32.IsWindow.restype = wintypes.BOOL
    user32.GetWindowRect.argtypes = [wintypes.HWND, ctypes.c_void_p]
    user32.GetWindowRect.restype = wintypes.BOOL
    user32.SetWindowPos.argtypes = [wintypes.HWND, wintypes.HWND, ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int, wintypes.UINT]
    user32.SetWindowPos.restype = wintypes.BOOL
    user32.ReleaseCapture.argtypes = []
    user32.ReleaseCapture.restype = wintypes.BOOL
    user32.SendMessageW.argtypes = [wintypes.HWND, wintypes.UINT, ctypes.c_size_t, ctypes.c_ssize_t]
    user32.SendMessageW.restype = ctypes.c_ssize_t
except (AttributeError, Exception):
    user32 = None


class POINT(ctypes.Structure):
    _fields_ = [("x", ctypes.c_long), ("y", ctypes.c_long)]

class MEMORYSTATUSEX(ctypes.Structure):
    _fields_ = [
        ('dwLength', wintypes.DWORD),
        ('dwMemoryLoad', wintypes.DWORD),
        ('ullTotalPhys', ctypes.c_uint64),
        ('ullAvailPhys', ctypes.c_uint64),
        ('ullTotalPageFile', ctypes.c_uint64),
        ('ullAvailPageFile', ctypes.c_uint64),
        ('ullTotalVirtual', ctypes.c_uint64),
        ('ullAvailVirtual', ctypes.c_uint64),
        ('ullAvailExtendedVirtual', ctypes.c_uint64),
    ]

class LASTINPUTINFO(ctypes.Structure):
    _fields_ = [('cbSize', wintypes.UINT), ('dwTime', wintypes.DWORD)]

class FILETIME(ctypes.Structure):
    _fields_ = [('dwLowDateTime', wintypes.DWORD), ('dwHighDateTime', wintypes.DWORD)]

def get_idle_seconds():
    try:
        lii = LASTINPUTINFO()
        lii.cbSize = ctypes.sizeof(LASTINPUTINFO)
        if user32.GetLastInputInfo(ctypes.byref(lii)):
            tick = ctypes.windll.kernel32.GetTickCount()
            return max(0.0, (tick - lii.dwTime) / 1000.0)
    except Exception:
        pass
    return 0.0

def get_system_load():
    mem_load = 0
    try:
        stat = MEMORYSTATUSEX()
        stat.dwLength = ctypes.sizeof(MEMORYSTATUSEX)
        if ctypes.windll.kernel32.GlobalMemoryStatusEx(ctypes.byref(stat)):
            mem_load = stat.dwMemoryLoad
    except Exception:
        pass

    cpu_load = 0.0
    try:
        def _to_int(ft):
            return (ft.dwHighDateTime << 32) + ft.dwLowDateTime
        idle1, kernel1, user1 = FILETIME(), FILETIME(), FILETIME()
        ctypes.windll.kernel32.GetSystemTimes(ctypes.byref(idle1), ctypes.byref(kernel1), ctypes.byref(user1))
        time.sleep(0.12)
        idle2, kernel2, user2 = FILETIME(), FILETIME(), FILETIME()
        ctypes.windll.kernel32.GetSystemTimes(ctypes.byref(idle2), ctypes.byref(kernel2), ctypes.byref(user2))

        idle = _to_int(idle2) - _to_int(idle1)
        kernel = _to_int(kernel2) - _to_int(kernel1)
        user = _to_int(user2) - _to_int(user1)
        total = kernel + user
        if total > 0:
            cpu_load = max(0.0, min(100.0, 100.0 * (total - idle) / total))
    except Exception:
        pass

    return cpu_load, mem_load

settings_window = None

class TrackerApi:
    def __init__(self):
        self.hwnd = None

    def set_hwnd(self, hwnd):
        self.hwnd = hwnd

    def close_settings(self):
        global settings_window
        log_msg("close_settings requested")
        if settings_window is not None:
            try:
                import webview.platforms.winforms as wf
                from System import Action
                inst = wf.BrowserView.instances.get(settings_window.uid)
                if inst is not None and not inst.IsDisposed and inst.IsHandleCreated:
                    try:
                        inst.Invoke(Action(lambda: inst.Close()))
                    except Exception:
                        try:
                            settings_window.destroy()
                        except Exception:
                            pass
                else:
                    try:
                        settings_window.destroy()
                    except Exception:
                        pass
            except Exception as e:
                log_msg(f"close_settings error: {e}")
            settings_window = None
            return True
        return False

    def toggle_settings(self):
        global settings_window
        log_msg("toggle_settings requested")
        if settings_window is not None:
            try:
                import webview.platforms.winforms as wf
                from System import Action
                inst = wf.BrowserView.instances.get(settings_window.uid)
                if inst is not None and not inst.IsDisposed and inst.IsHandleCreated:
                    hwnd = inst.Handle.ToInt64()
                    if user32.IsWindow(hwnd):
                        log_msg("settings_window is open -> closing (toggle)")
                        try:
                            inst.Invoke(Action(lambda: inst.Close()))
                        except Exception:
                            try:
                                settings_window.destroy()
                            except Exception:
                                pass
                        settings_window = None
                        return False
            except Exception as e:
                log_msg(f"close settings_window error: {e}")
            settings_window = None

        log_msg("settings_window is not open -> creating")
        try:
            settings_url = f"http://127.0.0.1:8989/settings?_v={int(time.time() * 1000)}"
            settings_window = webview.create_window(
                "🌱 즌다몬 컴패니언 설정",
                url=settings_url,
                width=540,
                height=650,
                resizable=True,
                on_top=True,
                js_api=self
            )
            def on_settings_closed():
                global settings_window
                log_msg("settings_window closed")
                settings_window = None
            settings_window.events.closed += on_settings_closed
            return True
        except Exception as e:
            log_msg(f"create settings_window error: {e}")
            settings_window = None
            try:
                import webbrowser
                webbrowser.open("http://127.0.0.1:8989/settings")
                return True
            except Exception as wb_err:
                log_msg(f"webbrowser fallback error: {wb_err}")
                return False

    def open_settings(self):
        global settings_window
        if settings_window is not None:
            self.close_settings()
            time.sleep(0.15)
        return self.toggle_settings()

    def start_drag(self):
        if self.hwnd and user32.IsWindow(self.hwnd):
            user32.ReleaseCapture()
            user32.SendMessageW(self.hwnd, 0x0112, 0xF012, 0)
            return True
        return False

    def move_window(self, dx, dy):

        if self.hwnd and user32.IsWindow(self.hwnd):
            rect = wintypes.RECT()
            user32.GetWindowRect(self.hwnd, ctypes.byref(rect))
            user32.SetWindowPos(self.hwnd, 0, rect.left + int(dx), rect.top + int(dy), 0, 0, 0x0001 | 0x0004 | 0x0010)
            return True
        return False

    def resize_window(self, width, height):
        if self.hwnd and user32.IsWindow(self.hwnd):
            rect = wintypes.RECT()
            user32.GetWindowRect(self.hwnd, ctypes.byref(rect))
            new_w = max(280, min(1920, int(width)))
            new_h = max(350, min(1440, int(height)))
            new_x = rect.right - new_w
            new_y = rect.bottom - new_h
            user32.SetWindowPos(self.hwnd, 0, new_x, new_y, new_w, new_h, 0x0004 | 0x0010)
            cfg = load_config()
            cfg["win_w"] = new_w
            cfg["win_h"] = new_h
            save_config(cfg)
            return True
        return False



    def get_tracking(self):
        pt = POINT()
        user32.GetCursorPos(ctypes.byref(pt))

        rect = wintypes.RECT()
        if self.hwnd and user32.IsWindow(self.hwnd):
            user32.GetWindowRect(self.hwnd, ctypes.byref(rect))
            center_x = (rect.left + rect.right) / 2
            center_y = (rect.top + rect.bottom) / 2
        else:
            center_x = 960
            center_y = 540

        dx = pt.x - center_x
        dy = pt.y - center_y

        sw = user32.GetSystemMetrics(0) or 1920
        sh = user32.GetSystemMetrics(1) or 1080

        # Full-screen 100% free tracking:
        # Normalize distance based on maximum reach from companion center to screen edges
        max_dist_x = max(center_x, sw - center_x) or 1.0
        max_dist_y = max(center_y, sh - center_y) or 1.0

        fx = max(-1.0, min(1.0, dx / max_dist_x))
        fy = max(-1.0, min(1.0, -dy / max_dist_y))

        return {
            "fx": round(fx, 4),
            "fy": round(fy, 4)
        }

tracker_api = TrackerApi()

app = Bottle()

@app.hook('before_request')
def log_request():
    if request.path != "/api/poll_speech":
        log_msg(f"HTTP {request.method} {request.path}")


current_audio_id = 0
latest_audio_info = None
voicevox_ready = False

# Non-blocking VOICEVOX startup check
def ensure_voicevox_running():
    global voicevox_ready
    try:
        with urllib.request.urlopen(f"{VOICEVOX_URL}/version", timeout=1) as resp:
            if resp.status == 200:
                voicevox_ready = True
                return True
    except Exception:
        pass

    engine_path = find_voicevox_engine()
    if engine_path and os.path.exists(engine_path):
        try:
            startupinfo = None
            if os.name == 'nt':
                startupinfo = subprocess.STARTUPINFO()
                startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
                startupinfo.wShowWindow = 0
            flags = getattr(subprocess, 'CREATE_NO_WINDOW', 0x08000000)
            subprocess.Popen([engine_path, "--host", "127.0.0.1", "--port", "50021"],
                             stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
                             startupinfo=startupinfo, creationflags=flags)
            for _ in range(25):
                time.sleep(0.5)
                try:
                    with urllib.request.urlopen(f"{VOICEVOX_URL}/version", timeout=1) as resp:
                        if resp.status == 200:
                            voicevox_ready = True
                            return True
                except Exception:
                    pass
        except Exception as e:
            log_msg(f"VOICEVOX start error: {e}")
    return False

CONFIG_PATH = os.path.join(APP_DIR, "config.json")

def load_config():
    default_cfg = {
        "win_w": 560,
        "win_h": 750,
        "subtitle_enabled": True,
        "subtitle_size": 14,
        "display_mode": "bubble",
        "resource_alert": True,
        "subtitle_mode": True,
        "voice_speed": 1.0,
        "voice_pitch": 0.0,
        "voice_intonation": 1.0,
        "voice_volume": 1.0,
        "voice_pause": 0.35
    }
    if os.path.exists(CONFIG_PATH):
        try:
            with open(CONFIG_PATH, "r", encoding="utf-8") as f:
                data = json.load(f)
                if isinstance(data, dict):
                    default_cfg.update(data)
                    return default_cfg
        except Exception:
            pass
    return default_cfg

def save_config(cfg):
    try:
        with open(CONFIG_PATH, "w", encoding="utf-8") as f:
            json.dump(cfg, f, indent=2)
    except Exception as e:
        log_msg(f"save_config error: {e}")


# Fast synthesis with MD5 hash caching and configurable voice parameters
def synthesize_voicevox(synth_text, speaker=3, display_text=None, expression=None, motion=None,
                        speed=None, pitch=None, intonation=None, volume=None, pause=None,
                        params=None, emotion=None):
    global current_audio_id, latest_audio_info

    if display_text is None:
        display_text = synth_text

    cfg = load_config()
    v_speed = float(speed if speed is not None else cfg.get("voice_speed", 1.0))
    v_pitch = float(pitch if pitch is not None else cfg.get("voice_pitch", 0.0))
    v_intonation = float(intonation if intonation is not None else cfg.get("voice_intonation", 1.0))
    v_volume = float(volume if volume is not None else cfg.get("voice_volume", 1.0))
    v_pause = float(pause if pause is not None else cfg.get("voice_pause", 0.35))

    # 1. Fast Cache Check with voice parameter hash
    cache_key = hashlib.md5(f"v5:{speaker}:{synth_text}:{v_speed:.2f}:{v_pitch:.2f}:{v_intonation:.2f}:{v_volume:.2f}:{v_pause:.2f}".encode("utf-8")).hexdigest()
    cached_name = f"cached_{cache_key}.wav"
    cached_path = os.path.join(AUDIO_DIR, cached_name)

    if os.path.exists(cached_path) and os.path.getsize(cached_path) > 0:
        current_audio_id += 1
        latest_audio_info = {
            "audioId": current_audio_id,
            "audioUrl": f"/audio/{cached_name}",
            "text": display_text,
            "expression": expression,
            "motion": motion,
            "params": params or {},
            "emotion": emotion
        }
        return latest_audio_info

    # 2. Synthesize via VOICEVOX
    ensure_voicevox_running()

    query_url = f"{VOICEVOX_URL}/audio_query?text={urllib.parse.quote(synth_text)}&speaker={speaker}"
    req = urllib.request.Request(query_url, method="POST")
    with urllib.request.urlopen(req, timeout=8) as resp:
        query_data = resp.read()

    # Apply voice parameters: speed, pitch, intonation, volume, and pause duration
    try:
        q_json = json.loads(query_data.decode("utf-8"))
        q_json["speedScale"] = v_speed
        q_json["pitchScale"] = v_pitch
        q_json["intonationScale"] = v_intonation
        q_json["volumeScale"] = v_volume
        q_json["pauseLengthScale"] = v_pause
        for ap in q_json.get("accent_phrases", []):
            pm = ap.get("pause_mora")
            if pm and "vowel_length" in pm and pm["vowel_length"] is not None:
                # Scale pause length according to voice_pause setting
                pm["vowel_length"] = min(pm["vowel_length"] * v_pause, max(0.08, 0.35 * v_pause))
        query_data = json.dumps(q_json).encode("utf-8")
    except Exception as qe:
        log_msg(f"audio_query parameter adjustment error: {qe}")

    synth_url = f"{VOICEVOX_URL}/synthesis?speaker={speaker}"
    synth_req = urllib.request.Request(synth_url, data=query_data,
                                       headers={"Content-Type": "application/json"},
                                       method="POST")
    with urllib.request.urlopen(synth_req, timeout=12) as resp:
        wav_bytes = resp.read()

    with open(cached_path, "wb") as f:
        f.write(wav_bytes)

    current_audio_id += 1
    latest_audio_info = {
        "audioId": current_audio_id,
        "audioUrl": f"/audio/{cached_name}",
        "text": display_text,
        "expression": expression,
        "motion": motion,
        "params": params or {},
        "emotion": emotion
    }
    return latest_audio_info


# HTTP Routes
@app.route("/")
def index():
    p = os.path.join(APP_DIR, "index.html")
    with open(p, "r", encoding="utf-8") as f:
        html = f.read()
    return HTTPResponse(
        body=html,
        status=200,
        headers={
            "Content-Type": "text/html; charset=utf-8",
            "Cache-Control": "no-cache, no-store, must-revalidate, max-age=0",
            "Pragma": "no-cache",
            "Expires": "0"
        }
    )

@app.route("/settings")
def serve_settings():
    p = os.path.join(APP_DIR, "settings.html")
    with open(p, "r", encoding="utf-8") as f:
        html = f.read()
    return HTTPResponse(
        body=html,
        status=200,
        headers={
            "Content-Type": "text/html; charset=utf-8",
            "Cache-Control": "no-cache, no-store, must-revalidate, max-age=0",
            "Pragma": "no-cache",
            "Expires": "0"
        }
    )

@app.route("/api/open_settings", method=["GET", "POST"])
@app.route("/api/toggle_settings", method=["GET", "POST"])
def api_toggle_settings():
    response.content_type = "application/json"
    res = tracker_api.toggle_settings()
    return json.dumps({"success": True, "open": bool(res)})

@app.route("/api/close_settings", method=["GET", "POST"])
def api_close_settings():
    response.content_type = "application/json"
    res = tracker_api.close_settings()
    return json.dumps({"success": True, "closed": bool(res)})


@app.route("/static/<filename:path>")
def serve_static(filename):
    return static_file(filename, root=os.path.join(APP_DIR, "static"))

@app.route("/model/<filepath:path>")
def serve_model(filepath):
    return static_file(filepath, root=MODEL_DIR)

@app.route("/audio/<filename:path>")
def serve_audio(filename):
    return static_file(filename, root=AUDIO_DIR)

model_status = "loading"

@app.route("/api/model_loaded")
def api_model_loaded():
    global model_status
    model_status = "loaded"
    log_msg("Live2D model loaded successfully in WebView2!")
    return json.dumps({"status": "loaded"})

@app.route("/api/model_error")
def api_model_error():
    global model_status
    err = request.query.get("err", "unknown error")
    model_status = f"error: {err}"
    log_msg(f"Live2D model error in WebView2: {err}")
    return json.dumps({"status": "error", "message": err})

@app.route("/api/health")
def api_health():
    response.content_type = "application/json"
    return json.dumps({
        "status": "ok",
        "voicevox": voicevox_ready,
        "model": model_status,
        "hwnd": hex(tracker_api.hwnd) if tracker_api.hwnd else None
    })


@app.route("/api/bring_to_front")
def api_bring_to_front():
    response.content_type = "application/json"
    if tracker_api.hwnd and user32.IsWindow(tracker_api.hwnd):
        user32.SetWindowPos(tracker_api.hwnd, -1, 0, 0, 0, 0, 0x0001 | 0x0002 | 0x0040)
        return json.dumps({"success": True})
    return json.dumps({"success": False})

@app.route("/api/poll_speech")
def poll_speech():
    response.content_type = "application/json"
    last_id = int(request.query.get("last", 0))
    if latest_audio_info and latest_audio_info["audioId"] > last_id:
        return json.dumps(latest_audio_info)
    return json.dumps({})

@app.route("/api/config", method=["GET", "POST"])
def api_config():
    response.content_type = "application/json"
    cfg = load_config()
    if request.method == "POST":
        data = request.json or {}
        if "win_w" in data and "win_h" in data:
            cfg["win_w"] = max(280, min(1920, int(data["win_w"])))
            cfg["win_h"] = max(350, min(1440, int(data["win_h"])))
            tracker_api.resize_window(cfg["win_w"], cfg["win_h"])
        if "subtitle_enabled" in data:
            cfg["subtitle_enabled"] = bool(data["subtitle_enabled"])
            cfg["subtitle_mode"] = cfg["subtitle_enabled"]
        if "subtitle_mode" in data:
            cfg["subtitle_mode"] = bool(data["subtitle_mode"])
            cfg["subtitle_enabled"] = cfg["subtitle_mode"]
        if "subtitle_size" in data:
            try:
                cfg["subtitle_size"] = max(10, min(36, int(data["subtitle_size"])))
            except Exception:
                pass
        if "display_mode" in data:
            cfg["display_mode"] = str(data["display_mode"])
        if "resource_alert" in data:
            cfg["resource_alert"] = bool(data["resource_alert"])
        for vk in ["voice_speed", "voice_pitch", "voice_intonation", "voice_volume", "voice_pause"]:
            if vk in data:
                try:
                    cfg[vk] = float(data[vk])
                except Exception:
                    pass

        save_config(cfg)
        return json.dumps(cfg)
    return json.dumps(cfg)

@app.route("/api/speak", method=["GET", "POST"])
def api_speak():
    response.content_type = "application/json"
    if request.method == "POST":
        data = request.json or {}
        text = data.get("text", "")
        raw_text = data.get("raw_text") or data.get("display_text") or ""
        speaker = data.get("speaker", 3)
        speaker_explicit = bool(data.get("speaker_explicit"))
        expression = data.get("expression")
        motion = data.get("motion")
        emotion = data.get("emotion")
        params = data.get("params")
        speed = data.get("voice_speed")
        pitch = data.get("voice_pitch")
        intonation = data.get("voice_intonation")
        volume = data.get("voice_volume")
        pause = data.get("voice_pause")
    else:
        data = {}
        text = request.query.get("text", "")
        raw_text = request.query.get("raw_text") or request.query.get("display_text") or ""
        speaker = int(request.query.get("speaker", 3))
        speaker_explicit = "speaker" in request.query
        expression = request.query.get("expression")
        motion = request.query.get("motion")
        emotion = request.query.get("emotion")
        params = None
        speed = request.query.get("voice_speed")
        pitch = request.query.get("voice_pitch")
        intonation = request.query.get("voice_intonation")
        volume = request.query.get("voice_volume")
        pause = request.query.get("voice_pause")

    if not text and not raw_text:
        return json.dumps({"error": "Empty text"})

    target_text = raw_text if raw_text else text

    # Analyze emotion from text
    emo_profile = analyze_emotion(target_text, default_speaker=speaker)
    clean_text = emo_profile.get("clean_text", target_text)

    display_text = clean_text

    if emotion is None:
        emotion = emo_profile.get("key")
    if expression is None:
        expression = emo_profile.get("expression")
    if motion is None:
        motion = emo_profile.get("motion")
    if params is None:
        params = emo_profile.get("params", {})
    if not speaker_explicit and emo_profile.get("speaker"):
        speaker = emo_profile.get("speaker")

    # Apply emotion voice fine-tuning if not manually overridden
    cfg = load_config()
    if speed is None and "voice_speed_delta" in emo_profile:
        speed = max(0.5, min(2.0, float(cfg.get("voice_speed", 1.0)) + emo_profile["voice_speed_delta"]))
    if pitch is None and "voice_pitch_delta" in emo_profile:
        pitch = max(-0.15, min(0.15, float(cfg.get("voice_pitch", 0.0)) + emo_profile["voice_pitch_delta"]))
    if intonation is None and "voice_intonation_delta" in emo_profile:
        intonation = max(0.0, min(2.0, float(cfg.get("voice_intonation", 1.0)) + emo_profile["voice_intonation_delta"]))

    # Determine speech synthesis text (convert Korean to Katakana for VOICEVOX)
    if any(0xAC00 <= ord(c) <= 0xD7A3 for c in clean_text):
        synth_text = to_katakana(clean_text)
    else:
        synth_text = clean_text

    try:
        info = synthesize_voicevox(synth_text, speaker, display_text=display_text,
                                   expression=expression, motion=motion,
                                   speed=speed, pitch=pitch,
                                   intonation=intonation, volume=volume,
                                   pause=pause, params=params, emotion=emotion)
        return json.dumps({"success": True, "info": info, "emotion": emotion})
    except Exception as e:
        return json.dumps({"error": str(e)})

class ResourceMonitor:
    def __init__(self):
        self.last_speech_time = 0.0
        self.last_resource_alert_time = 0.0

    def speak_alert(self, text, expression="exp_surprise", motion="mtnFace_surprise"):
        now = time.time()
        # Cooldown: at least 90s gap
        if now - self.last_speech_time < 90:
            return False
        self.last_speech_time = now
        try:
            kana = to_katakana(text) if any(0xAC00 <= ord(c) <= 0xD7A3 for c in text) else text
            synthesize_voicevox(kana, speaker=3, display_text=text, expression=expression, motion=motion)
            log_msg(f"ResourceMonitor alert spoken: {text}")
            return True
        except Exception as e:
            log_msg(f"ResourceMonitor speak error: {e}")
            return False

    def loop(self):
        time.sleep(20)
        while True:
            try:
                time.sleep(15)
                cfg = load_config()
                if not cfg.get("resource_alert", True):
                    continue

                now = time.time()
                # Cooldown: at least 12 minutes between overload alerts
                if now - self.last_resource_alert_time >= 12 * 60:
                    cpu, mem = get_system_load()
                    if cpu > 90 or mem > 92:
                        self.last_resource_alert_time = now
                        load_msg = "컴퓨터가 힘들어하고 있는 것이다! 무거운 프로그램이나 탭을 좀 정리해 주는 것이다!"
                        self.speak_alert(load_msg, expression="exp_surprise", motion="mtnFace_surprise")

            except Exception as e:
                log_msg(f"ResourceMonitor loop error: {traceback.format_exc()}")
                time.sleep(20)

resource_monitor = ResourceMonitor()


def run_server():
    try:
        host = os.environ.get("HOST", "0.0.0.0") if not user32 else "127.0.0.1"
        port = int(os.environ.get("PORT", os.environ.get("SERVER_PORT", 8989)))
        log_msg(f"run_server() starting bottle on {host}:{port}...")
        app.run(host=host, port=port, quiet=True)
    except Exception as e:
        log_msg(f"run_server() FATAL: {traceback.format_exc()}")


def check_already_running():
    try:
        req = urllib.request.Request("http://127.0.0.1:8989/api/health")
        with urllib.request.urlopen(req, timeout=0.8) as resp:
            if resp.status == 200:
                data = json.loads(resp.read().decode("utf-8"))
                raw_hwnd = data.get("hwnd")
                if raw_hwnd:
                    h = int(raw_hwnd, 16)
                    if user32.IsWindow(h):
                        try:
                            urllib.request.urlopen("http://127.0.0.1:8989/api/bring_to_front", timeout=0.8)
                        except Exception:
                            pass
                        return True
    except Exception:
        return False
    return False

if __name__ == "__main__":
    # If passed --speak argument, act as CLI client
    if len(sys.argv) > 2 and sys.argv[1] == "--speak":
        text_to_speak = " ".join(sys.argv[2:])
        try:
            req = urllib.request.Request("http://127.0.0.1:8989/api/speak",
                                         data=json.dumps({"text": text_to_speak, "speaker": 3}).encode("utf-8"),
                                         headers={"Content-Type": "application/json"})
            with urllib.request.urlopen(req, timeout=6) as resp:
                print(resp.read().decode("utf-8"))
        except Exception as e:
            print("Failed to send speak command:", e)
        sys.exit(0)

    # Prevent duplicate companion windows
    if check_already_running():
        print("Zundamon Companion is already running! Brought to front.")
        sys.exit(0)

    # Start local web server in background
    srv_thread = threading.Thread(target=run_server, daemon=True)
    srv_thread.start()

    # Pre-warm VOICEVOX in background thread (never blocks GUI window startup)
    threading.Thread(target=ensure_voicevox_running, daemon=True).start()

    # Server mode (for Linux hosting like Weirdhost, or headless execution)
    if not user32 or "--server" in sys.argv:
        host = os.environ.get("HOST", "0.0.0.0")
        port = int(os.environ.get("PORT", os.environ.get("SERVER_PORT", 8989)))
        print(f"🌱 즌다몬 웹 서버 모드로 실행됩니다: http://{host}:{port}")
        app.run(host=host, port=port)
        sys.exit(0)

    # Configurable window dimensions (saved in config.json)
    cfg = load_config()
    win_w = cfg.get("win_w", 560)
    win_h = cfg.get("win_h", 750)
    sw = user32.GetSystemMetrics(0) or 1920
    sh = user32.GetSystemMetrics(1) or 1080
    init_x = max(0, sw - win_w - 20)
    init_y = max(0, sh - win_h - 40)

    window = webview.create_window(
        "Zundamon Live2D",
        url=f"http://127.0.0.1:8989/?v={int(time.time())}",
        width=win_w,
        height=win_h,
        x=init_x,
        y=init_y,
        frameless=True,
        transparent=True,
        on_top=True,
        background_color="#000000",
        js_api=tracker_api
    )

    def on_window_ready():
        log_msg("on_window_ready triggered")
        try:
            import webview.platforms.winforms as wf
            from System import Action
            import System.Drawing as Drawing

            class MARGINS(ctypes.Structure):
                _fields_ = [
                    ("cxLeftWidth", ctypes.c_int),
                    ("cxRightWidth", ctypes.c_int),
                    ("cyTopHeight", ctypes.c_int),
                    ("cyBottomHeight", ctypes.c_int)
                ]

            hwnd = None
            for i in range(30):
                inst = wf.BrowserView.instances.get(window.uid)
                if inst:
                    hwnd = inst.Handle.ToInt64()
                    tracker_api.set_hwnd(hwnd)
                    log_msg(f"Attached hwnd: {hex(hwnd)}")

                    # Apply DWM glass margins for complete per-pixel transparency
                    m = MARGINS(-1, -1, -1, -1)
                    ctypes.windll.dwmapi.DwmExtendFrameIntoClientArea(hwnd, ctypes.byref(m))

                    def _configure_form():
                        inst.BackColor = Drawing.Color.Black
                        if hasattr(inst, 'browser') and hasattr(inst.browser, 'webview'):
                            inst.browser.webview.DefaultBackgroundColor = Drawing.Color.Transparent
                        inst.Show()
                        inst.BringToFront()
                        inst.Activate()

                    try:
                        inst.Invoke(Action(_configure_form))
                        log_msg("Applied transparency to Form and WebView2 successfully!")
                    except Exception as ie:
                        log_msg(f"Invoke show error: {ie}")
                    break
                time.sleep(0.1)
        except Exception as e:
            log_msg(f"on_window_ready error: {traceback.format_exc()}")

        # Initial greeting in background
        def greeting():
            time.sleep(1.0)
            try:
                greet_txt = "보쿠는 즌다몬인 것이다! 잘 부탁하는 것이다!"
                kana = to_katakana(greet_txt) if any(0xAC00 <= ord(c) <= 0xD7A3 for c in greet_txt) else greet_txt
                synthesize_voicevox(kana, speaker=3, display_text=greet_txt)
            except Exception as e:
                log_msg(f"Greeting error: {traceback.format_exc()}")
        threading.Thread(target=greeting, daemon=True).start()

        # Start PC Resource Monitor loop
        threading.Thread(target=resource_monitor.loop, daemon=True).start()

    log_msg("Calling webview.start()...")
    try:
        webview.start(on_window_ready, storage_path=WV2_STORAGE, private_mode=False)
        log_msg("webview.start() returned normally.")
    except Exception as e:
        log_msg(f"webview.start() exception: {traceback.format_exc()}")
