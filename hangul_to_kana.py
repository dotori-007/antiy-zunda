# -*- coding: utf-8 -*-
"""
Hangul to Katakana transliterator optimized for Japanese TTS (VOICEVOX / Zundamon).
Integrates G2P (Grapheme-to-Phoneme), English acronym expansion, and Korean phonological rules.
"""
import re

CHO_LIST = ['ㄱ','ㄲ','ㄴ','ㄷ','ㄸ','ㄹ','ㅁ','ㅂ','ㅃ','ㅅ','ㅆ','ㅇ','ㅈ','ㅉ','ㅊ','ㅋ','ㅌ','ㅍ','ㅎ']
JUNG_LIST = ['ㅏ','ㅐ','ㅑ','ㅒ','ㅓ','ㅔ','ㅕ','ㅖ','ㅗ','ㅘ','ㅙ','ㅚ','ㅛ','ㅜ','ㅝ','ㅞ','ㅟ','ㅠ','ㅡ','ㅢ','ㅣ']
JONG_LIST = ['', 'ㄱ','ㄲ','ㄳ','ㄴ','ㄵ','ㄶ','ㄷ','ㄹ','ㄺ','ㄻ','ㄼ','ㄽ','ㄾ','ㄿ','ㅀ','ㅁ','ㅂ','ㅄ','ㅅ','ㅆ','ㅇ','ㅈ','ㅊ','ㅋ','ㅌ','ㅍ','ㅎ']

