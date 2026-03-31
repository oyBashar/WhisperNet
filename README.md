# 🕶️ WhisperNet — Anonymous CLI Chat for Termux

<p align="center">
  <img src="https://img.shields.io/badge/Platform-Termux-green?style=for-the-badge&logo=android"/>
  <img src="https://img.shields.io/badge/Python-3.8+-blue?style=for-the-badge&logo=python"/>
  <img src="https://img.shields.io/badge/License-MIT-yellow?style=for-the-badge"/>
  <img src="https://img.shields.io/badge/Author-@oyBashar-purple?style=for-the-badge&logo=github"/>
</p>

<p align="center">
  <b>A lightweight, anonymous real-time chat tool for Termux</b><br/>
  Rooms · Encryption · Private DMs · Random Identities · Beautiful Terminal UI
</p>

---

> **Made by [@oyBashar](https://github.com/oyBashar)**

---

## ✨ Features

| Feature | Description |
|---|---|
| 🎭 **Auto Identity** | Random anonymous username every session |
| 🏠 **Chat Rooms** | Instantly create or join any room |
| 🔐 **Encryption** | Optional XOR + Base64 message encryption |
| ✉️ **Private DMs** | Direct message any user with `/dm` |
| 🏷️ **Nick Change** | Change your name mid-session with `/nick` |
| 🚫 **Ignore List** | Block users with `/ignore` |
| 📊 **Session Stats** | Track messages, uptime, encryption status |
| ⚡ **Real-time** | Instant messaging via WebSockets |
| 🌈 **Colored UI** | Beautiful magenta/cyan terminal interface |
| 🚦 **Rate Limiting** | Built-in flood protection |
| 📱 **Termux Native** | One-line install, runs on Android |
| 🛠️ **Self-hostable** | Run your own private server anywhere |

---

## 📱 Quick Install (Termux)

```bash
pkg install git python -y
git clone https://github.com/oyBashar/WhisperNet
cd WhisperNet
bash install.sh
```

Then just type:
```bash
whispernet
```

---

## 🖥️ Usage

### Setup Wizard
```bash
python3 client/whispernet.py
```

### CLI Flags
```
python3 client/whispernet.py [OPTIONS]

  -s, --server   <url>   WebSocket server (e.g. ws://localhost:8765)
  -r, --room     <n>  Room to join
  -u, --username <n>  Your nickname
  -k, --key      <key>   Encryption key
  -h, --help             Show help
```

---

## 💬 All Commands

### Chat
| Command | Description |
|---|---|
| `/help` | Show full command list |
| `/quit` | Exit WhisperNet |
| `/clear` | Clear the terminal screen |
| `/me <action>` | Send an action/emote message |

### Rooms
| Command | Description |
|---|---|
| `/room <n>` | Switch to a different room |
| `/rooms` | List all active rooms on server |
| `/leave` | Leave current room → go to lobby |

### Users
| Command | Description |
|---|---|
| `/users` | List users in current room |
| `/nick <n>` | Change your nickname |
| `/dm <user> <msg>` | Send a private message |
| `/ignore <user>` | Ignore messages from a user |
| `/unignore <user>` | Stop ignoring a user |
| `/ignored` | Show your ignore list |

### Info
| Command | Description |
|---|---|
| `/whoami` | Your username, room, server, encryption |
| `/whois <user>` | Which room a user is in |
| `/ping` | Check if server is alive |
| `/stats` | Session time, message count, settings |

### Encryption
| Command | Description |
|---|---|
| `/encrypt <key>` | Enable encryption with a key |
| `/decrypt` | Disable encryption |

---

## 🌐 Running Your Own Server

```bash
# Any Linux / VPS
pip install websockets
python3 server/server.py --host 0.0.0.0 --port 8765

# Or in Termux
python3 server/server.py
```

> Expose your Termux server publicly with [ngrok](https://ngrok.com) or [Cloudflare Tunnel](https://developers.cloudflare.com/cloudflare-one/connections/connect-networks/).

---

## 📁 Project Structure

```
WhisperNet/
├── client/
│   └── whispernet.py     ← Terminal chat client
├── server/
│   └── server.py         ← WebSocket server
├── install.sh            ← Termux one-click installer
├── requirements.txt
└── README.md
```

---

## 🔐 Encryption Notes

WhisperNet uses **XOR + Base64** encryption. Both users must share the same key. Enable live with `/encrypt <key>`, disable with `/decrypt`.

---

## 👤 Author

**[@oyBashar](https://github.com/oyBashar)**
> *Made with ❤️ for Termux users who value privacy.*

---

## 📄 License

MIT License — free to use, modify, and distribute.
