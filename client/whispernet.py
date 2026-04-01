#!/usr/bin/env python3
# ============================================================
#   WhisperNet — Anonymous Chat Tool for Termux
#   Author  : @oyBashar (github.com/oyBashar)
#   GitHub  : github.com/oyBashar/WhisperNet
#   License : MIT  |  Version : 2.0.0
# ============================================================

import asyncio
import websockets
import json
import random
import sys
import os
import base64
from datetime import datetime

try:
    from colorama import Fore, Style, init
    init(autoreset=True)
except ImportError:
    os.system("pip install colorama -q")
    from colorama import Fore, Style, init
    init(autoreset=True)

# ─── CONFIG (Cloudflare tunnel URL — IP is hidden) ──────────
SERVER_URL = "ws://your-cloudflare-tunnel.trycloudflare.com"
VERSION    = "2.0.0"
AUTHOR     = "@oyBashar"
GITHUB     = "github.com/oyBashar/WhisperNet"

# ─── USERNAME GENERATOR ─────────────────────────────────────
ADJECTIVES = [
    "Silent","Ghost","Shadow","Masked","Phantom","Dark",
    "Stealth","Mystic","Void","Neon","Cyber","Rebel",
    "Cryptic","Lone","Hollow","Null","Spectral","Covert"
]
NOUNS = [
    "Wolf","Fox","Viper","Raven","Specter","Cipher",
    "Daemon","Glitch","Cobra","Pulse","Echo","Zero",
    "Wisp","Shade","Wraith","Mirage","Signal","Byte"
]

def random_name():
    return f"{random.choice(ADJECTIVES)}{random.choice(NOUNS)}{random.randint(1000,9999)}"

