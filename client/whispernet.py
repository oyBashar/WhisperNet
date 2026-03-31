#!/usr/bin/env python3
# ============================================================
#   WhisperNet - Anonymous Chat Tool for Termux
#   Author  : @oyBashar (github.com/oyBashar)
#   GitHub  : github.com/oyBashar/WhisperNet
#   License : MIT
#   Version : 1.0.0
# ============================================================

import asyncio
import websockets
import json
import random
import sys
import os
import base64
import threading
from datetime import datetime

try:
    from colorama import Fore, Back, Style, init
    init(autoreset=True)
except ImportError:
    print("[!] Missing dependency: pip install colorama")
    sys.exit(1)

# ─── CONFIG ─────────────────────────────────────────────────
DEFAULT_SERVER = "ws://your-server-ip:8765"
VERSION        = "1.0.0"
AUTHOR         = "@oyBashar"
GITHUB         = "github.com/oyBashar/WhisperNet"
MAX_MSG_LEN    = 500

# ─── ANON NAME GENERATOR ────────────────────────────────────
ADJECTIVES = [
    "Silent","Ghost","Shadow","Hidden","Masked","Phantom",
    "Dark","Stealth","Anonymous","Mystic","Void","Neon",
    "Cyber","Rebel","Rogue","Covert","Cryptic","Lone",
    "Hollow","Blurred","Faded","Null","Binary","Spectral"
]
NOUNS = [
    "Wolf","Fox","Hawk","Viper","Raven","Phantom","Specter",
    "Ninja","Hacker","Cipher","Byte","Daemon","Node","Glitch",
    "Ghost","Cobra","Storm","Pulse","Echo","Zero","Byte",
    "Signal","Wisp","Shade","Wraith","Mirage","Vector"
]

def generate_username():
    adj  = random.choice(ADJECTIVES)
    noun = random.choice(NOUNS)
    num  = random.randint(1000, 9999)
    return f"{adj}{noun}{num}"

