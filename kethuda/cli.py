"""
KETHUDA CLI ve Etkileşimli Terminal Kabuğu
Doğrudan komut satırı çağrılarını ve etkileşimli REPL kabuğunu yönetir.
"""

import sys
import shlex
from typing import List, Optional

# Readline desteği (otomatik tamamlama ve geçmiş için)
try:
    import readline
except ImportError:
    readline = None

from kethuda.version import __version__, __app_name__
from kethuda.config import get_config
from kethuda.interface.banner import logo_metni, kucuk_baslik
from kethuda.interface.dashboard import sistem_ozet_paneli, hizli_komut_listesi
from kethuda.interface.colors import (
    renkleri_etkinlestir,
    c_bold,
    c_bright_cyan,
    c_cyan,
    c_green,
    c_dim,
    c_white,
)
from kethuda.core.command_router import CommandRouter, turkce_normalize

KOMUT_LISTESI = [
    "durum",
    "disk",
    "temizlik",
    "islem",
    "servis",
    "paket",
    "kontrol",
    "doktor",
    "gecmis",
    "ayar",
    "guncelle",
    "yardim",
    "surum",
    "cikis",
    "exit",
    "quit",
]


def _tamamlayici(metin: str, state: int) -> Optional[str]:
    """Readline için komut otomatik tamamlama."""
    eslesenler = [k for k in KOMUT_LISTESI if k.startswith(metin.lower())]
    if state < len(eslesenler):
        return eslesenler[state]
    return None


class InteractiveShell:
    """KETHUDA Etkileşimli Terminal Kabuğu (kethuda > )."""

    def __init__(self):
        self.cfg = get_config()
        renk_etkin = self.cfg.getir("renkler", True)
        renkleri_etkinlestir(renk_etkin)

    def baslat(self) -> None:
        """Açılış ekranını gösterir ve etkileşimli döngüyü başlatır."""
        # ASCII Logo
        print(logo_metni())

        # Sistem Özet Kartı
        sistem_ozet_paneli()

        # Temel Komutlar
        hizli_komut_listesi()

        # Readline yapılandırması
        if readline:
            readline.set_completer(_tamamlayici)
            readline.parse_and_bind("tab: complete")

        prompt = f"{c_bold(c_bright_cyan('kethuda'))} {c_bold(c_cyan('>'))} "

        while True:
            try:
                girdi = input(prompt).strip()
                if not girdi:
                    continue

                # Çıkış komutları
                norm_girdi = turkce_normalize(girdi)
                if norm_girdi in ("cikis", "exit", "quit", "q"):
                    print(f"\n{c_dim('KETHUDA oturumu kapatıldı. İyi çalışmalar!')}")
                    break

                # Komut argümanlarını ayrıştır
                try:
                    args = shlex.split(girdi)
                except ValueError:
                    args = girdi.split()

                if args:
                    CommandRouter.calistir(args)
                    print()  # Görsel boşluk

            except KeyboardInterrupt:
                print(f"\n{c_dim('(Çıkmak için: cikis veya Ctrl+D)')}")
            except EOFError:
                print(f"\n{c_dim('KETHUDA kapatılıyor...')}")
                break


def cli_calistir(argv: Optional[List[str]] = None) -> int:
    """KETHUDA ana CLI giriş noktası."""
    if argv is None:
        argv = sys.argv[1:]

    # Renk ayarını konfigürasyondan al
    cfg = get_config()
    renkleri_etkinlestir(cfg.getir("renkler", True))

    if not argv:
        # Argümansız başlatıldığında etkileşimli kabuğu aç
        shell = InteractiveShell()
        shell.baslat()
        return 0

    # Doğrudan argümanlarla tekil komut çalıştırma
    return CommandRouter.calistir(argv)
