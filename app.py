import os
import sys
import time
import json
import hashlib
import tempfile
import urllib.request
import urllib.parse
import threading
import subprocess
import ctypes
import traceback
from ctypes import wintypes
from bottle import Bottle, request, response, static_file
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


class POINT(ctypes.Structure):
    _fields_ = [("x", ctypes.c_long), ("y", ctypes.c_long)]

class TrackerApi:
    def __init__(self):
        self.hwnd = None

    def set_hwnd(self, hwnd):
        self.hwnd = hwnd

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
    default_cfg = {"win_w": 560, "win_h": 750, "subtitle_enabled": True, "subtitle_size": 14}
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


# Fast synthesis with MD5 hash caching
def synthesize_voicevox(synth_text, speaker=3, display_text=None):
    global current_audio_id, latest_audio_info

    if display_text is None:
        display_text = synth_text

    # 1. Fast Cache Check
    cache_key = hashlib.md5(f"{speaker}:{synth_text}".encode("utf-8")).hexdigest()
    cached_name = f"cached_{cache_key}.wav"
    cached_path = os.path.join(AUDIO_DIR, cached_name)

    if os.path.exists(cached_path) and os.path.getsize(cached_path) > 0:
        current_audio_id += 1
        latest_audio_info = {
            "audioId": current_audio_id,
            "audioUrl": f"/audio/{cached_name}",
            "text": display_text
        }
        return latest_audio_info

    # 2. Synthesize via VOICEVOX
    ensure_voicevox_running()

    query_url = f"{VOICEVOX_URL}/audio_query?text={urllib.parse.quote(synth_text)}&speaker={speaker}"
    req = urllib.request.Request(query_url, method="POST")
    with urllib.request.urlopen(req, timeout=8) as resp:
        query_data = resp.read()

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
        "text": display_text
    }
    return latest_audio_info


# HTTP Routes
@app.route("/")
def index():
    response.set_header("Cache-Control", "no-cache, no-store, must-revalidate")
    return static_file("index.html", root=APP_DIR)


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
        if "subtitle_size" in data:
            try:
                cfg["subtitle_size"] = max(10, min(36, int(data["subtitle_size"])))
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
        speaker = data.get("speaker", 3)
    else:
        text = request.query.get("text", "")
        speaker = int(request.query.get("speaker", 3))

    if not text:
        return json.dumps({"error": "Empty text"})

    display_text = text
    # Automatically transform Korean to Katakana via G2P for speech engine
    if any(0xAC00 <= ord(c) <= 0xD7A3 for c in text):
        synth_text = to_katakana(text)
    else:
        synth_text = text

    try:
        info = synthesize_voicevox(synth_text, speaker, display_text=display_text)
        return json.dumps({"success": True, "info": info})
    except Exception as e:
        return json.dumps({"error": str(e)})

def run_server():
    try:
        log_msg("run_server() starting bottle on 127.0.0.1:8989...")
        app.run(host="127.0.0.1", port=8989, quiet=True)
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

    log_msg("Calling webview.start()...")
    try:
        webview.start(on_window_ready, storage_path=WV2_STORAGE, private_mode=False)
        log_msg("webview.start() returned normally.")
    except Exception as e:
        log_msg(f"webview.start() exception: {traceback.format_exc()}")
