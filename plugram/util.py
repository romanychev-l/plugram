async def walk_reply_chain(message, max_depth: int = 10) -> list:
    """Walk back through reply_to links starting from `message`.

    Returns a list ordered oldest-first, including `message` at the end.
    """
    chain = [message]
    current = message
    while len(chain) < max_depth and getattr(current, "is_reply", False):
        parent = await current.get_reply_message()
        if parent is None:
            break
        chain.append(parent)
        current = parent
    chain.reverse()
    return chain


def format_messages(messages, max_chars: int = 12000) -> str:
    """Format an iterable of Telethon messages as `Author: text` lines, oldest-first.

    Truncates from the start if total length exceeds `max_chars`.
    """
    lines = []
    for m in messages:
        text = (m.text or "").strip()
        if not text:
            continue
        sender = getattr(m, "sender", None)
        name = "?"
        if sender is not None:
            name = (
                getattr(sender, "first_name", None)
                or getattr(sender, "username", None)
                or str(getattr(sender, "id", "?"))
            )
        lines.append(f"{name}: {text}")
    joined = "\n".join(lines)
    if len(joined) > max_chars:
        joined = "...\n" + joined[-max_chars:]
    return joined
