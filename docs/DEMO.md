# Demo and capture guide

Run the deterministic demo:

```bash
python3 scripts/demo.py
```

No installation is required. `make demo` is an equivalent convenience command.

It starts a temporary loopback-only HTTP server, writes a temporary Markdown
file, and produces a report containing a healthy link, a same-host redirect,
and a broken link. The script opts into `--allow-private` solely for this trusted
local fixture and removes the temporary file on exit.

For a GIF or terminal recording:

1. Use an 80-100 column terminal with a readable font.
2. Start on the repository root with a clean prompt.
3. Record `python3 scripts/demo.py` from command to completed table.
4. Stop within 10 seconds; do not edit the output or imply public-network data.

Expected invariant: 3 unique links, with 1 healthy, 1 redirect, and 1 broken.
The random loopback port and temporary directory will vary.
