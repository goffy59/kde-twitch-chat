Twitch KDE Chat Overlay (Wayland / Plasma) — Known-Good Setup
============================================================

What this is
------------
A lightweight Twitch chat overlay implemented as KDE/Plasma notifications.
Designed to work reliably on Fedora Kinoite (Wayland, KDE, AMD) without
fragile hacks, fullscreen issues, or third-party IRC wrappers.

This connects directly to Twitch IRC using an anonymous login and shows
batched chat messages as Plasma popups while gaming.

No OBS required. No window overlays. No MangoHud hacks. No Bottles nonsense.

Everything lives in ONE place:
-------------------------------
This directory is the source of truth:

  ~/twitch-kde-chat-working/

Contents:
  README.txt            ← this file
  install.sh            ← the only installer you should ever run
  twitch_kde_chat.py    ← the canonical, known-good Python script
  twitch-kde-chat.service (optional reference copy)

The installer copies files into the correct user locations automatically.

Live install locations (managed by install.sh):
------------------------------------------------
Python app:
  ~/.local/share/twitch-kde-chat/twitch_kde_chat.py

systemd user service:
  ~/.config/systemd/user/twitch-kde-chat.service

Logs:
  journalctl --user -u twitch-kde-chat.service -f

How it works (important details)
--------------------------------
• Uses direct Twitch IRC (socket connection) — no twitch_chat_irc module
• Supports Twitch IRC @tags (required for modern Twitch)
• Anonymous login (justinfan####)
• Wayland-safe systemd --user service
• Imports KDE/Plasma session environment correctly
• NO notification replace-id (Plasma can suppress popups when replace-id is used)
• Batches messages to avoid FPS drops

Why popups actually show (the hard-earned lesson)
--------------------------------------------------
KDE Plasma may silently update notifications without showing popups if:
  - replace-id is used
  - the service lacks the correct DBus session environment

This setup avoids both problems.

Install / reinstall (safe to re-run anytime)
---------------------------------------------
From this directory:

  cd ~/twitch-kde-chat-working
  ./install.sh hopelessdystopian

You can rerun the installer:
• after Plasma updates
• after system reinstalls
• after systemd breakage
• whenever something stops working

It is idempotent and cleans up broken overrides automatically.

Start / stop manually
---------------------
Start (enable + run now):
  systemctl --user enable --now twitch-kde-chat.service

Stop:
  systemctl --user stop twitch-kde-chat.service

Status:
  systemctl --user status twitch-kde-chat.service --no-pager

Configuration (environment variables)
-------------------------------------
Set these by editing the systemd unit if needed:

  TWITCH_CHANNEL                 (default: hopelessdystopian)
  TWITCH_IRC_HOST                (default: irc.chat.twitch.tv)
  TWITCH_IRC_PORT                (default: 6667)
  TWITCH_NOTIFY_TIMEOUT_MS       (default: 30000)
  TWITCH_NOTIFY_BATCH_WINDOW_SEC (default: 0.8)
  TWITCH_NOTIFY_MAX_LINES        (default: 6)
  TWITCH_DEBUG                   (set to 1 for verbose logs)

After changing the unit:
  systemctl --user daemon-reload
  systemctl --user restart twitch-kde-chat.service

Troubleshooting checklist (read this first)
--------------------------------------------
1) Does notify-send work from a user service?
   systemd-run --user --wait --collect /usr/bin/notify-send \
     -a "Twitch Chat" "Test" "Hello"

2) Is the service connected to Twitch?
   journalctl --user -u twitch-kde-chat.service -n 100 --no-pager
   Look for:
     connected
     msg username: text

3) Messages logged but no popup?
   Check Plasma notification rules for app "Twitch Chat"
   (they may be visible in history but suppressed as popups).

4) Everything broken?
   Just rerun:
     ./install.sh hopelessdystopian

Uninstall (clean removal)
-------------------------
systemctl --user disable --now twitch-kde-chat.service
rm -f ~/.config/systemd/user/twitch-kde-chat.service
rm -rf ~/.local/share/twitch-kde-chat
rm -rf ~/.config/systemd/user/twitch-kde-chat.service.d
systemctl --user daemon-reload

Final note
----------
This setup exists because many other approaches (OBS docks, MangoHud text,
Wayland overlays, Bottles hacks) are brittle or regress after updates.

This one is boring, direct, reproducible — and that’s the point.
