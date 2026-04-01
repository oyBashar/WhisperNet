#!/data/data/com.termux/files/usr/bin/bash
# ============================================================
#   WhisperNet — Termux Installer
#   Author : @oyBashar (github.com/oyBashar/WhisperNet)
# ============================================================

R='\033[0;31m'; G='\033[0;32m'; C='\033[0;36m'
Y='\033[1;33m'; M='\033[0;35m'; W='\033[1;37m'; N='\033[0m'

step()  { echo -e "\n  ${M}[STEP $1]${N} ${W}$2${N}"; }
info()  { echo -e "  ${C}[*]${N} $1"; }
ok()    { echo -e "  ${G}[+]${N} $1"; }
warn()  { echo -e "  ${Y}[!]${N} $1"; }
fail()  { echo -e "  ${R}[✗]${N} $1"; exit 1; }

clear
echo -e "${M}"
cat << "EOF"
 __        ___     _                      _   _      _
 \ \      / / |__ (_)___ _ __   ___ _ __| \ | | ___| |_
  \ \ /\ / /| '_ \| / __| '_ \ / _ \ '__|  \| |/ _ \ __|
   \ V  V / | | | | \__ \ |_) |  __/ |  | |\  |  __/ |_
    \_/\_/  |_| |_|_|___/ .__/ \___|_|  |_| \_|\___|\__|
                         |_|
EOF
echo -e "${N}"
echo -e "  ${Y}Anonymous Chat Tool for Termux${N}"
echo -e "  ${C}by @oyBashar — github.com/oyBashar/WhisperNet${N}"
echo -e "  ${M}────────────────────────────────────────────────${N}"

# ── Step 1: Storage permission ───────────────────────────────
step 1 "Setting up storage access..."
if [ -d "/data/data/com.termux" ]; then
    termux-setup-storage 2>/dev/null
    sleep 1
    ok "Storage access ready"
else
    warn "Not running in Termux — skipping storage setup"
fi

# ── Step 2: Update packages ──────────────────────────────────
step 2 "Updating package list..."
pkg update -y -q 2>/dev/null
ok "Packages updated"

# ── Step 3: Install Python ───────────────────────────────────
step 3 "Installing Python..."
pkg install python -y -q 2>/dev/null || fail "Could not install Python"
ok "Python installed → $(python3 --version)"

# ── Step 4: Install pip packages ────────────────────────────
step 4 "Installing required packages..."
pip install websockets colorama --quiet || fail "pip install failed"
ok "websockets + colorama installed"

# ── Step 5: Set permissions ──────────────────────────────────
step 5 "Setting file permissions..."
chmod +x "$(pwd)/client/whispernet.py"
chmod +x "$(pwd)/server/server.py"
ok "Permissions set"

# ── Step 6: Create shortcut ──────────────────────────────────
step 6 "Creating whispernet shortcut..."
SHORTCUT="/data/data/com.termux/files/usr/bin/whispernet"
if [ -d "/data/data/com.termux" ]; then
    echo "#!/data/data/com.termux/files/usr/bin/bash" > "$SHORTCUT"
    echo "python3 $(pwd)/client/whispernet.py \"\$@\""  >> "$SHORTCUT"
    chmod +x "$SHORTCUT"
    ok "Shortcut created — you can now type: ${C}whispernet${N}"
else
    warn "Shortcut skipped (not in Termux)"
    info "Run manually: python3 client/whispernet.py"
fi

# ── Done ─────────────────────────────────────────────────────
echo ""
echo -e "  ${M}────────────────────────────────────────────────${N}"
echo -e "  ${G}Installation complete! 🎉${N}"
echo ""
echo -e "  ${Y}Start WhisperNet:${N}"
echo -e "    ${W}whispernet${N}"
echo ""
echo -e "  ${Y}Or with options:${N}"
echo -e "    ${W}whispernet -r myroom -k secretkey${N}"
echo ""
echo -e "  ${Y}Need help?${N}"
echo -e "    ${W}whispernet --help${N}"
echo -e "  ${M}────────────────────────────────────────────────${N}"
echo ""
