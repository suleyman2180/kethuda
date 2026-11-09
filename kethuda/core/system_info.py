"""
KETHUDA Gerçek Zamanlı Sistem Bilgi Toplayıcısı
Ubuntu Linux çekirdek ve donanım verilerini doğrudan okur.
"""

import os
import getpass
import platform
import psutil
from typing import Dict, Any, Optional


def os_dagitim_bilgisi() -> Dict[str, str]:
    """Linux dağıtım bilgilerini /etc/os-release dosyasından okur."""
    bilgi = {
        "ad": "Linux",
        "surum": platform.release(),
        "kod_ad": "",
        "id": "linux",
    }
    os_release = "/etc/os-release"
    if os.path.isfile(os_release):
        try:
            with open(os_release, "r", encoding="utf-8") as f:
                for line in f:
                    if "=" in line:
                        k, v = line.strip().split("=", 1)
                        v = v.strip('"\'')
                        if k == "NAME":
                            bilgi["ad"] = v
                        elif k == "VERSION":
                            bilgi["surum"] = v
                        elif k == "VERSION_CODENAME":
                            bilgi["kod_ad"] = v
                        elif k == "ID":
                            bilgi["id"] = v
        except Exception:
            pass
    return bilgi


def cpu_modeli() -> str:
    """CPU model adını /proc/cpuinfo üzerinden öğrenir."""
    model = "Bilinmeyen CPU"
    cpuinfo = "/proc/cpuinfo"
    if os.path.isfile(cpuinfo):
        try:
            with open(cpuinfo, "r", encoding="utf-8") as f:
                for line in f:
                    if "model name" in line:
                        model = line.split(":", 1)[1].strip()
                        break
        except Exception:
            pass
    if model == "Bilinmeyen CPU":
        model = platform.processor() or "Standart x86/ARM İşlemci"
    return model


def sistem_calisma_suresi() -> float:
    """Sistemin açık kaldığı süreyi saniye cinsinden döndürür."""
    uptime_dosyasi = "/proc/uptime"
    if os.path.isfile(uptime_dosyasi):
        try:
            with open(uptime_dosyasi, "r") as f:
                return float(f.readline().split()[0])
        except Exception:
            pass
    try:
        import time
        return time.time() - psutil.boot_time()
    except Exception:
        return 0.0


def cpu_durumu() -> Dict[str, Any]:
    """CPU kullanımı ve çekirdek bilgilerini döndürür."""
    yuzde_toplam = psutil.cpu_percent(interval=0.1)
    cekirdekler = psutil.cpu_percent(interval=None, percpu=True)
    return {
        "model": cpu_modeli(),
        "fiziksel_cekirdek": psutil.cpu_count(logical=False) or 1,
        "mantiksal_cekirdek": psutil.cpu_count(logical=True) or 1,
        "toplam_yuzde": yuzde_toplam,
        "cekirdek_yuzdeleri": cekirdekler,
    }


def bellek_durumu() -> Dict[str, Any]:
    """RAM ve Takas (Swap) alanı kullanım bilgilerini döndürür."""
    vm = psutil.virtual_memory()
    sm = psutil.swap_memory()
    return {
        "toplam": vm.total,
        "kullanilan": vm.used,
        "bos": vm.free,
        "kullanilabilir": vm.available,
        "yuzde": vm.percent,
        "swap_toplam": sm.total,
        "swap_kullanilan": sm.used,
        "swap_bos": sm.free,
        "swap_yuzde": sm.percent,
    }


def kok_disk_durumu() -> Dict[str, Any]:
    """Kök (/) dizinine ait disk kullanımını döndürür."""
    try:
        du = psutil.disk_usage("/")
        return {
            "toplam": du.total,
            "kullanilan": du.used,
            "bos": du.free,
            "yuzde": du.percent,
            "baglanti_noktasi": "/",
        }
    except Exception:
        return {
            "toplam": 0,
            "kullanilan": 0,
            "bos": 0,
            "yuzde": 0.0,
            "baglanti_noktasi": "/",
        }


def genel_sistem_ozeti() -> Dict[str, Any]:
    """Sistem özet verilerini tek bir sözlükte toplar."""
    os_bilgi = os_dagitim_bilgisi()
    try:
        yuk = os.getloadavg()
    except (AttributeError, OSError):
        yuk = (0.0, 0.0, 0.0)

    return {
        "bilgisayar_adi": platform.node(),
        "kullanici": getpass.getuser(),
        "dagitim": f"{os_bilgi['ad']} {os_bilgi['surum']}".strip(),
        "kernel": platform.release(),
        "mimari": platform.machine(),
        "uptime_saniye": sistem_calisma_suresi(),
        "cpu": cpu_durumu(),
        "bellek": bellek_durumu(),
        "disk": kok_disk_durumu(),
        "yuk_ortalama": yuk,
    }