# Base Kana table: [Cho][Jung] -> (unvoiced, voiced)
KANA_TABLE = {
    # ㅇ (vowels)
    11: ('ア', 'エ', 'ヤ', 'イェ', 'オ', 'エ', 'ヨ', 'イェ', 'オ', 'ワ', 'ウェ', 'ウェ', 'ヨ', 'ウ', 'ウォ', 'ウェ', 'ウィ', 'ユ', 'ウ', 'ウイ', 'イ'),
    # ㄱ (unvoiced: k, voiced: g)
    0:  ('カ', 'ケ', 'キャ', 'キェ', 'コ', 'ケ', 'キョ', 'キェ', 'コ', 'クァ', 'クェ', 'クェ', 'キョ', 'ク', 'クォ', 'クェ', 'クィ', 'キュ', 'ク', 'クイ', 'キ'),
    # ㄲ
    1:  ('ッカ', 'ッケ', 'ッキャ', 'ッキェ', 'ッコ', 'ッケ', 'ッキョ', 'ッキェ', 'ッコ', 'ックァ', 'ックェ', 'ックェ', 'ッキョ', 'ック', 'ックォ', 'ックェ', 'ックィ', 'ッキュ', 'ック', 'ックイ', 'ッキ'),
    # ㄴ
    2:  ('ナ', 'ネ', 'ニャ', 'ニェ', 'ノ', 'ネ', 'ニョ', 'ニェ', 'ノ', 'ヌァ', 'ヌェ', 'ヌェ', 'ニョ', 'ヌ', 'ヌォ', 'ヌェ', 'ヌィ', 'ニュ', 'ヌ', 'ヌイ', 'ニ'),
    # ㄷ (unvoiced: t, voiced: d)
    3:  ('タ', 'テ', 'チャ', 'チェ', 'ト', 'テ', 'チョ', 'チェ', 'ト', 'トァ', 'トェ', 'トェ', 'チョ', 'トゥ', 'トォ', 'トェ', 'ティ', 'テュ', 'トゥ', 'トゥイ', 'ティ'),
    # ㄸ
    4:  ('ッタ', 'ッテ', 'ッチャ', 'ッチェ', 'ット', 'ッテ', 'ッチョ', 'ッチェ', 'ット', 'ットァ', 'ットェ', 'ットェ', 'ッチョ', 'ットゥ', 'ットォ', 'ットェ', 'ッティ', 'ッテュ', 'ットゥ', 'ットゥイ', 'ッティ'),
    # ㄹ
    5:  ('ラ', 'レ', 'リャ', 'リェ', 'ロ', 'レ', 'リョ', 'リェ', 'ロ', 'ルァ', 'ルェ', 'ルェ', 'リョ', 'ル', 'ルォ', 'ルェ', 'ルィ', 'リュ', 'ル', 'ルイ', 'リ'),
    # ㅁ
    6:  ('マ', 'メ', 'ミャ', 'ミェ', 'モ', 'メ', 'ミョ', 'ミェ', 'モ', 'ムァ', 'ムェ', 'ムェ', 'ミョ', 'ム', 'ムォ', 'ムェ', 'ムィ', 'ミュ', 'ム', 'ムイ', 'ミ'),
    # ㅂ (unvoiced: p, voiced: b)
    7:  ('パ', 'ペ', 'ピャ', 'ピェ', 'ポ', 'ペ', 'ピョ', 'ピェ', 'ポ', 'プァ', 'プェ', 'プェ', 'ピョ', 'プ', 'プォ', 'プェ', 'プィ', 'ピュ', 'プ', 'プ이', 'ピ'),
    # ㅃ
    8:  ('ッパ', 'ッペ', 'ッピャ', 'ッピェ', 'ッポ', 'ッペ', 'ッピョ', 'ッピェ', 'ッポ', 'ップァ', 'ップェ', 'ップェ', 'ッピョ', 'ップ', 'ップォ', 'ップェ', 'ップィ', 'ッピュ', 'ップ', 'ップイ', 'ッピ'),
    # ㅅ
    9:  ('サ', 'セ', 'シャ', 'シェ', 'ソ', 'セ', 'ショ', 'シェ', 'ソ', 'スァ', 'スェ', 'スェ', 'ショ', 'ス', 'スォ', 'スェ', 'スィ', 'シュ', 'ス', 'スイ', 'シ'),
    # ㅆ
    10: ('ッサ', 'ッセ', 'ッシャ', 'ッシェ', 'ッソ', 'ッセ', 'ッショ', 'ッシェ', 'ッソ', 'ッスァ', 'ッスェ', 'ッスェ', 'ッショ', 'ッス', 'ッスォ', 'ッスェ', 'ッスィ', 'ッシュ', 'ッス', 'ッスイ', 'ッシ'),
    # ㅈ (unvoiced: ch, voiced: j)
    12: ('チャ', 'チェ', 'チャ', 'チェ', 'チョ', 'チェ', 'チョ', 'チェ', 'チョ', 'チョァ', 'チョェ', 'チョェ', 'チョ', 'チュ', 'チョ', 'チェ', 'チュィ', 'チュ', 'ジュ', 'ジュイ', 'ジ'),
    # ㅉ
    13: ('ッチャ', 'ッチェ', 'ッチャ', 'ッチェ', 'ッチョ', 'ッチェ', 'ッチョ', 'ッチェ', 'ッチョ', 'ッチョァ', 'ッチョェ', 'ッチョェ', 'ッチョ', 'ッチュ', 'ッチョ', 'ッチェ', 'ッチュィ', 'ッチュ', 'ッチュ', 'ッチュイ', 'ッチ'),
    # ㅊ
    14: ('チャ', 'チェ', 'チャ', 'チェ', 'チョ', 'チェ', 'チョ', 'チェ', 'チョ', 'チョァ', 'チョェ', 'チョェ', 'チョ', 'チュ', 'チョ', 'チェ', 'チュィ', 'チュ', 'チュ', 'チュイ', 'チ'),
    # ㅋ
    15: ('カ', 'ケ', 'キャ', 'キェ', 'コ', 'ケ', 'キョ', 'キェ', 'コ', 'クァ', 'クェ', 'クェ', 'キョ', 'ク', 'クォ', 'クェ', 'クィ', 'キュ', 'ク', 'クイ', 'キ'),
    # ㅌ
    16: ('タ', 'テ', 'チャ', 'チェ', 'ト', 'テ', 'チョ', 'チェ', 'ト', 'トァ', 'トェ', 'トェ', 'チョ', 'トゥ', 'トォ', 'トェ', 'ティ', 'テュ', 'トゥ', 'トゥイ', 'ティ'),
    # ㅍ
    17: ('パ', 'ペ', 'ピャ', 'ピェ', 'ポ', 'ペ', 'ピョ', 'ピェ', 'ポ', 'プァ', 'プェ', 'プェ', 'ピョ', 'プ', 'プォ', 'プェ', 'プィ', 'ピュ', 'プ', 'プイ', 'ピ'),
    # ㅎ
    18: ('ハ', 'ヘ', 'ヒャ', 'ヒェ', 'ホ', 'ヘ', 'ヒョ', 'ヒェ', 'ホ', 'ファ', 'フェ', 'フェ', 'ヒョ', 'フ', 'フォ', 'フェ', 'フィ', 'ヒュ', 'フ', 'フイ', 'ヒ'),
}

