#!/data/data/com.termux/files/usr/bin/bash
# ============================================================
#   WhisperNet — Termux Installer
#   Author : @oyBashar (github.com/oyBashar)
# ============================================================

RED='\033[0;31m'; GREEN='\033[0;32m'; CYAN='\033[0;36m'
YELLOW='\033[1;33m'; MAGENTA='\033[0;35m'; NC='\033[0m'

info()    { echo -e "  ${CYAN}[*]${NC} $1"; }
success() { echo -e "  ${GREEN}[+]${NC} $1"; }
error()   { echo -e "  ${RED}[!]${NC} $1"; exit 1; }
warn()    { echo -e "  ${YELLOW}[~]${NC} $1"; }

clear
echo -e "${MAGENTA}"
cat << "EOF"
 __        ___     _                      _   _      _
 \ \      / / |__ (_)___ _ __   ___ _ __| \ | | ___| |_
  \ \ /\ / /| '_ \| / __| '_ \ / _ \ '__|  \| |/ _ \ __|
   \ V  V / | | | | \__ \ |_) |  __/ |  | |\  |  __/ |_
    \_/\_/  |_| |_|_|___/ .__/ \___|_|  |_| \_|\___|\__|
                         |_|
EOF
echo -e "${NC}"
echo -e "  ${YELLOW}Anonymous Chat Tool for Termux${NC}"
echo -e "  ${CYAN}Author: @oyBashar | github.com/oyBashar/WhisperNet${NC}"
echo -e "  ${MAGENTA}──────────────────────────────────────────────────${NC}"
echo ""

[ ! -d "/data/data/com.termux" ] && warn "Not in Termux — continuing anyway..."

info "Updating packages..."
pkg update -y -q 2>/dev/null || warn "pkg update failed, continuing..."

info "Installing Python..."
pkg install python -y -q 2>/dev/null || error "Failed to install Python."

info "Installing pip packages..."
pip install websockets colorama --quiet || error "pip install failed."

success "Dependencies installed!"

chmod +x client/whispernet.py 2>/dev/null
chmod +x server/server.py     2>/dev/null

SHORTCUT="/data/data/com.termux/files/usr/bin/whispernet"
if [ -d "/data/data/com.termux" ]; then
    echo "#!/data/data/com.termux/files/usr/bin/bash" > "$SHORTCUT"
    echo "python3 $(pwd)/client/whispernet.py \"\$@\""  >> "$SHORTCUT"
    chmod +x "$SHORTCUT"
    success "Shortcut created → run: ${CYAN}whispernet${NC}"
else
    warn "Run manually: python3 client/whispernet.py"
fi

echo ""
echo -e "  ${MAGENTA}──────────────────────────────────────────────────${NC}"
echo -e "  ${GREEN}Installation complete! 🎉${NC}"
echo ""
echo -e "  ${YELLOW}Start chatting:${NC}"
echo -e "    whispernet"
echo -e "    whispernet -r myroom -k secretkey"
echo -e "    whispernet --help"
echo ""
echo -e "  ${YELLOW}Host your own server:${NC}"
echo -e "    python3 server/server.py --port 8765"
echo -e "  ${MAGENTA}──────────────────────────────────────────────────${NC}"
echo ""
