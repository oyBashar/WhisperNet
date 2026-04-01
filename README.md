# 🕶️ WhisperNet

<p align="center">
  <img src="https://img.shields.io/badge/Platform-Termux-green?style=for-the-badge&logo=android"/>
  <img src="https://img.shields.io/badge/Python-3.8+-blue?style=for-the-badge&logo=python"/>
  <img src="https://img.shields.io/badge/License-MIT-yellow?style=for-the-badge"/>
  <img src="https://img.shields.io/badge/Author-@oyBashar-purple?style=for-the-badge&logo=github"/>
  <img src="https://img.shields.io/badge/Server-Always%20Online-brightgreen?style=for-the-badge"/>
</p>

<p align="center">
  <b>Anonymous real-time chat for Termux — no account, no IP exposed, no tracking.</b><br/>
  Pick a nickname, create a room, start chatting. That's it.
</p>

---

> **Made by [@oyBashar](https://github.com/oyBashar)**

---

## ✨ What is WhisperNet?

WhisperNet is a **command-line anonymous chat tool** that runs inside Termux on Android. You don't need an account. You don't need to know any server IP. The server is always online, protected by Cloudflare, and your identity is just a nickname you choose.

- 🎭 No account needed — just pick a nickname
- 🏠 Create or join any room instantly
- ✉️ Send private messages to anyone
- 🔐 Optional encryption for extra privacy
- 🛡️ Server IP is hidden behind Cloudflare
- ⚡ Real-time — messages appear instantly

---

## 📱 Installation (Step by Step)

### Step 1 — Open Termux
Download Termux from **F-Droid** (recommended) or Play Store and open it.

### Step 2 — Give storage permission
```bash
termux-setup-storage
```
A popup will appear — tap **Allow**.

### Step 3 — Install Git
```bash
pkg install git -y
```

### Step 4 — Clone WhisperNet
```bash
git clone https://github.com/oyBashar/WhisperNet.git
```

### Step 5 — Go into the folder
```bash
cd WhisperNet
```

### Step 6 — Run the installer
```bash
bash install.sh
```
The installer will automatically install Python, all dependencies, and create a shortcut.

### Step 7 — Start chatting
```bash
whispernet
```

That's it! You're connected. 🎉

---

## 🚀 How to Use (Step by Step)

When you run `whispernet` you'll see a simple setup screen:

### Step 1 — Choose a nickname
```
Your nickname [SilentViper8821]:
```
Type any name you want, or press **Enter** to use the random one suggested.

### Step 2 — Choose a room
```
Room to join [general]:
```
Type a room name to join or create it. Press **Enter** for the default `general` room.  
> Tip: Share a secret room name with friends so only you can find each other.

### Step 3 — Encryption (optional)
```
Encrypt key [leave blank to skip]:
```
If you want encrypted messages, type a password. Both you and the person you're chatting with must use the **same key**. Press **Enter** to skip.

### Step 4 — Start chatting
You're in! Just type a message and press **Enter** to send.

```
  21:04  ◀  GhostByte: anyone here?
  21:04  ▶  You: hello world 👻
  21:05  ◆  NullSignal joined the room.
```

---

## 💬 Commands

### 🏠 Rooms
| Command | What it does |
|---|---|
| `/join <room>` | Join or create a room |
| `/rooms` | See all active rooms |
| `/users` | See who's in your room |

**Example:**
```
/join secretroom
/join gaming
```

### ✉️ Messaging
| Command | What it does |
|---|---|
| `/dm <user> <message>` | Send a private message |
| `/me <action>` | Send an action message |

**Example:**
```
/dm GhostByte hey, you there?
/me waves hello
```

### 🏷️ Identity
| Command | What it does |
|---|---|
| `/nick <newname>` | Change your nickname |
| `/whoami` | See your current info |

**Example:**
```
/nick DarkEcho
/whoami
```

### 🔐 Privacy
| Command | What it does |
|---|---|
| `/encrypt <key>` | Turn on message encryption |
| `/decrypt` | Turn off encryption |
| `/ignore <user>` | Mute a user |
| `/unignore <user>` | Unmute a user |

**Example:**
```
/encrypt mysecretkey
/ignore SpammerX
```
> Both you and the other person must use the same key for encrypted messages to work.

### ⚙️ General
| Command | What it does |
|---|---|
| `/ping` | Check if server is alive |
| `/clear` | Clear your screen |
| `/help` | Show command list |
| `/quit` | Exit WhisperNet |

---

## 🔒 Privacy & Security

WhisperNet is designed with privacy in mind:

| Feature | Details |
|---|---|
| **No accounts** | You only need a nickname |
| **No logs** | Messages are not stored anywhere |
| **Hidden server** | Real server IP is hidden behind Cloudflare |
| **DDoS protection** | Cloudflare blocks malicious traffic automatically |
| **Encryption** | Optional end-to-end XOR encryption |
| **No tracking** | No IP logging, no analytics |

### How Cloudflare protects you
The WhisperNet server runs behind a **Cloudflare Tunnel**. This means:
- The real server IP is never exposed
- All traffic passes through Cloudflare's network
- Threats and attacks are blocked automatically before reaching the server
- You connect to a Cloudflare URL, not directly to a server

---

## 🌐 Host Your Own Server

Want to run your own private WhisperNet server? Here's how:

### On Oracle Cloud (Free Forever)

**Step 1 — Get a free Oracle VM**
1. Sign up at [cloud.oracle.com](https://cloud.oracle.com)
2. Create a free VM Instance with Ubuntu 22.04
3. Choose shape `VM.Standard.E2.1.Micro` (Always Free)

**Step 2 — Connect and install**
```bash
ssh ubuntu@YOUR_ORACLE_IP
sudo apt update && sudo apt install python3 python3-pip git -y
pip3 install websockets
git clone https://github.com/oyBashar/WhisperNet.git
cd WhisperNet
```

**Step 3 — Run the server permanently**
```bash
sudo apt install screen -y
screen -S whispernet
python3 server/server.py --host 0.0.0.0 --port 8765
# Press Ctrl+A then D to detach
```

**Step 4 — Set up Cloudflare Tunnel (hides your IP)**
```bash
# Install cloudflared
wget https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-amd64.deb
sudo dpkg -i cloudflared-linux-amd64.deb

# Create a tunnel (no account needed)
cloudflared tunnel --url ws://localhost:8765
```
Cloudflare will give you a public URL like:
```
https://random-words.trycloudflare.com
```
Update `SERVER_URL` in `client/whispernet.py` with this URL (use `wss://` instead of `https://`):
```python
SERVER_URL = "wss://random-words.trycloudflare.com"
```

**Step 5 — Open firewall port**
```bash
sudo iptables -I INPUT -p tcp --dport 8765 -j ACCEPT
sudo apt install iptables-persistent -y
sudo netfilter-persistent save
```

**Step 6 — Auto-start on reboot**
```bash
sudo nano /etc/systemd/system/whispernet.service
```
Paste:
```ini
[Unit]
Description=WhisperNet Server
After=network.target

[Service]
User=ubuntu
WorkingDirectory=/home/ubuntu/WhisperNet
ExecStart=/usr/bin/python3 server/server.py --host 0.0.0.0 --port 8765
Restart=always

[Install]
WantedBy=multi-user.target
```
Then:
```bash
sudo systemctl enable whispernet
sudo systemctl start whispernet
```

---

## 📁 Project Structure

```
WhisperNet/
├── client/
│   └── whispernet.py     ← The chat client (run this)
├── server/
│   └── server.py         ← WebSocket server
├── install.sh            ← Auto-installer for Termux
├── requirements.txt      ← Python dependencies
├── LICENSE
└── README.md
```

---

## 🤝 Contributing

Pull requests are welcome! Ideas:
- AES encryption upgrade
- File sharing
- Tor integration
- Message history

---

## 👤 Author

**[@oyBashar](https://github.com/oyBashar)**
> *Built for Termux users who value anonymity.*

---

## 📄 License

MIT License — free to use, modify, and distribute.
