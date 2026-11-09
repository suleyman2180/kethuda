"""
KETHUDA Sürüm ve Kimlik Bilgileri
"""

import sys
import platform
from typing import Dict, Any

__app_name__ = "KETHUDA"
__version__ = "1.0.0"
__description__ = "Ubuntu/Linux Modüler Bilgisayar ve Sistem Yönetim Aracı"
__author__ = "KETHUDA Geliştirici Ekibi"
__license__ = "MIT"


def get_version_info() -> Dict[str, Any]:
    """Sistem ve program sürüm bilgilerini döndürür."""
    return {
        "program": __app_name__,
        "surum": __version__,
        "aciklama": __description__,
        "yazar": __author__,
        "lisans": __license__,
        "python": platform.python_version(),
        "isletim_sistemi": platform.system(),
        "kernel": platform.release(),
        "mimari": platform.machine(),
    }
