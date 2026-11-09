"""
KETHUDA Günlük (Logging) Altyapısı
Tüm sistem işlemlerini ve hatalarını dosya ortamında kayıt altına alır.
"""

import os
import sys
import logging
from logging.handlers import RotatingFileHandler
from typing import Optional
from kethuda.config import get_config

_logger: Optional[logging.Logger] = None


def get_logger() -> logging.Logger:
    """KETHUDA sistem logger nesnesini yapılandırır ve döndürür."""
    global _logger
    if _logger is not None:
        return _logger

    cfg = get_config()
    log_file = cfg.log_path

    # Log dizininin varlığını garanti et
    os.makedirs(os.path.dirname(log_file), exist_ok=True)

    logger = logging.getLogger("kethuda")
    seviye_adi = str(cfg.getir("gunluk_seviyesi", "INFO")).upper()
    seviye = getattr(logging, seviye_adi, logging.INFO)
    logger.setLevel(seviye)

    if not logger.handlers:
        try:
            # 5 MB dosya boyutu, en fazla 3 yedek
            file_handler = RotatingFileHandler(
                log_file,
                maxBytes=5 * 1024 * 1024,
                backupCount=3,
                encoding="utf-8",
            )
            formatter = logging.Formatter(
                "%(asctime)s [%(levelname)s] [%(name)s] %(message)s",
                datefmt="%Y-%m-%d %H:%M:%S",
            )
            file_handler.setFormatter(formatter)
            logger.addHandler(file_handler)
        except Exception:
            # Dosyaya yazılamıyorsa null handler ekle
            logger.addHandler(logging.NullHandler())

    _logger = logger
    return _logger


def log_bilgi(mesaj: str) -> None:
    get_logger().info(mesaj)


def log_uyari(mesaj: str) -> None:
    get_logger().warning(mesaj)


def log_hata(mesaj: str, exc_info: bool = False) -> None:
    get_logger().error(mesaj, exc_info=exc_info)


def log_hata_ayiklama(mesaj: str) -> None:
    get_logger().debug(mesaj)
