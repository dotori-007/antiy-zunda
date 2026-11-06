# -*- coding: utf-8 -*-
"""
Zundamon Emotion Engine (즌다몬 감정 대응 엔진)
텍스트의 의미, 키워드 및 태그를 분석하여 실시간 Live2D 표정, 모션,
및 VOICEVOX 화자 스타일을 자동으로 매핑합니다.
(신체 파츠 소실이나 반투명 고스트 현상을 원천 방지하기 위해
모델 제작자가 검증한 네이티브 Expression과 Motion으로 100% 안전하게 구동합니다.)
"""

import re

# 감정 프로필 정의
EMOTION_PROFILES = {
    "crying": {
        "name": "눈물/슬픔 (오류·실패)",
        "expression": "exp_sad",       # 네이티브 눈물 + 시든 귀 + 슬픈 표정
        "motion": "mtnBody_tremble",   # 온몸 부들부들 떨기
        "speaker": 3,
        "voice_speed_delta": -0.05,
        "voice_pitch_delta": -0.03,
        "voice_intonation_delta": -0.15,
        "params": {}
    },
    "panic": {
        "name": "충격/공포/새파람 (비상·차단·경고)",
        "expression": "exp_01",        # 네이티브 얼굴 파랗게 질림 + 식은땀 + 당황 눈
        "motion": "mtnBody_tremble",   # 떨기
        "speaker": 3,
        "voice_speed_delta": 0.15,
        "voice_pitch_delta": 0.05,
        "voice_intonation_delta": 0.20,
        "params": {}
    },
    "angry_pout": {
        "name": "삐짐/거절/반박 (볼빵빵·도리도리)",
        "expression": "exp_05",        # 네이티브 볼 빵빵하게 부풀림(ParamcheekPuff)
        "motion": "mtnBody_no",        # 도리도리 거절 모션
        "speaker": 7,                  # 츤츤 스타일
        "voice_speed_delta": 0.05,
        "voice_pitch_delta": 0.02,
        "voice_intonation_delta": 0.35,
        "params": {}
    },
    "joy_cheer": {
        "name": "환호/성공/만세 (기쁨·축하)",
        "expression": "exp_laugh2",    # 네이티브 활짝 웃는 눈 + 쫑긋 선 귀
        "motion": "mtnBody_wave",      # 손 흔들어 환호
        "speaker": 1,                  # 아마아마 (달콤애교)
        "voice_speed_delta": 0.08,
        "voice_pitch_delta": 0.03,
        "voice_intonation_delta": 0.25,
        "params": {}
    },
    "smug_pride": {
        "name": "당당/허세/자신감",
        "expression": "exp_smile",     # 미소
        "motion": "mtnBody_point",     # 당당하게 삿대질/가리키기 모션
        "speaker": 7,                  # 츤츤 / 당돌
        "voice_speed_delta": 0.02,
        "voice_pitch_delta": 0.01,
        "voice_intonation_delta": 0.20,
        "params": {}
    },
    "thinking": {
        "name": "고민/분석/진단 (턱괴기)",
        "expression": "exp_04",        # 턱에 손대기 자세 포즈
        "motion": "mtnBody_think",     # 골똘히 생각하는 모션
        "speaker": 3,
        "voice_speed_delta": 0.0,
        "voice_pitch_delta": 0.0,
        "voice_intonation_delta": 0.0,
        "params": {}
    },
    "love_shy": {
        "name": "부끄/감동/하트 (고마움·애정)",
        "expression": "exp_shy",       # 부끄러운 미소 + 홍조
        "motion": "mtnFace_shy",       # 배시시 수줍어하는 모션
        "speaker": 1,                  # 아마아마
        "voice_speed_delta": -0.02,
        "voice_pitch_delta": 0.04,
        "voice_intonation_delta": 0.15,
        "params": {}
    },
    "chop_action": {
        "name": "손날치기 (촙!)",
        "expression": "exp_angry3",    # 발끈한 눈
        "motion": "mtnBody_point2",    # 손날 내지르기 모션
        "speaker": 7,
        "voice_speed_delta": 0.10,
        "voice_pitch_delta": 0.02,
        "voice_intonation_delta": 0.30,
        "params": {}
    },
    "normal": {
        "name": "기본/친근 (일상 대화)",
        "expression": "exp_smile",     # 기본 미소 (완벽한 신체 및 귀 기본값)
        "motion": "mtnBody_yes",       # 끄덕임
        "speaker": 3,                  # 노멀
        "voice_speed_delta": 0.0,
        "voice_pitch_delta": 0.0,
        "voice_intonation_delta": 0.0,
        "params": {}
    }
}

