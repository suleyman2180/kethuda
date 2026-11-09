#!/usr/bin/env bash
# KETHUDA Kaldırma Betiği (uninstall.sh)
# KETHUDA CLI aracını sistemden güvenle kaldırır.

set -e

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
BOLD='\033[1m'
NC='\033[0m'

echo -e "${CYAN}======================================================================${NC}"
echo -e "${BOLD}KETHUDA Kaldırma Sihirbazı${NC}"
echo -e "${CYAN}======================================================================${NC}\n"

# 1. Komut kısayollarını kaldır
echo -ne "Komut dosyaları kaldırılıyor... "
rm -f "$HOME/.local/bin/kethuda"

if [ -w /usr/local/bin/kethuda ]; then
    rm -f /usr/local/bin/kethuda 2>/dev/null || true
elif sudo -n true 2>/dev/null; then
    sudo rm -f /usr/local/bin/kethuda 2>/dev/null || true
fi
echo -e "${GREEN}[TAMAM]${NC}"

# 2. Kullanıcı verileri koruma uyarısı ve seçeneği
echo -e "\n${YELLOW}Kullanıcı verileri (yapılandırma, geçmiş veritabanı ve loglar) varsayılan olarak korunmuştur:${NC}"
echo "  - Yapılandırma : $HOME/.config/kethuda"
echo "  - Veritabanı   : $HOME/.local/share/kethuda"
echo "  - Günlükler    : $HOME/.local/state/kethuda"

echo -e ""
read -p "Tüm KETHUDA kullanıcı verilerini de kalıcı olarak silmek istiyor musunuz? [e/H]: " SIL_VERI

if [[ "$SIL_VERI" =~ ^[eE]$ ]]; then
    rm -rf "$HOME/.config/kethuda"
    rm -rf "$HOME/.local/share/kethuda"
    rm -rf "$HOME/.local/state/kethuda"
    echo -e "${GREEN}[TAMAM]${NC} Kullanıcı verileri ve ayarları tamamen temizlendi."
else
    echo -e "${GREEN}[KORUNDU]${NC} Kullanıcı verileriniz saklandı."
fi

echo -e "\n${GREEN}${BOLD}KETHUDA başarıyla sistemden kaldırıldı.${NC}\n"