# ─── ENCRYPTION ─────────────────────────────────────────────
def encrypt(text, key):
    k = (key * (len(text)//len(key)+1))[:len(text)]
    return base64.b64encode(bytes(a^b for a,b in zip(text.encode(),k.encode()))).decode()

def decrypt(data, key):
    try:
        raw = base64.b64decode(data.encode())
        k   = (key * (len(raw)//len(key)+1))[:len(raw)]
        return bytes(a^b for a,b in zip(raw,k.encode())).decode()
    except:
        return "[wrong encryption key]"

# ─── UI ─────────────────────────────────────────────────────
def banner():
    os.system("clear")
    print(f"""
{Fore.MAGENTA}╔══════════════════════════════════════════════════╗
{Fore.MAGENTA}║  {Fore.CYAN}██╗    ██╗██╗  ██╗██╗███████╗██████╗ ███████╗{Fore.MAGENTA}  ║
{Fore.MAGENTA}║  {Fore.CYAN}██║    ██║██║  ██║██║██╔════╝██╔══██╗██╔════╝{Fore.MAGENTA}  ║
{Fore.MAGENTA}║  {Fore.CYAN}██║ █╗ ██║███████║██║███████╗██████╔╝█████╗  {Fore.MAGENTA}  ║
{Fore.MAGENTA}║  {Fore.CYAN}██║███╗██║██╔══██║██║╚════██║██╔═══╝ ██╔══╝  {Fore.MAGENTA}  ║
{Fore.MAGENTA}║  {Fore.CYAN}╚███╔███╔╝██║  ██║██║███████║██║     ███████╗{Fore.MAGENTA}  ║
{Fore.MAGENTA}║  {Fore.CYAN} ╚══╝╚══╝ ╚═╝  ╚═╝╚═╝╚══════╝╚═╝     ╚══════╝{Fore.MAGENTA} ║
{Fore.MAGENTA}║  {Fore.WHITE}            N  E  T                           {Fore.MAGENTA}  ║
{Fore.MAGENTA}║  {Fore.YELLOW}    Anonymous Chat  •  v{VERSION}  •  Termux     {Fore.MAGENTA}  ║
{Fore.MAGENTA}║  {Fore.LIGHTBLACK_EX}    by {AUTHOR} — {GITHUB}  {Fore.MAGENTA}  ║
{Fore.MAGENTA}╚══════════════════════════════════════════════════╝{Style.RESET_ALL}
""")

def log_info(m):    print(f"  {Fore.CYAN}[*]{Style.RESET_ALL} {m}")
def log_ok(m):      print(f"  {Fore.GREEN}[+]{Style.RESET_ALL} {m}")
def log_warn(m):    print(f"  {Fore.YELLOW}[!]{Style.RESET_ALL} {m}")
def sep():          print(f"  {Fore.MAGENTA}{'─'*48}{Style.RESET_ALL}")

def fmt(sender, text, ts, me=False, sys=False, dm=False):
    t = f"{Fore.LIGHTBLACK_EX}{ts}{Style.RESET_ALL}"
    if sys: return f"\n  {t}  {Fore.YELLOW}◆  {text}{Style.RESET_ALL}"
    if me:  return f"\n  {t}  {Fore.GREEN}▶  You:{Style.RESET_ALL} {text}"
    if dm:  return f"\n  {t}  {Fore.MAGENTA}✉  [DM from {sender}]:{Style.RESET_ALL} {text}"
    return      f"\n  {t}  {Fore.CYAN}◀  {sender}:{Style.RESET_ALL} {text}"

def show_help():
    print(f"""
{Fore.MAGENTA}  ╔══ Commands ══════════════════════════════════════╗{Style.RESET_ALL}

{Fore.CYAN}  ── Rooms ────────────────────────────────────────{Style.RESET_ALL}
  {Fore.WHITE}/join <room>{Style.RESET_ALL}        Join or create a room
  {Fore.WHITE}/rooms{Style.RESET_ALL}              List all active rooms
  {Fore.WHITE}/users{Style.RESET_ALL}              List users in your room

{Fore.CYAN}  ── Messaging ────────────────────────────────────{Style.RESET_ALL}
  {Fore.WHITE}/dm <user> <msg>{Style.RESET_ALL}    Send a private message
  {Fore.WHITE}/me <action>{Style.RESET_ALL}        Send an action message
                      {Fore.LIGHTBLACK_EX}e.g. /me waves hello{Style.RESET_ALL}

{Fore.CYAN}  ── Identity ─────────────────────────────────────{Style.RESET_ALL}
  {Fore.WHITE}/nick <name>{Style.RESET_ALL}        Change your nickname
  {Fore.WHITE}/whoami{Style.RESET_ALL}             Show your current info

{Fore.CYAN}  ── Privacy ──────────────────────────────────────{Style.RESET_ALL}
  {Fore.WHITE}/encrypt <key>{Style.RESET_ALL}      Lock messages with a key
  {Fore.WHITE}/decrypt{Style.RESET_ALL}            Turn off encryption
  {Fore.WHITE}/ignore <user>{Style.RESET_ALL}      Mute a user
  {Fore.WHITE}/unignore <user>{Style.RESET_ALL}    Unmute a user

{Fore.CYAN}  ── General ──────────────────────────────────────{Style.RESET_ALL}
  {Fore.WHITE}/clear{Style.RESET_ALL}              Clear the screen
  {Fore.WHITE}/ping{Style.RESET_ALL}               Check server connection
  {Fore.WHITE}/quit{Style.RESET_ALL}               Exit WhisperNet

{Fore.MAGENTA}  ╚════════════════════════════════════════════════╝{Style.RESET_ALL}
""")

# ─── MAIN CHAT CLASS ─────────────────────────────────────────
class WhisperNet:
    def __init__(self, username, room, enc_key=None):
        self.username = username
        self.room     = room
        self.enc_key  = enc_key
        self.ws       = None
        self.running  = True
        self.ignored  = set()
        self.started  = datetime.now()

    async def run(self):
        try:
            async with websockets.connect(SERVER_URL) as ws:
                self.ws = ws
                await ws.send(json.dumps({
                    "type": "join", "room": self.room, "username": self.username
                }))
                log_ok(f"Connected!  Room: {Fore.YELLOW}#{self.room}")
                log_info(f"Your name : {Fore.GREEN}{self.username}")
                log_info(f"Encryption: " + (f"{Fore.GREEN}ON" if self.enc_key else f"{Fore.RED}OFF"))
                sep()
                print(f"  {Fore.LIGHTBLACK_EX}Type a message and press Enter  •  /help for commands{Style.RESET_ALL}")
                sep()
                await asyncio.gather(self._recv(), self._send())
        except ConnectionRefusedError:
            log_warn("Cannot connect to server.")
        except Exception as e:
            log_warn(f"Error: {e}")

    async def _recv(self):
        try:
            async for raw in self.ws:
                data  = json.loads(raw)
                mtype = data.get("type","")
                ts    = datetime.now().strftime("%H:%M")

                if mtype == "system":
                    print(fmt("","",ts, sys=True))
                    # fix: pass text properly
                    text = data.get("text","")
                    print(fmt("", text, ts, sys=True))

                elif mtype == "message":
                    sender = data.get("username","?")
                    if sender in self.ignored: continue
                    text = data.get("text","")
                    if self.enc_key: text = decrypt(text, self.enc_key)
                    print(fmt(sender, text, ts))

                elif mtype == "dm":
                    sender = data.get("from","?")
                    if sender in self.ignored: continue
                    print(fmt(sender, data.get("text",""), ts, dm=True))

                elif mtype == "userlist":
                    users = data.get("users",[])
                    print(f"\n  {Fore.CYAN}[*]{Style.RESET_ALL} Users in {Fore.YELLOW}#{self.room}{Style.RESET_ALL} ({len(users)}):")
                    for u in users:
                        tag = f" {Fore.GREEN}← you{Style.RESET_ALL}" if u == self.username else ""
                        print(f"      {Fore.MAGENTA}•{Style.RESET_ALL} {u}{tag}")

                elif mtype == "roomlist":
                    rms = data.get("rooms",[])
                    print(f"\n  {Fore.CYAN}[*]{Style.RESET_ALL} Active rooms ({len(rms)}):")
                    for r in rms:
                        tag = f" {Fore.YELLOW}← you{Style.RESET_ALL}" if r == self.room else ""
                        print(f"      {Fore.MAGENTA}#{Style.RESET_ALL}{r}{tag}")

                elif mtype == "pong":
                    print(fmt("","Server is alive ✓", ts, sys=True))

                elif mtype == "whois":
                    u = data.get("username","?")
                    r = data.get("room","?")
                    print(fmt("", f"{u} is in #{r}", ts, sys=True))

        except websockets.exceptions.ConnectionClosed:
            log_warn("Disconnected.")
            self.running = False

    async def _send(self):
        loop = asyncio.get_event_loop()
        while self.running:
            try:
                raw  = await loop.run_in_executor(None, input, "")
                text = raw.strip()
                if not text: continue
                ts = datetime.now().strftime("%H:%M")

                if text == "/help":
                    show_help()

                elif text == "/quit":
                    log_warn("Goodbye. Stay anonymous. 👻")
                    self.running = False
                    await self.ws.close()
                    break

                elif text == "/clear":
                    os.system("clear")

                elif text.startswith("/join "):
                    room = text.split(" ",1)[1].strip().lstrip("#").lower()
                    if room:
                        self.room = room
                        await self.ws.send(json.dumps({
                            "type":"join","room":room,"username":self.username
                        }))
                        log_info(f"Joined {Fore.YELLOW}#{room}")

                elif text == "/rooms":
                    await self.ws.send(json.dumps({"type":"get_rooms"}))

                elif text == "/users":
                    await self.ws.send(json.dumps({"type":"get_users","room":self.room}))

                elif text.startswith("/dm "):
                    parts = text.split(" ",2)
                    if len(parts) == 3:
                        to, msg = parts[1], parts[2]
                        await self.ws.send(json.dumps({
                            "type":"dm","to":to,"from":self.username,"text":msg
                        }))
                        print(fmt("", f"[DM → {to}]: {msg}", ts, sys=True))
                    else:
                        log_warn("Usage: /dm <username> <message>")

                elif text.startswith("/me "):
                    action = text[4:].strip()
                    payload = f"* {self.username} {action}"
                    await self.ws.send(json.dumps({
                        "type":"message","room":self.room,
                        "username":self.username,"text":payload
                    }))
                    print(fmt("", f"* You {action}", ts, sys=True))

                elif text.startswith("/nick "):
                    new = text.split(" ",1)[1].strip()[:24]
                    if new:
                        old = self.username
                        self.username = new
                        await self.ws.send(json.dumps({
                            "type":"nick","old":old,"new":new,"room":self.room
                        }))
                        log_info(f"Nickname: {Fore.YELLOW}{old}{Style.RESET_ALL} → {Fore.GREEN}{new}")

                elif text == "/whoami":
                    log_info(f"Name      : {Fore.GREEN}{self.username}")
                    log_info(f"Room      : {Fore.YELLOW}#{self.room}")
                    log_info(f"Encrypt   : " + (f"{Fore.GREEN}ON" if self.enc_key else f"{Fore.RED}OFF"))
                    elapsed = datetime.now() - self.started
                    m,s = divmod(int(elapsed.total_seconds()),60)
                    log_info(f"Connected : {m}m {s}s")

                elif text.startswith("/encrypt "):
                    key = text.split(" ",1)[1].strip()
                    if key:
                        self.enc_key = key
                        log_ok(f"Encryption ON — key: {Fore.YELLOW}{key}")

                elif text == "/decrypt":
                    self.enc_key = None
                    log_warn("Encryption OFF — messages are plaintext.")

                elif text.startswith("/ignore "):
                    u = text.split(" ",1)[1].strip()
                    self.ignored.add(u)
                    log_warn(f"Ignoring {Fore.YELLOW}{u}")

                elif text.startswith("/unignore "):
                    u = text.split(" ",1)[1].strip()
                    self.ignored.discard(u)
                    log_info(f"No longer ignoring {Fore.YELLOW}{u}")

                elif text == "/ping":
                    await self.ws.send(json.dumps({"type":"ping"}))

                elif text.startswith("/"):
                    log_warn(f"Unknown command. Type {Fore.WHITE}/help{Style.RESET_ALL} to see all commands.")

                else:
                    if len(text) > 500:
                        log_warn("Message too long (max 500 chars).")
                        continue
                    payload = encrypt(text, self.enc_key) if self.enc_key else text
                    await self.ws.send(json.dumps({
                        "type":"message","room":self.room,
                        "username":self.username,"text":payload
                    }))
                    print(fmt("", text, ts, me=True))

            except (EOFError, KeyboardInterrupt):
                self.running = False
                break

# ─── STARTUP WIZARD ──────────────────────────────────────────
def wizard():
    banner()
    sep()
    print(f"  {Fore.CYAN}Welcome to WhisperNet — you are anonymous by default.{Style.RESET_ALL}")
    print(f"  {Fore.LIGHTBLACK_EX}Press Enter to use the suggested value in [brackets].{Style.RESET_ALL}")
    sep()
    print()

    suggested = random_name()
    name = input(f"  {Fore.WHITE}Your nickname {Fore.LIGHTBLACK_EX}[{suggested}]{Style.RESET_ALL}: ").strip()
    if not name: name = suggested

    room = input(f"  {Fore.WHITE}Room to join  {Fore.LIGHTBLACK_EX}[general]{Style.RESET_ALL}: ").strip()
    if not room: room = "general"
    room = room.lstrip("#").lower().replace(" ","-")

    enc = input(f"  {Fore.WHITE}Encrypt key   {Fore.LIGHTBLACK_EX}[leave blank to skip]{Style.RESET_ALL}: ").strip()
    enc_key = enc if enc else None

    print()
    sep()
    return name, room, enc_key

# ─── ENTRY ───────────────────────────────────────────────────
def main():
    if "-h" in sys.argv or "--help" in sys.argv:
        banner()
        print(f"""  {Fore.CYAN}Usage:{Style.RESET_ALL}
    python3 whispernet.py
    python3 whispernet.py -r <room> -u <username> -k <key>

  {Fore.CYAN}Flags:{Style.RESET_ALL}
    -r  Room to join
    -u  Your nickname
    -k  Encryption key
    -h  Show this help

  {Fore.CYAN}Author:{Style.RESET_ALL} {AUTHOR}
  {Fore.CYAN}GitHub:{Style.RESET_ALL} https://{GITHUB}
""")
        return

    args = sys.argv[1:]
    room = username = enc_key = None
    i = 0
    while i < len(args):
        if args[i]=="-r" and i+1<len(args): room=args[i+1]; i+=2
        elif args[i]=="-u" and i+1<len(args): username=args[i+1]; i+=2
        elif args[i]=="-k" and i+1<len(args): enc_key=args[i+1]; i+=2
        else: i+=1

    if not all([room, username]):
        username, room, enc_key = wizard()

    chat = WhisperNet(username, room, enc_key)
    try:
        asyncio.run(chat.run())
    except KeyboardInterrupt:
        print(f"\n  {Fore.YELLOW}[!]{Style.RESET_ALL} Exiting. Stay anonymous. 👻")

if __name__ == "__main__":
    main()
