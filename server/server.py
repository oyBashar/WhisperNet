#!/usr/bin/env python3
# ============================================================
#   WhisperNet Server — WebSocket Chat Server
#   Author  : @oyBashar (github.com/oyBashar)
#   GitHub  : github.com/oyBashar/WhisperNet
#   License : MIT
#   Run     : python3 server.py [--host 0.0.0.0] [--port 8765]
# ============================================================

import asyncio
import websockets
import json
import sys
import logging
from datetime import datetime
from collections import defaultdict

DEFAULT_HOST   = "0.0.0.0"
DEFAULT_PORT   = 8765
MAX_ROOMS      = 100
MAX_USERS_ROOM = 50
RATE_LIMIT     = 20   # messages per 10 sec

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)
log = logging.getLogger("WhisperNet")

# rooms[room][username] = websocket
rooms: dict[str, dict[str, object]] = defaultdict(dict)
rate_tracker: dict[object, list]    = defaultdict(list)

# ─── HELPERS ─────────────────────────────────────────────────
async def broadcast(room: str, message: dict, exclude=None):
    payload = json.dumps(message)
    dead    = []
    for uname, ws in list(rooms[room].items()):
        if ws is exclude:
            continue
        try:
            await ws.send(payload)
        except Exception:
            dead.append(uname)
    for u in dead:
        rooms[room].pop(u, None)

async def sys_msg(ws, text: str):
    await ws.send(json.dumps({"type": "system", "text": text}))

def is_rate_limited(ws) -> bool:
    now  = asyncio.get_event_loop().time()
    hist = rate_tracker[ws]
    hist[:] = [t for t in hist if now - t < 10]
    if len(hist) >= RATE_LIMIT:
        return True
    hist.append(now)
    return False

def find_user(ws):
    for room, users in rooms.items():
        for uname, sock in users.items():
            if sock is ws:
                return room, uname
    return None, None

def find_ws_by_name(username):
    for room, users in rooms.items():
        if username in users:
            return users[username], room
    return None, None

async def leave_room(ws):
    room, username = find_user(ws)
    if room and username:
        rooms[room].pop(username, None)
        await broadcast(room, {"type": "system", "text": f"{username} has left the room."})
        log.info(f"[{room}] {username} left")
        if not rooms[room]:
            del rooms[room]

# ─── HANDLER ─────────────────────────────────────────────────
async def handler(ws):
    log.info(f"Connection from {ws.remote_address}")
    try:
        async for raw in ws:
            try:
                data = json.loads(raw)
            except json.JSONDecodeError:
                await sys_msg(ws, "Bad message format.")
                continue

            mtype = data.get("type", "")

            # ── JOIN ──────────────────────────────────────
            if mtype == "join":
                room     = str(data.get("room", "general")).lower()[:32].strip()
                username = str(data.get("username", "Anon"))[:24].strip()
                if not room or not username:
                    await sys_msg(ws, "Invalid room or username."); continue
                if len(rooms) >= MAX_ROOMS and room not in rooms:
                    await sys_msg(ws, "Server room limit reached."); continue
                if len(rooms[room]) >= MAX_USERS_ROOM:
                    await sys_msg(ws, f"#{room} is full."); continue
                if username in rooms[room] and rooms[room][username] is not ws:
                    username += f"_{len(rooms[room])}"

                await leave_room(ws)
                rooms[room][username] = ws
                log.info(f"[{room}] {username} joined")

                await sys_msg(ws, f"Welcome to #{room}! You are {username}.")
                await broadcast(room, {"type": "system", "text": f"{username} joined."}, exclude=ws)
                await ws.send(json.dumps({"type": "userlist", "users": list(rooms[room].keys())}))

            # ── MESSAGE ───────────────────────────────────
            elif mtype == "message":
                room, username = find_user(ws)
                if not room:
                    await sys_msg(ws, "Join a room first."); continue
                if is_rate_limited(ws):
                    await sys_msg(ws, "Rate limit hit. Slow down."); continue
                text = str(data.get("text", ""))[:1000]
                if not text: continue
                await broadcast(room, {
                    "type": "message", "username": username, "text": text,
                    "time": datetime.utcnow().strftime("%H:%M")
                }, exclude=ws)

            # ── DM ────────────────────────────────────────
            elif mtype == "dm":
                to       = data.get("to", "")
                sender   = data.get("from", "")
                text     = str(data.get("text", ""))[:500]
                target_ws, _ = find_ws_by_name(to)
                if target_ws:
                    await target_ws.send(json.dumps({"type": "dm", "from": sender, "text": text}))
                else:
                    await sys_msg(ws, f"User '{to}' not found.")

            # ── NICK ──────────────────────────────────────
            elif mtype == "nick":
                room, old = find_user(ws)
                new_nick  = str(data.get("new", ""))[:24].strip()
                if not room or not new_nick: continue
                if new_nick in rooms[room]:
                    await sys_msg(ws, f"'{new_nick}' is already taken."); continue
                rooms[room][new_nick] = rooms[room].pop(old)
                await broadcast(room, {"type": "system", "text": f"{old} is now known as {new_nick}."})
                log.info(f"[{room}] {old} → {new_nick}")

            # ── GET USERS ─────────────────────────────────
            elif mtype == "get_users":
                room, _ = find_user(ws)
                if room:
                    await ws.send(json.dumps({"type": "userlist", "users": list(rooms[room].keys())}))

            # ── GET ROOMS ─────────────────────────────────
            elif mtype == "get_rooms":
                await ws.send(json.dumps({"type": "roomlist", "rooms": list(rooms.keys())}))

            # ── WHOIS ─────────────────────────────────────
            elif mtype == "whois":
                target = data.get("target", "")
                _, room_of = find_ws_by_name(target)
                if room_of:
                    await ws.send(json.dumps({"type": "whois", "username": target, "room": room_of}))
                else:
                    await sys_msg(ws, f"User '{target}' not found.")

            # ── PING ──────────────────────────────────────
            elif mtype == "ping":
                await ws.send(json.dumps({"type": "pong"}))

    except websockets.exceptions.ConnectionClosed:
        pass
    except Exception as e:
        log.error(f"Error: {e}")
    finally:
        await leave_room(ws)
        rate_tracker.pop(ws, None)

# ─── MAIN ────────────────────────────────────────────────────
async def main():
    args = sys.argv[1:]
    host, port = DEFAULT_HOST, DEFAULT_PORT
    i = 0
    while i < len(args):
        if args[i] == "--host" and i+1 < len(args): host = args[i+1]; i += 2
        elif args[i] == "--port" and i+1 < len(args): port = int(args[i+1]); i += 2
        else: i += 1

    log.info(f"WhisperNet server on ws://{host}:{port}")
    log.info("Author: @oyBashar | github.com/oyBashar/WhisperNet")
    async with websockets.serve(handler, host, port):
        await asyncio.Future()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        log.info("Server stopped.")