VOICED_MAP = {
    # ㄱ -> g
    0:  ('ガ', 'ゲ', 'ギャ', 'ギェ', 'ゴ', 'ゲ', 'ギョ', 'ギェ', 'ゴ', 'グァ', 'グェ', 'グェ', 'ギョ', 'グ', 'グォ', 'グェ', 'グィ', 'ギュ', 'グ', 'グイ', 'ギ'),
    # ㄷ -> d
    3:  ('ダ', 'デ', 'ジャ', 'ジェ', 'ド', 'デ', 'ジョ', 'ジェ', 'ド', 'ドァ', 'ドェ', 'ドェ', 'ジョ', 'ドゥ', 'ドォ', 'ドェ', 'ディ', 'デュ', 'ドゥ', 'ドゥイ', 'ディ'),
    # ㅂ -> b
    7:  ('バ', 'ベ', 'ビャ', 'ビェ', 'ボ', 'ベ', 'ビョ', 'ビェ', 'ボ', 'ブァ', 'ブェ', 'ブェ', 'ビョ', 'ブ', 'ブォ', 'ブェ', 'ブィ', 'ビュ', 'ブ', 'ブイ', 'ビ'),
    # ㅈ -> j
    12: ('ジャ', 'ジェ', 'ジャ', 'ジェ', 'ジョ', 'ジェ', 'ジョ', 'ジェ', 'ジョ', 'ジョァ', 'ジョェ', 'ジョェ', 'ジョ', 'ジュ', 'ジョ', 'ジェ', 'ジュィ', 'ジュ', 'ジュ', 'ジュイ', 'ジ'),
}

ENG_LETTER_MAP = {
    'A': '에이', 'B': '비', 'C': '씨', 'D': '디', 'E': '이', 'F': '에프',
    'G': '지', 'H': '에이치', 'I': '아이', 'J': '제이', 'K': '케이', 'L': '엘',
    'M': '엠', 'N': '엔', 'O': '오', 'P': '피', 'Q': '큐', 'R': '알',
    'S': '에스', 'T': '티', 'U': '유', 'V': '브이', 'W': '더블유', 'X': '엑스',
    'Y': '와이', 'Z': '제트'
}

COMMON_WORDS = {
    'AI': '에이아이', 'TTS': '티티에스', 'G2P': '지이피', 'API': '에이피아이',
    'UI': '유아이', 'UX': '유엑스', 'OS': '오에스', 'PC': '피씨',
    'CPU': '씨피유', 'GPU': '지피유', 'RAM': '램', 'SSD': '에스에스디',
    'URL': '유알엘', 'HTTP': '에이치티티피', 'HTTPS': '에이치티티피에스',
    'JSON': '제이슨', 'HTML': '에이치티엠엘', 'CSS': '씨에스에스', 'JS': '제이에스',
    'PDF': '피디에프', 'DB': '디비', 'SQL': '에스큐엘', 'LLM': '엘엘엠'
}

_g2p_instance = None
_g2p_failed = False

def get_g2p():
    global _g2p_instance, _g2p_failed
    if _g2p_instance is None and not _g2p_failed:
        try:
            from g2pk2 import G2p
            _g2p_instance = G2p()
        except Exception:
            _g2p_failed = True
    return _g2p_instance

def expand_english(text):
    if not text:
        return ""
    for k, v in sorted(COMMON_WORDS.items(), key=lambda x: -len(x[0])):
        text = re.sub(r'(?i)\b' + re.escape(k) + r'(?=[^a-zA-Z]|$)', v, text)
    def repl_caps(m):
        return ''.join(ENG_LETTER_MAP.get(c, c) for c in m.group(0))
    text = re.sub(r'[A-Z]{2,}', repl_caps, text)
    return text

def apply_g2p(text):
    if not text:
        return ""
    text = expand_english(text)
    g2p = get_g2p()
    if g2p:
        try:
            return g2p(text)
        except Exception:
            return text
    return text

def decompose(ch):
    code = ord(ch) - 0xAC00
    if 0 <= code <= 11171:
        jong = code % 28
        code //= 28
        jung = code % 21
        cho = code // 21
        return [cho, jung, jong]
    return None

def compose(cho, jung, jong):
    return chr(0xAC00 + (cho * 21 + jung) * 28 + jong)

