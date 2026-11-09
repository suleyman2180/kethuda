#!/usr/bin/env bash
# KETHUDA Kurulum Betiği (install.sh)
# Ubuntu Linux için otomatik kontrol ve kurulum

set -e

CYAN='\033[0;36m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BOLD='\033[1m'
NC='\033[0m' # No Color

clear 2>/dev/null || true

# ASCII KETHUDA Logosu
echo -e "${CYAN}"
cat << "EOF"
 ██╗  ██╗███████╗████████╗██╗  ██╗██╗   ██╗██████╗  █████╗ 
 ██║ ██╔╝██╔════╝╚══██╔══╝██║  ██║██║   ██║██╔══██╗██╔══██╗
 █████╔╝ █████╗     ██║   ███████║██║   ██║██║  ██║███████║
 ██╔═██╗ ██╔══╝     ██║   ██╔══██║██║   ██║██║  ██║██╔══██║
 ██║  ██╗███████╗   ██║   ██║  ██║╚██████╔╝██████╔╝██║  ██║
 ╚═╝  ╚═╝╚══════╝   ╚═╝   ╚═╝  ╚═╝ ╚═════╝ ╚═════╝  ╚═╝  ╚═╝
EOF
echo -e "${GREEN}${BOLD}                                                KETHUDA v1.0.0${NC}"
echo -e "${CYAN}----------------------------------------------------------------------${NC}"
echo -e "${BOLD}KETHUDA Kurulum Sihirbazı Başlatılıyor...${NC}\n"

# 1. İşletim Sistemi Kontrolü
echo -ne "[ 1/6 ] İşletim sistemi denetleniyor... "
if [ -f /etc/os-release ]; then
    . /etc/os-release
    OS_NAME=$NAME
    OS_VER=$VERSION_ID
    echo -e "${GREEN}[TAMAM]${NC} ($OS_NAME $OS_VER)"
else
    echo -e "${YELLOW}[UYARI]${NC} (/etc/os-release bulunamadı, Linux kabul ediliyor)"
fi

# 2. Python Sürümü Kontrolü
echo -ne "[ 2/6 ] Python 3 ortamı kontrol ediliyor... "
if command -v python3 >/dev/null 2>&1; then
    PY_VER=$(python3 -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')")
    PY_MAJOR=$(echo "$PY_VER" | cut -d. -f1)
    PY_MINOR=$(echo "$PY_VER" | cut -d. -f2)
    if [ "$PY_MAJOR" -ge 3 ] && [ "$PY_MINOR" -ge 8 ]; then
        echo -e "${GREEN}[TAMAM]${NC} (Python $PY_VER)"
    else
        echo -e "${RED}[HATA]${NC} Python 3.8 veya üzeri gerekli. Mevcut: $PY_VER"
        exit 1
    fi
else
    echo -e "${RED}[HATA]${NC} python3 bulunamadı. Lütfen 'sudo apt install python3' kurun."
    exit 1
fi

# 3. Bağımlılık Kontrolü (psutil)
echo -ne "[ 3/6 ] Bağımlılıklar denetleniyor (psutil)... "
if python3 -c "import psutil" >/dev/null 2>&1; then
    echo -e "${GREEN}[TAMAM]${NC}"
else
    echo -e "${YELLOW}[KURULUYOR]${NC}"
    echo "       psutil kütüphanesi yükleniyor..."
    if command -v pip3 >/dev/null 2>&1; then
        pip3 install --user psutil || python3 -m pip install psutil
    else
        echo -e "${RED}[HATA]${NC} Lütfen 'sudo apt install python3-psutil' komutu ile psutil kurun."
        exit 1
    fi
fi

# 4. KETHUDA Dizin ve Yapılandırma Klasörleri
echo -ne "[ 4/6 ] Kullanıcı yapılandırma dizinleri hazırlanıyor... "
mkdir -p "$HOME/.config/kethuda"
mkdir -p "$HOME/.local/share/kethuda"
mkdir -p "$HOME/.local/state/kethuda"
mkdir -p "$HOME/.local/bin"
echo -e "${GREEN}[TAMAM]${NC}"

# 5. Komut Satırı Bağlantısı ve Çalıştırılabilir Dosya Oluşturma
echo -ne "[ 5/6 ] 'kethuda' komut kısayolu oluşturuluyor... "
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
WRAPPER_SCRIPT="$HOME/.local/bin/kethuda"

cat << EOF > "$WRAPPER_SCRIPT"
#!/usr/bin/env bash
export PYTHONPATH="$SCRIPT_DIR:\$PYTHONPATH"
exec python3 "$SCRIPT_DIR/kethuda/main.py" "\$@"
EOF

chmod +x "$WRAPPER_SCRIPT"
chmod +x "$SCRIPT_DIR/kethuda/main.py"

# Eğer sudo yetkisi varsa /usr/local/bin altına da bağla
if [ -w /usr/local/bin ]; then
    ln -sf "$WRAPPER_SCRIPT" /usr/local/bin/kethuda 2>/dev/null || true
elif sudo -n true 2>/dev/null; then
    sudo ln -sf "$WRAPPER_SCRIPT" /usr/local/bin/kethuda 2>/dev/null || true
fi
echo -e "${GREEN}[TAMAM]${NC}"

# 6. PATH Kontrolü
echo -ne "[ 6/6 ] Ortam değişkeni (PATH) denetleniyor... "
if [[ ":$PATH:" != *":$HOME/.local/bin:"* ]]; then
    # Bashrc içine ekle
    if [ -f "$HOME/.bashrc" ] && ! grep -q 'HOME/.local/bin' "$HOME/.bashrc"; then
        echo 'export PATH="$HOME/.local/bin:$PATH"' >> "$HOME/.bashrc"
    fi
    echo -e "${YELLOW}[UYARI]${NC} (~/.local/bin PATH'e eklendi. Yeni bir terminal açabilir veya 'source ~/.bashrc' yapabilirsiniz)"
else
    echo -e "${GREEN}[TAMAM]${NC}"
fi

# İlk çalıştırma ve doğrulama testi
python3 "$SCRIPT_DIR/kethuda/main.py" surum >/dev/null 2>&1

echo -e "\n${CYAN}======================================================================${NC}"
echo -e "${GREEN}${BOLD}KETHUDA başarıyla kuruldu.${NC}\n"
echo -e "Çalıştırmak için:"
echo -e "  ${BOLD}kethuda${NC}          (Etkileşimli kabuğu başlatır)"
echo -e "  ${BOLD}kethuda durum${NC}    (Sistem durumunu gösterir)"
echo -e "  ${BOLD}kethuda yardim${NC}   (Kullanılabilir komutları listeler)\n"
