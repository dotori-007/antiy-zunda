import sys
import json
import urllib.request
import urllib.parse
import os
import subprocess

current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

try:
    from hangul_to_kana import to_katakana
except Exception:
    def to_katakana(t): return t

def speak(text, speaker=3):
    # Try sending to running Live2D companion first (fast timeout)
    # Keep original Korean text so subtitles and speech bubbles display natural Korean
    try:
        host = os.environ.get("ZUNDAMON_HOST", "127.0.0.1:8989")
        req = urllib.request.Request(
            f"http://{host}/api/speak",
            data=json.dumps({"text": text, "display_text": text, "raw_text": text, "speaker": speaker}).encode("utf-8"),
            headers={"Content-Type": "application/json"}
        )
        with urllib.request.urlopen(req, timeout=20) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            if data.get("success"):
                print("Spoke via Live2D Companion.")
                return
    except Exception:
        pass

    # Direct fallback to VOICEVOX if companion window is not active
    # Convert any Korean Hangul text to natural Katakana pronunciation for VOICEVOX
    tts_text = to_katakana(text)
    try:
        vv_url = "http://127.0.0.1:50021"
        q_url = f"{vv_url}/audio_query?text={urllib.parse.quote(tts_text)}&speaker={speaker}"
        with urllib.request.urlopen(urllib.request.Request(q_url, method="POST"), timeout=4) as resp:
            q_data = resp.read()

        # Reduce pause duration at spaces
        try:
            q_json = json.loads(q_data.decode("utf-8"))
            q_json["pauseLengthScale"] = 0.35
            for ap in q_json.get("accent_phrases", []):
                pm = ap.get("pause_mora")
                if pm and "vowel_length" in pm and pm["vowel_length"] is not None:
                    pm["vowel_length"] = min(pm["vowel_length"] * 0.35, 0.13)
            q_data = json.dumps(q_json).encode("utf-8")
        except Exception:
            pass

        s_url = f"{vv_url}/synthesis?speaker={speaker}"
        s_req = urllib.request.Request(s_url, data=q_data, headers={"Content-Type": "application/json"}, method="POST")
        with urllib.request.urlopen(s_req, timeout=6) as resp:
            wav_data = resp.read()

        temp_wav = os.path.join(os.environ.get("TEMP", "."), "zundamon_temp.wav")
        with open(temp_wav, "wb") as f:
            f.write(wav_data)

        # Async audio play via PowerShell SoundPlayer (.Play() instead of blocking .PlaySync())
        ps_cmd = f"(New-Object Media.SoundPlayer '{temp_wav}').Play()"
        flags = getattr(subprocess, 'CREATE_NO_WINDOW', 0x08000000)
        subprocess.Popen(["powershell", "-NoProfile", "-NonInteractive", "-Command", ps_cmd],
                         stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
                         creationflags=flags)
        print("Spoke via VOICEVOX directly.")
    except Exception as e:
        print("Speak error:", e)

if __name__ == "__main__":
    if len(sys.argv) > 1:
        text = " ".join(sys.argv[1:])
    else:
        text = "보쿠는 즌다몬인 것이다!"
    speak(text)
