import asyncio
import json
import logging
import re
from pathlib import Path

from .base import Command, Module


log = logging.getLogger(__name__)

DATA_DIR = Path(__file__).resolve().parent.parent.parent / "data"
DUMPS_DIR = DATA_DIR / "dumps"

USAGE = "Usage: `.dump @channel [N]` or `.dump reset @channel`"


def _slug(channel: str) -> str:
    cleaned = channel.lstrip("@").strip("/").replace("https://t.me/", "").replace("t.me/", "")
    slug = re.sub(r"[^\w-]+", "_", cleaned).strip("_")
    return slug or "channel"


def _dump_path(channel: str) -> Path:
    return DUMPS_DIR / f"{_slug(channel)}.json"


def _read_existing(path: Path) -> list[dict]:
    if not path.exists():
        return []
    try:
        with path.open("r", encoding="utf-8") as f:
            data = json.load(f)
        if isinstance(data, list):
            return data
    except (json.JSONDecodeError, OSError):
        log.warning("Could not read %s, starting fresh", path)
    return []


def _last_message_id(messages: list[dict]) -> int:
    ids = [m.get("message_id", 0) for m in messages if isinstance(m, dict)]
    return max(ids) if ids else 0


def _atomic_write(path: Path, data: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    with tmp.open("w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    tmp.replace(path)


class DumpModule(Module):
    description = (
        "Export channel posts to JSON. `.dump @channel` collects all messages "
        "(incremental: subsequent runs only fetch new posts). Optional `N` limits a single call: "
        "`.dump @channel 100`. `.dump reset @channel` drops the cached dump. "
        "Cache lives in `data/dumps/`."
    )
    triggers = [Command("dump", aliases=["d"])]

    async def handle(self, event, command, args) -> None:
        tokens = (args or "").split()
        if not tokens:
            await event.message.reply(USAGE)
            return

        if tokens[0].lower() == "reset":
            if len(tokens) < 2:
                await event.message.reply(USAGE)
                return
            await self._reset(event, tokens[1])
            return

        channel = tokens[0]
        limit: int | None = None
        if len(tokens) >= 2:
            try:
                limit = int(tokens[1])
            except ValueError:
                await event.message.reply(USAGE)
                return
            if limit <= 0:
                await event.message.reply(USAGE)
                return

        asyncio.create_task(self._dump(event, channel, limit))

    async def _reset(self, event, channel: str) -> None:
        path = _dump_path(channel)
        if path.exists():
            try:
                path.unlink()
            except OSError as e:
                log.exception("Failed to remove dump cache")
                await event.message.reply(f"Reset failed: {e}")
                return
            await event.message.reply(f"Reset cache for {channel}.")
        else:
            await event.message.reply(f"No cache for {channel}.")

    async def _dump(self, event, channel: str, limit: int | None) -> None:
        try:
            path = _dump_path(channel)
            existing = _read_existing(path)
            last_id = _last_message_id(existing)

            await event.message.reply(f"Dumping {channel}...")

            new_messages: list[dict] = []
            async for m in self.ctx.client.iter_messages(channel, min_id=last_id, limit=limit):
                if not m.text:
                    continue
                new_messages.append({
                    "message_id": m.id,
                    "date": m.date.isoformat() if m.date else None,
                    "text": m.text,
                })

            combined = new_messages + existing
            _atomic_write(path, combined)

            await event.message.reply(
                f"{channel}: +{len(new_messages)}, total {len(combined)}",
                file=str(path),
            )
        except Exception as e:
            log.exception("Dump failed")
            await event.message.reply(f"Dump failed: {e}")