# ─── XOR ENCRYPTION ─────────────────────────────────────────
def xor_encrypt(message: str, key: str) -> str:
    key_bytes = (key * (len(message) // len(key) + 1))[:len(message)]
    encrypted = bytes(a ^ b for a, b in zip(message.encode(), key_bytes.encode()))
    return base64.b64encode(encrypted).decode()

def xor_decrypt(encrypted: str, key: str) -> str:
    try:
        data      = base64.b64decode(encrypted.encode())
        key_bytes = (key * (len(data) // len(key) + 1))[:len(data)]
        decrypted = bytes(a ^ b for a, b in zip(data, key_bytes.encode()))
        return decrypted.decode()
    except Exception:
        return "[encrypted — wrong key]"

# ─── BANNER ─────────────────────────────────────────────────
def print_banner():
    os.system("clear")
    print(f"""
{Fore.MAGENTA}╔══════════════════════════════════════════════════╗
{Fore.MAGENTA}║                                                  ║
{Fore.MAGENTA}║  {Fore.CYAN}██╗    ██╗██╗  ██╗██╗███████╗██████╗ ███████╗{Fore.MAGENTA} ║
{Fore.MAGENTA}║  {Fore.CYAN}██║    ██║██║  ██║██║██╔════╝██╔══██╗██╔════╝{Fore.MAGENTA} ║
{Fore.MAGENTA}║  {Fore.CYAN}██║ █╗ ██║███████║██║███████╗██████╔╝█████╗  {Fore.MAGENTA} ║
{Fore.MAGENTA}║  {Fore.CYAN}██║███╗██║██╔══██║██║╚════██║██╔═══╝ ██╔══╝  {Fore.MAGENTA} ║
{Fore.MAGENTA}║  {Fore.CYAN}╚███╔███╔╝██║  ██║██║███████║██║     ███████╗{Fore.MAGENTA} ║
{Fore.MAGENTA}║  {Fore.CYAN} ╚══╝╚══╝ ╚═╝  ╚═╝╚═╝╚══════╝╚═╝     ╚══════╝{Fore.MAGENTA}║
{Fore.MAGENTA}║                                                  ║
{Fore.MAGENTA}║  {Fore.WHITE}███╗  ██╗███████╗████████╗                    {Fore.MAGENTA}║
{Fore.MAGENTA}║  {Fore.WHITE}████╗ ██║██╔════╝╚══██╔══╝                    {Fore.MAGENTA}║
{Fore.MAGENTA}║  {Fore.WHITE}██╔██╗██║█████╗     ██║                       {Fore.MAGENTA}║
{Fore.MAGENTA}║  {Fore.WHITE}██║╚████║██╔══╝     ██║                       {Fore.MAGENTA}║
{Fore.MAGENTA}║  {Fore.WHITE}██║ ╚███║███████╗   ██║                       {Fore.MAGENTA}║
{Fore.MAGENTA}║  {Fore.WHITE}╚═╝  ╚══╝╚══════╝   ╚═╝                       {Fore.MAGENTA}║
{Fore.MAGENTA}║                                                  ║
{Fore.MAGENTA}║  {Fore.YELLOW}  Anonymous Chat Tool  •  v{VERSION}             {Fore.MAGENTA}║
{Fore.MAGENTA}║  {Fore.GREEN}  Author : {AUTHOR:<38}{Fore.MAGENTA}║
{Fore.MAGENTA}║  {Fore.CYAN}  GitHub : {GITHUB:<38}{Fore.MAGENTA}║
{Fore.MAGENTA}╚══════════════════════════════════════════════════╝{Style.RESET_ALL}
""")

# ─── UI HELPERS ─────────────────────────────────────────────
def info(msg):    print(f"{Fore.CYAN}  [*]{Style.RESET_ALL} {msg}")
def success(msg): print(f"{Fore.GREEN}  [+]{Style.RESET_ALL} {msg}")
def error(msg):   print(f"{Fore.RED}  [!]{Style.RESET_ALL} {msg}")
def warn(msg):    print(f"{Fore.YELLOW}  [~]{Style.RESET_ALL} {msg}")

def separator(char="─", width=52):
    print(f"{Fore.MAGENTA}  {'─' * width}{Style.RESET_ALL}")

def fmt_msg(sender, text, ts, is_self=False, is_system=False, is_dm=False):
    t = f"{Fore.LIGHTBLACK_EX}{ts}{Style.RESET_ALL}"
    if is_system:
        return f"\n  {t}  {Fore.YELLOW}◆  {text}{Style.RESET_ALL}"
    if is_self:
        return f"\n  {t}  {Fore.GREEN}▶  You:{Style.RESET_ALL} {text}"
    if is_dm:
        return f"\n  {t}  {Fore.MAGENTA}✉  [DM from {sender}]:{Style.RESET_ALL} {text}"
    return f"\n  {t}  {Fore.CYAN}◀  {sender}:{Style.RESET_ALL} {text}"

def print_help():
    separator()
    print(f"""
{Fore.MAGENTA}  ╔══ WhisperNet Commands ══════════════════════════╗{Style.RESET_ALL}

{Fore.CYAN}  ── Chat ─────────────────────────────────────────{Style.RESET_ALL}
  {Fore.WHITE}/help{Style.RESET_ALL}               Show this command list
  {Fore.WHITE}/quit{Style.RESET_ALL}               Leave WhisperNet
  {Fore.WHITE}/clear{Style.RESET_ALL}              Clear the screen
  {Fore.WHITE}/me <action>{Style.RESET_ALL}        Send an action message
                      {Fore.LIGHTBLACK_EX}e.g. /me waves hello{Style.RESET_ALL}

{Fore.CYAN}  ── Rooms ────────────────────────────────────────{Style.RESET_ALL}
  {Fore.WHITE}/room <name>{Style.RESET_ALL}        Switch to a different room
  {Fore.WHITE}/rooms{Style.RESET_ALL}              List all active rooms
  {Fore.WHITE}/leave{Style.RESET_ALL}              Leave current room (go to lobby)

{Fore.CYAN}  ── Users ────────────────────────────────────────{Style.RESET_ALL}
  {Fore.WHITE}/users{Style.RESET_ALL}              List users in current room
  {Fore.WHITE}/nick <name>{Style.RESET_ALL}        Change your nickname
  {Fore.WHITE}/dm <user> <msg>{Style.RESET_ALL}    Send a private message
  {Fore.WHITE}/ignore <user>{Style.RESET_ALL}      Ignore messages from a user
  {Fore.WHITE}/unignore <user>{Style.RESET_ALL}    Stop ignoring a user
  {Fore.WHITE}/ignored{Style.RESET_ALL}            Show your ignore list

{Fore.CYAN}  ── Info ─────────────────────────────────────────{Style.RESET_ALL}
  {Fore.WHITE}/whoami{Style.RESET_ALL}             Show your current identity
  {Fore.WHITE}/whois <user>{Style.RESET_ALL}       Show info about a user
  {Fore.WHITE}/ping{Style.RESET_ALL}               Check server connection
  {Fore.WHITE}/stats{Style.RESET_ALL}              Show session statistics

{Fore.CYAN}  ── Encryption ───────────────────────────────────{Style.RESET_ALL}
  {Fore.WHITE}/encrypt <key>{Style.RESET_ALL}      Enable encryption with key
  {Fore.WHITE}/decrypt{Style.RESET_ALL}            Disable encryption

{Fore.MAGENTA}  ╚════════════════════════════════════════════════╝{Style.RESET_ALL}
""")

# ─── CHAT SESSION ─────────────────────────────────────────────
class WhisperNet:
    def __init__(self, server_url, room, username, enc_key=None):
        self.server_url  = server_url
        self.room        = room
        self.username    = username
        self.enc_key     = enc_key
        self.ws          = None
        self.running     = True
        self.ignored     = set()
        self.msg_count   = 0
        self.start_time  = datetime.now()

    async def connect(self):
        try:
            async with websockets.connect(self.server_url) as ws:
                self.ws = ws
                await ws.send(json.dumps({
                    "type":     "join",
                    "room":     self.room,
                    "username": self.username
                }))
                success(f"Connected to room {Fore.YELLOW}#{self.room}")
                info(f"Your identity : {Fore.GREEN}{self.username}")
                info(f"Encryption    : " + (f"{Fore.GREEN}ON (key set)" if self.enc_key else f"{Fore.RED}OFF"))
                separator()
                print(f"  {Fore.LIGHTBLACK_EX}Type a message and press Enter  •  /help for commands{Style.RESET_ALL}")
                separator()

                await asyncio.gather(
                    self.receive_loop(),
                    self.send_loop()
                )

        except ConnectionRefusedError:
            error("Cannot connect to server. Is it running?")
        except Exception as e:
            error(f"Connection error: {e}")

    # ── RECEIVE ───────────────────────────────────────────────
    async def receive_loop(self):
        try:
            async for raw in self.ws:
                try:
                    data     = json.loads(raw)
                    mtype    = data.get("type", "message")
                    ts       = datetime.now().strftime("%H:%M")

                    if mtype == "system":
                        print(fmt_msg("", data["text"], ts, is_system=True))

                    elif mtype == "message":
                        sender = data.get("username", "Unknown")
                        if sender in self.ignored:
                            continue
                        text = data.get("text", "")
                        if self.enc_key:
                            text = xor_decrypt(text, self.enc_key)
                        self.msg_count += 1
                        print(fmt_msg(sender, text, ts))

                    elif mtype == "dm":
                        sender = data.get("from", "Unknown")
                        if sender in self.ignored:
                            continue
                        text = data.get("text", "")
                        print(fmt_msg(sender, text, ts, is_dm=True))

                    elif mtype == "userlist":
                        users = data.get("users", [])
                        print(f"\n  {Fore.CYAN}[*]{Style.RESET_ALL} Online in {Fore.YELLOW}#{self.room}{Style.RESET_ALL} ({len(users)}):")
                        for u in users:
                            tag = f" {Fore.GREEN}← you{Style.RESET_ALL}" if u == self.username else ""
                            print(f"      {Fore.CYAN}•{Style.RESET_ALL} {u}{tag}")

                    elif mtype == "roomlist":
                        rms = data.get("rooms", [])
                        print(f"\n  {Fore.CYAN}[*]{Style.RESET_ALL} Active rooms ({len(rms)}):")
                        for r in rms:
                            active = f" {Fore.YELLOW}← you{Style.RESET_ALL}" if r == self.room else ""
                            print(f"      {Fore.MAGENTA}#{Style.RESET_ALL}{r}{active}")

                    elif mtype == "pong":
                        print(fmt_msg("", "Pong! Server is alive.", ts, is_system=True))

                    elif mtype == "whois":
                        u    = data.get("username","?")
                        room = data.get("room","?")
                        print(fmt_msg("", f"{u} is in room #{room}", ts, is_system=True))

                except json.JSONDecodeError:
                    pass
        except websockets.exceptions.ConnectionClosed:
            warn("Disconnected from server.")
            self.running = False

    # ── SEND ──────────────────────────────────────────────────
    async def send_loop(self):
        loop = asyncio.get_event_loop()
        while self.running:
            try:
                raw = await loop.run_in_executor(None, input, "")
                text = raw.strip()
                if not text:
                    continue
                ts = datetime.now().strftime("%H:%M")

                # ── /help ──────────────────────────────────
                if text == "/help":
                    print_help()

                # ── /quit ──────────────────────────────────
                elif text == "/quit":
                    warn("Leaving WhisperNet... Stay anonymous. 👻")
                    self.running = False
                    await self.ws.close()
                    break

                # ── /clear ─────────────────────────────────
                elif text == "/clear":
                    os.system("clear")

                # ── /me <action> ───────────────────────────
                elif text.startswith("/me "):
                    action = text[4:].strip()
                    payload = f"* {self.username} {action}"
                    await self.ws.send(json.dumps({
                        "type":     "message",
                        "room":     self.room,
                        "username": self.username,
                        "text":     payload
                    }))
                    print(fmt_msg("", f"* You {action}", ts, is_system=True))

                # ── /room <name> ───────────────────────────
                elif text.startswith("/room "):
                    new_room = text.split(" ", 1)[1].strip().lstrip("#").lower()
                    if new_room:
                        self.room = new_room
                        await self.ws.send(json.dumps({
                            "type":     "join",
                            "room":     new_room,
                            "username": self.username
                        }))
                        info(f"Switched to room {Fore.YELLOW}#{new_room}")

                # ── /rooms ─────────────────────────────────
                elif text == "/rooms":
                    await self.ws.send(json.dumps({"type": "get_rooms"}))

                # ── /leave ─────────────────────────────────
                elif text == "/leave":
                    self.room = "lobby"
                    await self.ws.send(json.dumps({
                        "type":     "join",
                        "room":     "lobby",
                        "username": self.username
                    }))
                    info(f"Moved to {Fore.YELLOW}#lobby")

                # ── /users ─────────────────────────────────
                elif text == "/users":
                    await self.ws.send(json.dumps({
                        "type": "get_users",
                        "room": self.room
                    }))

                # ── /nick <name> ───────────────────────────
                elif text.startswith("/nick "):
                    new_nick = text.split(" ", 1)[1].strip()[:24]
                    if new_nick:
                        old = self.username
                        self.username = new_nick
                        await self.ws.send(json.dumps({
                            "type":     "nick",
                            "old":      old,
                            "new":      new_nick,
                            "room":     self.room
                        }))
                        info(f"Nickname changed: {Fore.YELLOW}{old}{Style.RESET_ALL} → {Fore.GREEN}{new_nick}")

                # ── /dm <user> <msg> ───────────────────────
                elif text.startswith("/dm "):
                    parts = text.split(" ", 2)
                    if len(parts) >= 3:
                        target, msg = parts[1], parts[2]
                        await self.ws.send(json.dumps({
                            "type":   "dm",
                            "to":     target,
                            "from":   self.username,
                            "text":   msg
                        }))
                        print(fmt_msg("", f"[DM → {target}]: {msg}", ts, is_system=True))
                    else:
                        warn("Usage: /dm <username> <message>")

                # ── /ignore <user> ─────────────────────────
                elif text.startswith("/ignore "):
                    target = text.split(" ", 1)[1].strip()
                    if target:
                        self.ignored.add(target)
                        warn(f"Now ignoring {Fore.YELLOW}{target}")

                # ── /unignore <user> ───────────────────────
                elif text.startswith("/unignore "):
                    target = text.split(" ", 1)[1].strip()
                    self.ignored.discard(target)
                    info(f"No longer ignoring {Fore.YELLOW}{target}")

                # ── /ignored ───────────────────────────────
                elif text == "/ignored":
                    if self.ignored:
                        info("Ignored users: " + ", ".join(
                            f"{Fore.YELLOW}{u}{Style.RESET_ALL}" for u in self.ignored))
                    else:
                        info("Ignore list is empty.")

                # ── /whoami ────────────────────────────────
                elif text == "/whoami":
                    info(f"Username   : {Fore.GREEN}{self.username}")
                    info(f"Room       : {Fore.YELLOW}#{self.room}")
                    info(f"Server     : {Fore.CYAN}{self.server_url}")
                    info(f"Encryption : " + (f"{Fore.GREEN}ON" if self.enc_key else f"{Fore.RED}OFF"))

                # ── /whois <user> ──────────────────────────
                elif text.startswith("/whois "):
                    target = text.split(" ", 1)[1].strip()
                    await self.ws.send(json.dumps({
                        "type":   "whois",
                        "target": target
                    }))

                # ── /ping ──────────────────────────────────
                elif text == "/ping":
                    await self.ws.send(json.dumps({"type": "ping"}))
                    info("Ping sent...")

                # ── /stats ─────────────────────────────────
                elif text == "/stats":
                    elapsed = datetime.now() - self.start_time
                    mins    = int(elapsed.total_seconds() // 60)
                    secs    = int(elapsed.total_seconds() % 60)
                    info(f"Session time  : {mins}m {secs}s")
                    info(f"Messages recv : {self.msg_count}")
                    info(f"Ignored users : {len(self.ignored)}")
                    info(f"Encryption    : " + ("ON" if self.enc_key else "OFF"))

                # ── /encrypt <key> ─────────────────────────
                elif text.startswith("/encrypt "):
                    key = text.split(" ", 1)[1].strip()
                    if key:
                        self.enc_key = key
                        success(f"Encryption enabled with key: {Fore.YELLOW}{key}")

                # ── /decrypt ───────────────────────────────
                elif text == "/decrypt":
                    self.enc_key = None
                    warn("Encryption disabled. Messages sent in plaintext.")

                # ── Unknown command ────────────────────────
                elif text.startswith("/"):
                    warn(f"Unknown command: {text}  •  Type {Fore.WHITE}/help{Style.RESET_ALL} for commands.")

                # ── Regular message ────────────────────────
                else:
                    if len(text) > MAX_MSG_LEN:
                        warn(f"Message too long (max {MAX_MSG_LEN} chars).")
                        continue
                    payload = xor_encrypt(text, self.enc_key) if self.enc_key else text
                    await self.ws.send(json.dumps({
                        "type":     "message",
                        "room":     self.room,
                        "username": self.username,
                        "text":     payload
                    }))
                    print(fmt_msg("", text, ts, is_self=True))

            except (EOFError, KeyboardInterrupt):
                self.running = False
                break

# ─── SETUP WIZARD ────────────────────────────────────────────
def setup_wizard():
    print_banner()
    print(f"  {Fore.MAGENTA}── Setup Wizard ──────────────────────────────────{Style.RESET_ALL}\n")

    server = input(f"  {Fore.WHITE}Server URL  {Fore.LIGHTBLACK_EX}[{DEFAULT_SERVER}]{Style.RESET_ALL}: ").strip()
    if not server:
        server = DEFAULT_SERVER

    room = input(f"  {Fore.WHITE}Room name   {Fore.LIGHTBLACK_EX}[general]{Style.RESET_ALL}: ").strip()
    if not room:
        room = "general"
    room = room.lstrip("#").lower().replace(" ", "-")

    suggested = generate_username()
    username  = input(f"  {Fore.WHITE}Username    {Fore.LIGHTBLACK_EX}[{suggested}]{Style.RESET_ALL}: ").strip()
    if not username:
        username = suggested

    enc = input(f"  {Fore.WHITE}Encrypt key {Fore.LIGHTBLACK_EX}(blank = off){Style.RESET_ALL}: ").strip()
    enc_key = enc if enc else None

    print()
    separator()
    return server, room, username, enc_key

# ─── HELP FLAG ───────────────────────────────────────────────
def print_cli_help():
    print_banner()
    print(f"""  {Fore.CYAN}Usage:{Style.RESET_ALL}
    python3 whispernet.py [OPTIONS]

  {Fore.CYAN}Options:{Style.RESET_ALL}
    -s, --server   <url>   WebSocket server  (e.g. ws://ip:8765)
    -r, --room     <name>  Room to join       (e.g. general)
    -u, --username <name>  Your nickname
    -k, --key      <key>   Encryption key
    -h, --help             Show this help

  {Fore.CYAN}In-chat commands:{Style.RESET_ALL}
    /help                  Full command list
    /quit                  Exit WhisperNet
    /clear                 Clear screen
    /me <action>           Action/emote message
    /room <name>           Switch room
    /rooms                 List all rooms
    /leave                 Go to lobby
    /users                 List users in room
    /nick <name>           Change nickname
    /dm <user> <msg>       Private message
    /ignore <user>         Ignore a user
    /unignore <user>       Unignore a user
    /ignored               Show ignore list
    /whoami                Your session info
    /whois <user>          Info about a user
    /ping                  Ping the server
    /stats                 Session statistics
    /encrypt <key>         Enable encryption
    /decrypt               Disable encryption

  {Fore.CYAN}Example:{Style.RESET_ALL}
    python3 whispernet.py -s ws://localhost:8765 -r shadow -k mykey

  {Fore.CYAN}Author:{Style.RESET_ALL}  {AUTHOR}
  {Fore.CYAN}GitHub:{Style.RESET_ALL}  https://{GITHUB}
""")

# ─── ENTRY ───────────────────────────────────────────────────
def main():
    if "--help" in sys.argv or "-h" in sys.argv:
        print_cli_help()
        sys.exit(0)

    args     = sys.argv[1:]
    server   = None
    room     = None
    username = None
    enc_key  = None

    i = 0
    while i < len(args):
        if   args[i] in ("-s","--server")   and i+1 < len(args): server   = args[i+1]; i += 2
        elif args[i] in ("-r","--room")     and i+1 < len(args): room     = args[i+1]; i += 2
        elif args[i] in ("-u","--username") and i+1 < len(args): username = args[i+1]; i += 2
        elif args[i] in ("-k","--key")      and i+1 < len(args): enc_key  = args[i+1]; i += 2
        else: i += 1

    if not all([server, room, username]):
        server, room, username, enc_key = setup_wizard()

    chat = WhisperNet(server, room, username, enc_key)
    try:
        asyncio.run(chat.connect())
    except KeyboardInterrupt:
        print(f"\n  {Fore.YELLOW}[~]{Style.RESET_ALL} Exiting WhisperNet. Stay anonymous. 👻")

if __name__ == "__main__":
    main()