def to_katakana(text, use_g2p=True):
    if not text:
        return ""

    if use_g2p:
        text = apply_g2p(text)

    tokens = []
    # Tokenize Hangul vs non-Hangul
    for ch in text:
        dec = decompose(ch)
        if dec:
            tokens.append({"type": "hangul", "dec": dec, "raw": ch})
        else:
            tokens.append({"type": "other", "raw": ch})

    # Phonological modifications (Liaison & Nasalization fallback)
    for i in range(len(tokens) - 1):
        t1 = tokens[i]
        t2 = tokens[i+1]
        if t1["type"] == "hangul" and t2["type"] == "hangul":
            c1, j1, tail1 = t1["dec"]
            c2, j2, tail2 = t2["dec"]

            # Liaison: tail meets ㅇ (c2 == 11)
            if tail1 != 0 and c2 == 11:
                jong_char = JONG_LIST[tail1]
                cho_idx = None
                if jong_char in ('ㄱ', 'ㄲ', 'ㅋ'): cho_idx = 0
                elif jong_char in ('ㄴ', 'ㄵ', 'ㄶ'): cho_idx = 2
                elif jong_char in ('ㄷ', 'ㅅ', 'ㅆ', 'ㅈ', 'ㅊ', 'ㅌ', 'ㅎ'): cho_idx = 3
                elif jong_char in ('ㄹ', 'ㄺ', 'ㄼ', 'ㄽ', 'ㄾ', 'ㅀ'): cho_idx = 5
                elif jong_char in ('ㅁ', 'ㄻ'): cho_idx = 6
                elif jong_char in ('ㅂ', 'ㄿ', 'ㅄ'): cho_idx = 7

                if cho_idx is not None:
                    t1["dec"][2] = 0
                    t2["dec"][0] = cho_idx

            # Nasalization: tail meets ㄴ/ㅁ (c2 in (2, 6))
            elif tail1 != 0 and c2 in (2, 6):
                jong_char = JONG_LIST[tail1]
                if jong_char in ('ㄱ', 'ㄲ', 'ㄳ', 'ㅋ', 'ㄺ'):
                    t1["dec"][2] = 21 # ㅇ (ng)
                elif jong_char in ('ㄷ', 'ㅅ', 'ㅆ', 'ㅈ', 'ㅊ', 'ㅌ', 'ㅎ'):
                    t1["dec"][2] = 4  # ㄴ (n)
                elif jong_char in ('ㅂ', 'ㅍ', 'ㄼ', 'ㄿ', 'ㅄ'):
                    t1["dec"][2] = 16 # ㅁ (m)

    # Convert to Katakana
    result = []
    prev_has_sonorant = False

    for i, tok in enumerate(tokens):
        if tok["type"] != "hangul":
            result.append(tok["raw"])
            prev_has_sonorant = False
            continue

        cho, jung, jong = tok["dec"]

        # Voiced if preceded by vowel or ㄴ, ㄹ, ㅁ, ㅇ
        use_voiced = prev_has_sonorant and (cho in VOICED_MAP)

        if use_voiced:
            syl = VOICED_MAP[cho][jung]
        else:
            syl = KANA_TABLE.get(cho, KANA_TABLE[11])[jung]

        # Jongseong (tail)
        tail_str = ""
        if jong != 0:
            jong_char = JONG_LIST[jong]
            next_is_hangul = (i + 1 < len(tokens) and tokens[i+1]["type"] == "hangul")

            if jong_char in ('ㄱ', 'ㄲ', 'ㄳ', 'ㅋ'):
                tail_str = 'ッ' if next_is_hangul else 'ク'
            elif jong_char in ('ㄴ', 'ㄵ', 'ㄶ'):
                tail_str = 'ン'
            elif jong_char in ('ㄷ', 'ㅅ', 'ㅆ', 'ㅈ', 'ㅊ', 'ㅌ', 'ㅎ'):
                tail_str = 'ッ'
            elif jong_char in ('ㄹ', 'ㄺ', 'ㄼ', 'ㄽ', 'ㄾ', 'ㅀ'):
                tail_str = 'ル'
            elif jong_char in ('ㅁ', 'ㄻ'):
                tail_str = 'ム'
            elif jong_char in ('ㅂ', 'ㅍ', 'ㅄ'):
                tail_str = 'プ'
            elif jong_char == 'ㅇ':
                tail_str = 'ン'

        result.append(syl + tail_str)

        if jong == 0:
            prev_has_sonorant = True
        elif jong in (4, 8, 16, 21): # ㄴ, ㄹ, ㅁ, ㅇ
            prev_has_sonorant = True
        else:
            prev_has_sonorant = False

    res_str = "".join(result)
    # Deduplicate consecutive small tsu or n
    res_str = re.sub(r'ッ{2,}', 'ッ', res_str)
    res_str = re.sub(r'ン{2,}', 'ン', res_str)
    return res_str

if __name__ == '__main__':
    tests = [
        "알겠는のだ! 이제부터 한국어로 말하겠는のだ!",
        "한국어 발음을 개선하기 위해 G2P를 거치는のだ!",
        "TTS 음질이 아주 자연스럽고 매끄러운のだ!",
        "닭볶음탕과 짬뽕을 같이 먹었는のだ!"
    ]
    for t in tests:
        print(t, "->", to_katakana(t))
