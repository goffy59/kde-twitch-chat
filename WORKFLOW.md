Got it — you want **plain, human documentation** that tells you **how to edit this project**, not more tooling or automation. Something you can read later when your brain is fried and just follow.

Here’s a **simple, no-bullshit guide** you can paste into your repo as something like `HOW_TO_EDIT.md` (or fold into README if you want).

---

# How to Edit & Update This Project (For Future Me)

This repo lives at:

```
~/twitch-kde-chat-working
```

That folder is the **source of truth**.
Nothing outside it should be edited by hand.

---

## The files that actually matter

### 1) `twitch_kde_chat.py` — the program

This is the Twitch chat listener and notification logic.

Edit this file when you want to:

* change how messages are displayed
* change batching / timing
* add filters, keywords, highlights
* debug Twitch IRC behavior

Edit it with:

```bash
cd ~/twitch-kde-chat-working
nano twitch_kde_chat.py
```

After editing, you **must reinstall** (see below).

---

### 2) `install.sh` — deploys changes to the system

This script copies files into the correct live locations and restarts the service.

Edit this file when you want to:

* change install paths
* change environment variables
* add flags like `--check` later
* change how systemd is handled

Edit it with:

```bash
nano install.sh
```

You normally **do not** need to touch this unless you’re changing install behavior.

---

### 3) `twitch-kde-chat.service` — systemd user service template

This is the **template** unit file tracked in git.

Edit this file when you want to:

* change startup ordering
* change restart behavior
* add/remove environment defaults
* toggle debug defaults

⚠️ Rules:

* MUST use `%h` (never `/home/username`)
* SHOULD NOT hardcode the channel
* Debug should stay commented by default

Edit it with:

```bash
nano twitch-kde-chat.service
```

---

## How changes actually take effect (important)

Editing files in the repo **does nothing by itself**.

To apply changes to the running system, you must **reinstall**:

```bash
cd ~/twitch-kde-chat-working
./install.sh hopelessdystopian
```

This:

* copies `twitch_kde_chat.py` into `~/.local/share/twitch-kde-chat/`
* installs the systemd unit into `~/.config/systemd/user/`
* writes the channel override
* restarts the service

---

## How to verify it’s working

### Check service status

```bash
systemctl --user status twitch-kde-chat.service --no-pager
```

### Watch logs

```bash
journalctl --user -u twitch-kde-chat.service -f
```

### Test notifications manually

```bash
systemd-run --user --wait --collect \
  /usr/bin/notify-send "Twitch Chat" "Test" "hello"
```

If this works but chat doesn’t, the problem is in `twitch_kde_chat.py`.

---

## How to save changes to GitHub

After you edit and test:

```bash
cd ~/twitch-kde-chat-working

git status        # see what changed
git add -A
git commit -m "Describe what you changed"
git push
```

If push fails:

```bash
git pull --rebase
git push
```

---

## Emergency recovery (“I broke something”)

This resets the live system to whatever is in the repo:

```bash
cd ~/twitch-kde-chat-working
./install.sh hopelessdystopian
systemctl --user restart twitch-kde-chat.service
journalctl --user -u twitch-kde-chat.service -n 80 --no-pager
```

---

## Mental model (remember this)

* **Repo = blueprint**
* **install.sh = deploy**
* **systemd = keeps it alive**
* If it’s weird: check logs
* If it’s really weird: reinstall

That’s it. Nothing else is hiding.

---
