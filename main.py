import json
import os
import subprocess
import time

import decky

BIN = os.path.join(decky.DECKY_PLUGIN_DIR, "bin", "net-merge")
STATE_DIR = decky.DECKY_PLUGIN_RUNTIME_DIR
LOG = os.path.join(decky.DECKY_PLUGIN_LOG_DIR, "net-merge.log")


class Plugin:
    proc = None

    def _running(self):
        return self.proc is not None and self.proc.poll() is None

    async def start(self):
        if self._running():
            return True
        os.chmod(BIN, 0o755)  # zip extraction can drop the exec bit
        # -stats 0: status.json already has the numbers, no need to spam the log
        self.proc = subprocess.Popen(
            [BIN, "run", "-state-dir", STATE_DIR, "-stats", "0", "-log", LOG],
            stdin=subprocess.DEVNULL, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
        )
        decky.logger.info("started net-merge pid %d", self.proc.pid)
        return True

    async def stop(self):
        if not self._running():
            return True
        self.proc.terminate()  # SIGTERM: net-merge removes its TUN and routes itself
        try:
            self.proc.wait(timeout=10)
        except subprocess.TimeoutExpired:
            self.proc.kill()
            self.proc.wait()
            self._cleanup()
        self.proc = None
        return True

    async def status(self):
        st = None
        try:
            with open(os.path.join(STATE_DIR, "status.json")) as f:
                st = json.load(f)
        except (OSError, ValueError):
            pass
        on = self._running() and st is not None
        err = None
        if self.proc is not None and not self._running():
            err = self._log_tail()  # it died: show why
        return {"running": self._running(), "on": on, "nics": (st.get("NICs") or []) if on else [],"error": err}

    def _log_tail(self):
        try:
            with open(LOG) as f:
                return "".join(f.readlines()[-3:]).strip() or None
        except OSError:
            return None

    def _cleanup(self):
        subprocess.run([BIN, "cleanup"], stdin=subprocess.DEVNULL, capture_output=True, timeout=15)

    async def _main(self):
        # A crash or hard power-off can leave routes pointing at a TUN that no longer exists.
        self._cleanup()

    async def _unload(self):
        await self.stop()

    async def _uninstall(self):
        await self.stop()
