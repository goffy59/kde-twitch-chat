#!/usr/bin/env python3
import os
import re
import socket
import time
import random
import subprocess
from collections import deque

CHANNEL = os.environ.get("TWITCH_CHANNEL", "hopelessdystopian").strip().lstrip("#")
HOST = os.environ.get("TWITCH_IRC_HOST", "irc.chat.twitch.tv").strip()
PORT = int(os.environ.get("TWITCH_IRC_PORT", "6667"))

REPLACE_ID = int(os.environ.get("TWITCH_NOTIFY_REPLACE_ID", "424242"))
TIMEOUT_MS = int(os.environ.get("TWITCH_NOTIFY_TIMEOUT_MS", "30000"))
BATCH_WINDOW_SEC = float(os.environ.get("TWITCH_NOTIFY_BATCH_WINDOW_SEC", "0.8"))
MAX_LINES = int(os.environ.get("TWITCH_NOTIFY_MAX_LINES", "6"))

DEBUG = os.environ.get("TWITCH_DEBUG", "0").strip() not in ("0", "false", "False")

# Accept optional Twitch IRC tags prefix:
#   @tag1=...;tag2=... :nick!user@host PRIVMSG #chan :message
PRIVMSG_RE = re.compile(r"^(?:@[^ ]+ )?:(?P<nick>[^!]+)![^ ]+ PRIVMSG #(?P<chan>[^ ]+) :(?P<msg>.*)$")

def dlog(msg: str) -> None:
    if DEBUG:
        print(f"[twitch-kde-chat] {msg}", flush=True)

def notify(title: str, body: str) -> None:
    # KDE/Plasma can "update" a notification without showing a popup when -r is used.
    # So: avoid replace-id for chat messages. Still efficient because we batch.
    cmd = [
        "/usr/bin/notify-send",
        "-a", "Twitch Chat",
        "-t", str(TIMEOUT_MS),
        # Make Plasma treat it as attention-worthy
        "-u", "normal",
        "-h", "string:category:im.received",
        "-h", "boolean:transient:true",
        title,
        body,
    ]
    p = subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE, text=True, check=False)
    if DEBUG:
        err = (p.stderr or "").strip()
        print(f"[twitch-kde-chat] notify rc={p.returncode} err={err}", flush=True)

def send(s: socket.socket, line: str) -> None:
    s.sendall((line + "\r\n").encode("utf-8", "ignore"))

def connect_and_join() -> socket.socket:
    dlog(f"connecting to {HOST}:{PORT} channel=#{CHANNEL}")
    s = socket.create_connection((HOST, PORT), timeout=10)
    s.settimeout(0.5)

    nick = f"justinfan{random.randint(10000, 99999)}"
    send(s, "PASS SCHMOOPIIE")
    send(s, f"NICK {nick}")
    send(s, "CAP REQ :twitch.tv/tags twitch.tv/commands")
    send(s, f"JOIN #{CHANNEL}")
    return s

def main() -> int:
    notify("Twitch chat", f"Starting… #{CHANNEL}")
    dlog("started")

    pending = deque()
    last_flush = time.monotonic()
    buf = ""
    backoff = 1.0

    while True:
        try:
            s = connect_and_join()
            notify("Twitch chat", f"Connected — listening to #{CHANNEL}")
            dlog("connected")
            backoff = 1.0
            buf = ""
            pending.clear()
            last_flush = time.monotonic()

            while True:
                now = time.monotonic()
                got_line = False

                try:
                    data = s.recv(4096)
                    if not data:
                        raise ConnectionError("socket closed")
                    buf += data.decode("utf-8", "ignore")
                except socket.timeout:
                    pass

                while "\r\n" in buf:
                    line, buf = buf.split("\r\n", 1)
                    if not line:
                        continue
                    got_line = True

                    if line.startswith("PING "):
                        send(s, "PONG " + line[5:])
                        continue

                    m = PRIVMSG_RE.match(line)
                    if not m:
                        continue

                    nick = m.group("nick").strip()
                    msg = m.group("msg").strip()
                    if msg:
                        pending.append((nick, msg))
                        dlog(f"msg {nick}: {msg[:120]}")

                if pending and (now - last_flush >= BATCH_WINDOW_SEC):
                    items = list(pending)[-MAX_LINES:]
                    pending.clear()
                    body = "\n".join([f"{u}: {t}" for (u, t) in items])
                    notify(f"#{CHANNEL}", body)
                    last_flush = now

                if not got_line:
                    time.sleep(0.05)

        except Exception as e:
            dlog(f"disconnected: {type(e).__name__}: {e}")
            try:
                notify("Twitch chat", f"Disconnected — reconnecting…")
            except Exception:
                pass
            time.sleep(backoff)
            backoff = min(backoff * 1.7, 60.0)

if __name__ == "__main__":
    raise SystemExit(main())
