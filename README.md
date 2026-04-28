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

## Install

You'll need [uv](https://docs.astral.sh/uv/).

```bash
git clone <repo> ~/plugram
cd ~/plugram
uv sync
cp .env.example .env
# Fill in TELEGRAM_API_ID, TELEGRAM_API_HASH (https://my.telegram.org/apps)
# and OPENROUTER_API_KEY (https://openrouter.ai/keys)
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
