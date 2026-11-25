import sys
import json
import urllib.request
import urllib.parse
import os
import subprocess
import hashlib

current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

try:
    from hangul_to_kana import to_katakana
except Exception:
    def to_katakana(t): return t

try:
    from emotion_engine import analyze_emotion
except Exception:
    def analyze_emotion(t, default_speaker=3):
        return {"key": "normal", "speaker": default_speaker, "clean_text": t}

def speak(text, speaker=None, emotion=None):
    # Try sending to running Live2D companion first (fast timeout)
    # Keep original Korean text so subtitles and speech bubbles display natural Korean
    try:
        host = os.environ.get("ZUNDAMON_HOST", "127.0.0.1:8989")
        payload = {
            "text": text,
            "display_text": text,
            "raw_text": text
        }
        if speaker is not None:
            payload["speaker"] = speaker
            payload["speaker_explicit"] = True
        if emotion is not None:
            payload["emotion"] = emotion

        req = urllib.request.Request(
            f"http://{host}/api/speak",
            data=json.dumps(payload).encode("utf-8"),
            headers={"Content-Type": "application/json"}
        )
        with urllib.request.urlopen(req, timeout=20) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            if data.get("success"):
                emo_name = data.get("emotion") or "auto"
                print(f"Spoke via Live2D Companion (Emotion: {emo_name}).")
                return
    except Exception:
        pass

    # Direct fallback to VOICEVOX if companion window is not active
    emo_profile = analyze_emotion(text, default_speaker=3)
    clean_text = emo_profile.get("clean_text", text)
    actual_speaker = speaker if speaker is not None else emo_profile.get("speaker", 3)
    emo_key = emotion if emotion is not None else emo_profile.get("key")

    tts_text = to_katakana(clean_text)
    try:
        cache_dir = os.path.join(current_dir, "audio_cache")
        os.makedirs(cache_dir, exist_ok=True)
        cache_key = hashlib.md5(f"v5:{actual_speaker}:{tts_text}:1.00:0.00:1.00:1.00:0.35".encode("utf-8")).hexdigest()
        target_wav = os.path.join(cache_dir, f"cached_{cache_key}.wav")

        if not (os.path.exists(target_wav) and os.path.getsize(target_wav) > 0):
            vv_url = "http://127.0.0.1:50021"
            q_url = f"{vv_url}/audio_query?text={urllib.parse.quote(tts_text)}&speaker={actual_speaker}"
            with urllib.request.urlopen(urllib.request.Request(q_url, method="POST"), timeout=4) as resp:
                q_data = resp.read()

            # Reduce pause duration at spaces and apply emotion fine-tuning
            try:
                q_json = json.loads(q_data.decode("utf-8"))
                q_json["pauseLengthScale"] = 0.35
                if "voice_speed_delta" in emo_profile:
                    q_json["speedScale"] = max(0.5, min(2.0, 1.0 + emo_profile["voice_speed_delta"]))
                if "voice_pitch_delta" in emo_profile:
                    q_json["pitchScale"] = max(-0.15, min(0.15, emo_profile["voice_pitch_delta"]))
                if "voice_intonation_delta" in emo_profile:
                    q_json["intonationScale"] = max(0.0, min(2.0, 1.0 + emo_profile["voice_intonation_delta"]))

                for ap in q_json.get("accent_phrases", []):
                    pm = ap.get("pause_mora")
                    if pm and "vowel_length" in pm and pm["vowel_length"] is not None:
                        pm["vowel_length"] = min(pm["vowel_length"] * 0.35, 0.13)
                q_data = json.dumps(q_json).encode("utf-8")
            except Exception:
                pass

            s_url = f"{vv_url}/synthesis?speaker={actual_speaker}"
            s_req = urllib.request.Request(s_url, data=q_data, headers={"Content-Type": "application/json"}, method="POST")
            with urllib.request.urlopen(s_req, timeout=6) as resp:
                wav_data = resp.read()

            with open(target_wav, "wb") as f:
                f.write(wav_data)

        # Safe sound playback (native winsound first, zero subprocess latency and immune to injection)
        played = False
        try:
            import winsound
            winsound.PlaySound(target_wav, winsound.SND_FILENAME | winsound.SND_ASYNC)
            played = True
        except Exception:
            pass

        if not played:
            ps_path = target_wav.replace("'", "''")
            ps_cmd = f"(New-Object Media.SoundPlayer '{ps_path}').Play()"
            flags = getattr(subprocess, 'CREATE_NO_WINDOW', 0x08000000)
            subprocess.Popen(["powershell", "-NoProfile", "-NonInteractive", "-Command", ps_cmd],
                             stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
                             creationflags=flags)
        print(f"Spoke via VOICEVOX directly (Speaker: {actual_speaker}).")
    except Exception as e:
        print("Speak error:", e)

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Zundamon Emotion Speak CLI")
    parser.add_argument("text", nargs="*", help="Text to speak")
    parser.add_argument("-s", "--speaker", type=int, default=None, help="VOICEVOX Speaker ID")
    parser.add_argument("-e", "--emotion", type=str, default=None, help="Force specific emotion")
    args = parser.parse_args()

    input_text = " ".join(args.text) if args.text else "보쿠는 즌다몬인 것이다!"
    speak(input_text, speaker=args.speaker, emotion=args.emotion)
