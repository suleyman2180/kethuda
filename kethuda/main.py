#!/usr/bin/env python3
"""
KETHUDA - Ubuntu Linux Bilgisayar ve Sistem Yönetim Aracı
Ana Giriş Dosyası
"""

import sys
import os

# Eğer üst dizin sys.path'te değilse ekle
proje_kok = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if proje_kok not in sys.path:
    sys.path.insert(0, proje_kok)

from kethuda.cli import cli_calistir


def main() -> None:
    try:
        kod = cli_calistir()
        sys.exit(kod or 0)
    except KeyboardInterrupt:
        print("\nİşlem iptal edildi.")
        sys.exit(130)
    except Exception as e:
        print(f"\nBeklenmeyen bir hata oluştu: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