# 태그 매핑 [감정:태그] 또는 [emo:tag]
TAG_MAPPING = {
    "눈물": "crying", "슬픔": "crying", "오류": "crying", "실패": "crying", "crying": "crying", "sad": "crying",
    "충격": "panic", "공포": "panic", "비상": "panic", "새파람": "panic", "panic": "panic", "shock": "panic",
    "삐짐": "angry_pout", "거절": "angry_pout", "볼빵빵": "angry_pout", "화남": "angry_pout", "pout": "angry_pout", "angry": "angry_pout",
    "성공": "joy_cheer", "기쁨": "joy_cheer", "환호": "joy_cheer", "만세": "joy_cheer", "축하": "joy_cheer", "joy": "joy_cheer",
    "당당": "smug_pride", "팔짱": "smug_pride", "허세": "smug_pride", "자신": "smug_pride", "smug": "smug_pride", "pride": "smug_pride",
    "생각": "thinking", "분석": "thinking", "진단": "thinking", "턱괴기": "thinking", "think": "thinking",
    "사랑": "love_shy", "하트": "love_shy", "부끄": "love_shy", "감동": "love_shy", "love": "love_shy", "shy": "love_shy",
    "촙": "chop_action", "손날": "chop_action", "chop": "chop_action",
    "기본": "normal", "보통": "normal", "normal": "normal"
}

# 키워드 규칙 (우선순위 순서대로 매칭)
KEYWORD_RULES = [
    # 1. 촙 / 손날
    (r"(촙|손날치기|받아라|응징)", "chop_action"),

    # 2. 충격 / 공포 / 새파랗게 질림
    (r"(충격|공포|비상|새파랗|경고|위험|큰일|사고|덜덜|으악|깜짝|403|521|turnstile|차단당|막혀|막혔)", "panic"),

    # 3. 삐짐 / 거절 / 반박 / 볼빵빵
    (r"(말도\s*안|인정\s*못|틀렸|바보|거절|안\s*돼|그만|삐짐|치사|흥[!~]|불만|불합리|반대|따질|억울)", "angry_pout"),

    # 4. 눈물 / 오류 / 실패 / 슬픔
    (r"(오류|에러|실패|타임아웃|timeout|불가|안\s*됨|안\s*되|못\s*함|죽었|꺼졌|다운|망했|슬프|눈물|흑흑|우에엥|ㅠㅠ|ㅜㅜ|미안|죄송|유감)", "crying"),

    # 5. 사랑 / 부끄 / 감동 / 하트
    (r"(고마워|감사|사랑|좋아|귀여|헤헤|부끄|두근|감동|최고야|다행)", "love_shy"),

    # 6. 환호 / 성공 / 만세 / 축하
    (r"(성공|완료|완성|해냈|축하|대성공|좋았|나이스|최고인|만세|신나|와아|야호|돌파|해결했)", "joy_cheer"),

    # 7. 당당 / 허세 / 팔짱
    (r"(맡겨|당연|물론|내가\s|보쿠가|완벽|후후|에헴|자신\s*있|파악|문제없|알고\s*있)", "smug_pride"),

    # 8. 생각 / 분석 / 진단
    (r"(분석|진단|확인|검토|테스트|조사|생각|계획|플랜|추정|판단|살펴|살펴보)", "thinking")
]

def analyze_emotion(text, default_speaker=3):
    clean_text = text
    detected_key = None

    tag_match = re.search(r"\[(?:감정|emo|emotion)\s*:\s*([^\]]+)\]", text, re.IGNORECASE)
    if tag_match:
        tag_val = tag_match.group(1).strip().lower()
        if tag_val in TAG_MAPPING:
            detected_key = TAG_MAPPING[tag_val]
        clean_text = re.sub(r"\[(?:감정|emo|emotion)\s*:\s*[^\]]+\]", "", clean_text).strip()

    if not detected_key:
        lower_text = text.lower()
        for pattern, emo_key in KEYWORD_RULES:
            if re.search(pattern, lower_text):
                detected_key = emo_key
                break

    if not detected_key or detected_key not in EMOTION_PROFILES:
        detected_key = "normal"

    profile = EMOTION_PROFILES[detected_key].copy()
    profile["key"] = detected_key
    profile["clean_text"] = clean_text
    profile["speaker"] = profile.get("speaker", default_speaker)

    return profile
