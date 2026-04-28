EXCLUDED_WORDS = {
    "hi", "hello", "hey", "bye", "ok", "okay", "yes", "no", "thanks",
    "thank", "you", "pls", "please", "np", "no problem", "sorry", "lol",
    "lmao", "haha", "wow", "omg", "btw", "idk", "imo", "smh", "wtf",
    "gg", "wp", "gl", "hf", "brb", "tbh", "ty", "cya", "de", "ru",
    "wanna", "gonna", "gotta", "kinda", "sorta", "dunno", "yeah", "yep",
    "nope", "meh", "oops", "ugh", "hm", "ah", "oh", "uh", "um", "vs"
}


def strip_username(text: str) -> str:
    text = text.strip()
    if text.startswith("@"):
        parts = text.split(None, 1)
        if len(parts) > 1:
            return parts[1]
    return text


def is_english(text: str) -> bool:
    text = strip_username(text)
    if not text:
        return False
    first_char = text[0].lower()
    if not first_char.isalpha():
        return False
    return first_char.isascii()


def is_excluded(text: str) -> bool:
    text = strip_username(text)
    words = text.lower().split()

    if len(words) == 1 and words[0] in EXCLUDED_WORDS:
        return True

    alpha_words = [w for w in words if w.isalpha()]
    if not alpha_words:
        return True

    excluded_count = sum(1 for w in alpha_words if w.lower() in EXCLUDED_WORDS)
    if excluded_count == len(alpha_words):
        return True

    return False


def should_correct(text: str) -> bool:
    return is_english(text) and not is_excluded(text)
