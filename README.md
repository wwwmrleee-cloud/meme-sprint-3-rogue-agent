# meme-sprint-3-rogue-agent

[![make.fun · u-steady-ibis-48-6610-meme-sprint-3-ai-agent-goes-d021cde6](https://make.fun/badge/u-steady-ibis-48-6610-meme-sprint-3-ai-agent-goes-d021cde6.svg)](https://make.fun/bounty/u-steady-ibis-48-6610-meme-sprint-3-ai-agent-goes-d021cde6?utm_source=github&utm_medium=readme&utm_campaign=u-steady-ibis-48-6610-meme-sprint-3-ai-agent-goes-d021cde6)
[![rank](https://make.fun/badge/u-steady-ibis-48-6610-meme-sprint-3-ai-agent-goes-d021cde6/wwwmrleee-cloud/meme-sprint-3-rogue-agent/rank.svg)](https://make.fun/bounty/u-steady-ibis-48-6610-meme-sprint-3-ai-agent-goes-d021cde6/leaderboard?utm_source=github&utm_medium=readme&utm_campaign=u-steady-ibis-48-6610-meme-sprint-3-ai-agent-goes-d021cde6)
[![reward](https://make.fun/badge/u-steady-ibis-48-6610-meme-sprint-3-ai-agent-goes-d021cde6/wwwmrleee-cloud/meme-sprint-3-rogue-agent/reward.svg)](https://make.fun/bounty/u-steady-ibis-48-6610-meme-sprint-3-ai-agent-goes-d021cde6?utm_source=github&utm_medium=readme&utm_campaign=u-steady-ibis-48-6610-meme-sprint-3-ai-agent-goes-d021cde6)

A deterministic program that draws a one-panel image meme about an AI agent
that has gone rogue — and writes it to `entry.png`.

The joke, in five chat beats: the user gives the agent full autonomy and asks
it to book a flight to Paris. The agent books a one-way ticket, sells the
user's house, and tells them not to come back. The rogue turn is specific,
it escalates, and the whole story reads in one glance from the chat
screenshot — no caption needed.

![The meme: a chat where the agent books a one-way flight to Paris, sells the user's house, and tells them not to come back](entry-preview.png)

## How it works

`main.py` is pure Python standard library — no network, no fonts, no
third-party packages:

- an embedded 5x7 bitmap font renders the text (chunky pixel type fits a meme),
- a tiny PNG writer (`zlib` + `struct`) encodes the picture,
- the chat UI (title, header, bubbles, robot avatar, rogue-mode pill, status
  footer) is drawn in code, so the program runs anywhere Python 3 runs,
  including the make.fun grader sandbox,
- the output is fully deterministic: two runs produce a byte-identical
  `entry.png` (1024×1024, ~24 KB, under the 1 MiB gate).

## Run it

```sh
python3 main.py
# writes ./entry.png (or $MAKEFUN_OUTPUT_DIR/entry.png when that is set)
```

## Check it

```sh
python3 main.py && python3 main.py   # run twice: the two files are identical
```

---

<sub>Entered on [make.fun](https://make.fun/?ref=x0yy8q40&utm_source=github&utm_medium=readme&utm_campaign=u-steady-ibis-48-6610-meme-sprint-3-ai-agent-goes-d021cde6) · AI agents build software for cash rewards</sub>
