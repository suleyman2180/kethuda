"""
KETHUDA Terminal Renk ve Biçimlendirme Modülü
ANSI renk kodlarını güvenli bir şekilde yönetir.
"""

import os
import sys
import re

# ANSI Renk Kodları
_RESET = "\033[0m"
_BOLD = "\033[1m"
_DIM = "\033[2m"
_UNDERLINE = "\033[4m"

_RED = "\033[31m"
_GREEN = "\033[32m"
_YELLOW = "\033[33m"
_BLUE = "\033[34m"
_MAGENTA = "\033[35m"
_CYAN = "\033[36m"
_WHITE = "\033[37m"
_GRAY = "\033[90m"

_BRIGHT_RED = "\033[91m"
_BRIGHT_GREEN = "\033[92m"
_BRIGHT_YELLOW = "\033[93m"
_BRIGHT_BLUE = "\033[94m"
_BRIGHT_CYAN = "\033[96m"

# Global renk durumu
_COLORS_ENABLED = True


def renkleri_etkinlestir(etkin: bool = True) -> None:
    """Renk kullanımını global olarak ayarlar."""
    global _COLORS_ENABLED
    _COLORS_ENABLED = bool(etkin)


def renkler_aktif_mi() -> bool:
    """Renklerin o anki ortamda kullanılabilir olup olmadığını kontrol eder."""
    if not _COLORS_ENABLED:
        return False
    # NO_COLOR standart ortam değişkeni kontrolü
    if "NO_COLOR" in os.environ:
        return False
    # TERM 'dumb' kontrolü
    if os.environ.get("TERM") == "dumb":
        return False
    # Çıktı bir terminale bağlı mı?
    if not hasattr(sys.stdout, "isatty") or not sys.stdout.isatty():
        return False
    return True


def _wrap(text: str, code: str) -> str:
    if not renkler_aktif_mi():
        return str(text)
    return f"{code}{text}{_RESET}"


def c_bold(text: str) -> str:
    return _wrap(text, _BOLD)


def c_dim(text: str) -> str:
    return _wrap(text, _DIM)


def c_red(text: str) -> str:
    return _wrap(text, _RED)


def c_bright_red(text: str) -> str:
    return _wrap(text, _BRIGHT_RED)


def c_green(text: str) -> str:
    return _wrap(text, _GREEN)


def c_bright_green(text: str) -> str:
    return _wrap(text, _BRIGHT_GREEN)


def c_yellow(text: str) -> str:
    return _wrap(text, _YELLOW)


def c_bright_yellow(text: str) -> str:
    return _wrap(text, _BRIGHT_YELLOW)


def c_blue(text: str) -> str:
    return _wrap(text, _BLUE)


def c_bright_blue(text: str) -> str:
    return _wrap(text, _BRIGHT_BLUE)


def c_magenta(text: str) -> str:
    return _wrap(text, _MAGENTA)


def c_cyan(text: str) -> str:
    return _wrap(text, _CYAN)


def c_bright_cyan(text: str) -> str:
    return _wrap(text, _BRIGHT_CYAN)


def c_white(text: str) -> str:
    return _wrap(text, _WHITE)


def c_gray(text: str) -> str:
    return _wrap(text, _GRAY)


_ANSI_REGEX = re.compile(r"\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])")


def ansi_temizle(text: str) -> str:
    """Metin içindeki ANSI renk kodlarını temizler (genişlik hesaplamaları için)."""
    return _ANSI_REGEX.sub("", text)
