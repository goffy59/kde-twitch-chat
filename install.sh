#!/usr/bin/env bash
set -euo pipefail

# Twitch KDE Chat Overlay - one-place installer
# Canonical source dir: ~/twitch-kde-chat-working
# Safe to re-run. DO NOT use sudo.

CHANNEL="${1:-hopelessdystopian}"

BASE="$HOME/twitch-kde-chat-working"
SRC_PY="$BASE/twitch_kde_chat.py"
SRC_UNIT="$BASE/twitch-kde-chat.service"

APPDIR="$HOME/.local/share/twitch-kde-chat"
DST_PY="$APPDIR/twitch_kde_chat.py"

UNITDIR="$HOME/.config/systemd/user"
UNIT="$UNITDIR/twitch-kde-chat.service"
OVERRIDEDIR="$UNITDIR/twitch-kde-chat.service.d"
OVERRIDE="$OVERRIDEDIR/override.conf"

die() { echo "ERROR: $*" >&2; exit 1; }

[[ "$EUID" -eq 0 ]] && die "Do NOT run with sudo/root."

command -v python3 >/dev/null || die "python3 missing"
command -v notify-send >/dev/null || die "notify-send missing"
command -v systemctl >/dev/null || die "systemctl missing"
command -v dbus-update-activation-environment >/dev/null || die "dbus-update-activation-environment missing"

[[ -f "$SRC_PY" ]] || die "Missing $SRC_PY"
[[ -f "$SRC_UNIT" ]] || die "Missing $SRC_UNIT"

echo "== Install Twitch KDE Chat =="
echo "Source:  $BASE"
echo "Channel: $CHANNEL"

# Install python app (live location)
mkdir -p "$APPDIR"
cp -f "$SRC_PY" "$DST_PY"
chmod +x "$DST_PY"

# Install systemd user unit from the repo copy (no drift)
mkdir -p "$UNITDIR"
cp -f "$SRC_UNIT" "$UNIT"

# Dynamic config via override (safe + rerunnable)
mkdir -p "$OVERRIDEDIR"
cat > "$OVERRIDE" <<EOF
[Service]
Environment=TWITCH_CHANNEL=$CHANNEL
EOF

# Reload + restart
systemctl --user daemon-reload
systemctl --user enable twitch-kde-chat.service >/dev/null 2>&1 || true
systemctl --user restart twitch-kde-chat.service

echo
echo "DONE."
echo "Status:"
echo "  systemctl --user status twitch-kde-chat.service --no-pager"
echo "Logs:"
echo "  journalctl --user -u twitch-kde-chat.service -f"
