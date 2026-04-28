import logging
import os
from dataclasses import dataclass, field
from pathlib import Path

from dotenv import load_dotenv
from telethon import TelegramClient, events

from .config import Config
from .corpus import Corpus
from .dispatcher import Dispatcher
from .llm import LLM


log = logging.getLogger(__name__)

DATA_DIR = Path(__file__).resolve().parent.parent / "data"


@dataclass
class Context:
    client: TelegramClient
    llm: LLM
    corpus: Corpus
    config: Config
    dispatcher: Dispatcher | None = field(default=None)


def _require_env(name: str) -> str:
    value = os.getenv(name)
    if not value:
        raise SystemExit(
            f"Missing {name} in .env. Copy .env.example to .env and fill it in."
        )
    return value


async def run() -> None:
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(name)s: %(message)s",
    )
    load_dotenv()

    api_id = _require_env("TELEGRAM_API_ID")
    api_hash = _require_env("TELEGRAM_API_HASH")
    openrouter_key = _require_env("OPENROUTER_API_KEY")

    DATA_DIR.mkdir(parents=True, exist_ok=True)
    config = Config(DATA_DIR / "config.toml")
    config.save()  # persist defaults on first run

    corpus = Corpus(DATA_DIR / "plugram.db")
    llm = LLM(openrouter_key, model=config.model)
    client = TelegramClient(str(DATA_DIR / "session"), api_id, api_hash)

    ctx = Context(client=client, llm=llm, corpus=corpus, config=config)
    dispatcher = Dispatcher(ctx)
    ctx.dispatcher = dispatcher

    @client.on(events.NewMessage(outgoing=True))
    async def _on_outgoing(event):
        await dispatcher.dispatch(event)

    await client.start()
    log.info("plugram is up. Modules: %s", ", ".join(dispatcher.modules) or "(none)")
    try:
        await client.run_until_disconnected()
    finally:
        corpus.close()
