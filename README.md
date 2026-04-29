# plugram

A modular Telegram userbot. Commands use the `.` prefix (`.ask`, `.tldr`, `.fact`, `.twin`, `.mod`), plus passive modules (e.g. auto-fixing English/Russian mix in your messages).

## Vibe Code Alert

This project was 99% vibe-coded as a fun hack to make my own Telegram messaging a little weirder and a little smarter. I'm not going to support it in any way — it's posted here as-is for other people's inspiration, and I don't intend to harden it. Code is ephemeral now and libraries are over: ask your LLM to change it in whatever way you like.

(Inspired by the disclaimer on [karpathy/llm-council](https://github.com/karpathy/llm-council).)

## Quick start

```bash
git clone <repo> ~/plugram && cd ~/plugram
uv sync
cp .env.example .env && $EDITOR .env   # paste TELEGRAM_API_ID, TELEGRAM_API_HASH, OPENROUTER_API_KEY
uv run python -m plugram               # first run will ask for the Telegram code; subsequent runs won't
```

Then in any Telegram chat (Saved Messages is the safest place to play):

```
.help            ← list modules and commands
.ask hi          ← ask the LLM
.mod off translate   ← disable a module
```

## Credentials

You need three secrets before the first run.

### `TELEGRAM_API_ID` and `TELEGRAM_API_HASH`

These identify the *application* (not your account) to Telegram's MTProto API. They are free and personal — don't share them.

1. Open [my.telegram.org](https://my.telegram.org) and log in with your phone number (Telegram sends a one-time code to your account).
2. Click **API development tools**.
3. Fill the form: any **App title** and **Short name** work (e.g. `plugram`). Pick **Desktop** or **Other** for platform. URL/description can be empty.
4. Click **Create application**.
5. Copy the resulting **App api_id** (a number) and **App api_hash** (a hex string) into `.env`.

The page shows the values once — if you lose the hash, you can come back to the same page and reveal it again with your account.

### `OPENROUTER_API_KEY`

Used for all LLM calls (default model: `deepseek/deepseek-v3.2`).

1. Sign up / log in at [openrouter.ai](https://openrouter.ai).
2. Open [openrouter.ai/keys](https://openrouter.ai/keys) and click **Create Key**.
3. Copy the key (shown only once) into `.env`.
4. Top up some credits at [openrouter.ai/credits](https://openrouter.ai/credits) — DeepSeek is cheap, a couple of dollars lasts a long time.

## Install

You'll need [uv](https://docs.astral.sh/uv/).

```bash
git clone <repo> ~/plugram
cd ~/plugram
uv sync
cp .env.example .env
$EDITOR .env   # paste the three values from the Credentials section above
```

## First run

```bash
uv run python -m plugram
```

Telethon will prompt for your phone number and the confirmation code Telegram sends you. After a successful login the session is saved to `data/session.session`, so subsequent runs don't need the code.

## Running on a VPS in tmux

```bash
tmux new -s plugram
cd ~/plugram && uv run python -m plugram
# Ctrl+B, then D — detach (the bot keeps running)
# tmux attach -t plugram — reattach to see logs
```

## Commands

- `.help` or `.mod help` — module help
- `.mod` — list modules with on/off status
- `.mod on <name>` / `.mod off <name>` — enable/disable a module
- `.ask <text>` (alias `.a`) — ask the LLM
- `.tldr [N|Nm|Nh|Nd]` — summarize the last N messages, the last period, or a replied-to message
- `.fact` (as a reply) — objective breakdown of an argument thread
- `.twin <text>` or `.twin` (as a reply) — answer in your own writing style
- `.twin stats` — corpus size
- `.twin import @channel` — import channel posts into the corpus

## Modules

Module on/off state lives in `data/config.toml`. Defaults are baked into the code — the file is created on first run.

| Module | Type | What it does |
|---|---|---|
| `translate` | passive | Auto-fix messages that start in English (or mix English/Russian) |
| `ask` | command | `.ask` / `.a` — query the LLM, optionally with a replied-to message as context |
| `tldr` | command | `.tldr` — summarize last N messages, a time window, or a replied-to message |
| `fact` | command | `.fact` — objective analysis of a reply-chain argument |
| `twin` | command + passive | `.twin` — reply in your style, plus background corpus collection |
| `manage` | command | `.mod` / `.help` — toggle modules |
