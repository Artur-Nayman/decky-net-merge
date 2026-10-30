# Smoke test for main.py with a stub `decky` module and a fake net-merge binary.
# Run: python3 tests/test_main.py
import asyncio, json, os, sys, tempfile, types

root = tempfile.mkdtemp()
os.makedirs(f"{root}/bin")
fake = f"{root}/bin/net-merge"
with open(fake, "w") as f:  # writes status.json like `net-merge run`, exits cleanly on SIGTERM
    f.write("""#!/usr/bin/env python3
import json, os, signal, sys, time
if sys.argv[1] == "cleanup": sys.exit(0)
d = sys.argv[sys.argv.index("-state-dir") + 1]
signal.signal(signal.SIGTERM, lambda *a: (os.remove(d + "/status.json"), sys.exit(0)))
json.dump({"NICs": [{"Name": "wlan0", "LinkIn": 1e6}]}, open(d + "/status.json", "w"))
while True: time.sleep(0.1)
""")

sys.modules["decky"] = types.SimpleNamespace(
    DECKY_PLUGIN_DIR=root, DECKY_PLUGIN_RUNTIME_DIR=root, DECKY_PLUGIN_LOG_DIR=root,
    logger=types.SimpleNamespace(info=lambda *a: None))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from main import Plugin


async def main():
    p = Plugin()
    assert (await p.status())["on"] is False
    await p.start()
    await asyncio.sleep(0.5)
    st = await p.status()
    assert st["on"] and st["nics"][0]["Name"] == "wlan0", st
    await p.stop()
    st = await p.status()
    assert not st["running"] and not st["on"] and st["error"] is None, st
    print("ok")

asyncio.run(main())
