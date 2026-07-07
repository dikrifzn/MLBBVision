import re


# GOLD

def parse_gold(text: str) -> int:

    if not text:
        return 0

    text = text.replace(",", "")
    text = text.replace(".", "")
    text = text.replace(" ", "")

    number = re.findall(r"\d+", text)

    if not number:
        return 0

    return int("".join(number))


# LEVEL

def parse_level(text: str) -> int:

    if not text:
        return 0

    number = re.findall(r"\d+", text)

    if not number:
        return 0

    value = int(number[0])

    # Level MLBB maksimal 15
    value = max(1, min(15, value))

    return value


# SCORE (BO SCORE)

def parse_score(text: str) -> int:

    if not text:
        return 0

    number = re.findall(r"\d+", text)

    if not number:
        return 0

    return int(number[0])


# GAME DURATION

def parse_duration(text: str) -> str:

    if not text:
        return ""

    text = text.replace(".", ":")

    m = re.search(r"(\d{1,2})\D+(\d{2})", text)

    if m:

        minute = int(m.group(1))
        second = int(m.group(2))

        return f"{minute}:{second:02d}"

    return ""


# KDA

def parse_kda(text: str) -> str:

    if not text:
        return ""

    # OCR sering salah membaca separator
    text = text.replace("|", "/")
    text = text.replace("\\", "/")
    text = text.replace("I", "/")
    text = text.replace("l", "/")
    text = text.replace("-", "/")

    m = re.search(r"(\d+)\D+(\d+)\D+(\d+)", text)

    if not m:
        return ""

    kill = int(m.group(1))
    death = int(m.group(2))
    assist = int(m.group(3))

    return f"{kill}/{death}/{assist}"


# PLAYER NAME

def parse_name(text: str) -> str:

    if not text:
        return ""

    text = text.strip()

    text = re.sub(r"\s+", " ", text)

    return text


# UNIVERSAL

def clean_text(text: str) -> str:

    if not text:
        return ""

    text = text.replace("\n", " ")

    text = re.sub(r"\s+", " ", text)

    return text.strip()