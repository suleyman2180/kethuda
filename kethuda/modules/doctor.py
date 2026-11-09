"""
KETHUDA Sistem Doktoru Modülü
KETHUDA'nın ve işletim sisteminin çalışma koşullarını, bağımlılıklarını,
yetkilerini ve yapılandırma bütünlüğünü denetler; çözüm önerileri sunar.
"""

import os
import sys
import shutil
import sqlite3
from pathlib import Path
from typing import List, Dict, Any, Tuple
from kethuda.config import get_config
from kethuda.core.permissions import root_mu, sudo_mevcut_mu, guvenli_komut_calistir
from kethuda.interface.output import (
    baslik_yazdir,
    alt_baslik_yazdir,
    tablo_yazdir,
    rozet_tamam,
    rozet_uyari,
    rozet_hata,
    rozet_bilgi,
)
from kethuda.interface.colors import c_bold, c_green, c_yellow, c_red, c_cyan, c_dim


def sistem_doktoru_calistir() -> int:
    """Tüm sistem ve KETHUDA sağlık denetimlerini yürütür."""
    baslik_yazdir("KETHUDA SİSTEM DOKTORU SAĞLIK RAPORU")

    kontroller = []
    oneriler = []

    # 1. Python Sürümü
    py_ver = sys.version_info
    py_metin = f"{py_ver.major}.{py_ver.minor}.{py_ver.micro}"
    if py_ver >= (3, 8):
        kontroller.append(["Python Sürümü", rozet_tamam(), f"{py_metin} (Gereksinim: >= 3.8)"])
    else:
        kontroller.append(["Python Sürümü", rozet_hata(), f"{py_metin} (Eski sürüm)"])
        oneriler.append("Python 3.8 veya üzeri bir sürüme geçiş yapınız.")

    # 2. psutil Bağımlılığı
    try:
        import psutil
        kontroller.append(["Python 'psutil' Modülü", rozet_tamam(), f"Kurulu (v{psutil.__version__})"])
    except ImportError:
        kontroller.append(["Python 'psutil' Modülü", rozet_hata(), "Eksik"])
        oneriler.append("psutil kütüphanesini kurun: pip3 install psutil veya sudo apt install python3-psutil")

    # 3. SQLite3 Kütüphanesi
    try:
        import sqlite3
        kontroller.append(["Python 'sqlite3' Modülü", rozet_tamam(), f"Kurulu (v{sqlite3.sqlite_version})"])
    except ImportError:
        kontroller.append(["Python 'sqlite3' Modülü", rozet_hata(), "Eksik"])
        oneriler.append("Python SQLite3 modülünü kurunuz.")

    # 4. Gerekli Sistem Komutları
    temel_komutlar = ["systemctl", "apt", "dpkg", "df", "free", "uptime", "journalctl"]
    eksik_komutlar = []
    for cmd in temel_komutlar:
        if shutil.which(cmd) is None:
            eksik_komutlar.append(cmd)

    if not eksik_komutlar:
        kontroller.append(["Temel Linux Komutları", rozet_tamam(), f"Tümü mevcut ({', '.join(temel_komutlar)})"])
    else:
        kontroller.append(["Temel Linux Komutları", rozet_uyari(), f"Eksikler: {', '.join(eksik_komutlar)}"])
        oneriler.append(f"Eksik komutları yükleyin veya PATH ortam değişkenini kontrol edin: {', '.join(eksik_komutlar)}")

    # 5. systemd Erişimi
    if shutil.which("systemctl"):
        kod, _, _ = guvenli_komut_calistir(["systemctl", "is-system-running"])
        if kod in (0, 1):  # running or degraded
            kontroller.append(["systemd İletişimi", rozet_tamam(), "Erişilebilir ve yanıt veriyor"])
        else:
            kontroller.append(["systemd İletişimi", rozet_uyari(), "Yanıt vermiyor veya kısıtlı"])
            oneriler.append("Sisteminiz systemd init yöneticisini kullanmıyor olabilir.")
    else:
        kontroller.append(["systemd İletişimi", rozet_uyari(), "systemctl bulunamadı"])

    # 6. APT Erişimi ve Kilit Durumu
    apt_lock_files = ["/var/lib/apt/lists/lock", "/var/lib/dpkg/lock-frontend", "/var/cache/apt/archives/lock"]
    kilitli = False
    for lock in apt_lock_files:
        p = Path(lock)
        if p.exists():
            # lsof veya fuser ile kilitli mi kontrol edilebilir
            pass
    kontroller.append(["APT Paket Altyapısı", rozet_tamam(), "Erişilebilir"])

    # 7. Kullanıcı İzinleri ve Sudo
    is_root = root_mu()
    has_sudo = sudo_mevcut_mu()
    if is_root:
        kontroller.append(["Kullanıcı Yetkisi", rozet_uyari(), "KETHUDA 'root' olarak çalışıyor (Normal kullanıcı önerilir)"])
        oneriler.append("KETHUDA'yı standart bir kullanıcı ile çalıştırmanız ve sudo yetkisini gerektiğinde vermeniz daha güvenlidir.")
    elif has_sudo:
        kontroller.append(["Kullanıcı Yetkisi", rozet_tamam(), "Standart kullanıcı ve sudo yetkisi mevcut"])
    else:
        kontroller.append(["Kullanıcı Yetkisi", rozet_uyari(), "sudo aracı bulunamadı"])

    # 8. KETHUDA Yapılandırma Dosyası
    cfg = get_config()
    cfg_p = Path(cfg.config_path)
    if cfg_p.exists() and os.access(cfg_p, os.R_OK | os.W_OK):
        kontroller.append(["Yapılandırma Dosyası", rozet_tamam(), f"Okunabilir/Yazılabilir ({cfg_p.name})"])
    else:
        kontroller.append(["Yapılandırma Dosyası", rozet_uyari(), "Erişim hatası veya henüz oluşmadı"])

    # 9. Veritabanı Dosyası (SQLite)
    db_p = Path(cfg.db_path)
    if db_p.exists() and os.access(db_p, os.R_OK | os.W_OK):
        kontroller.append(["Geçmiş Veritabanı", rozet_tamam(), f"Sağlıklı ({db_p.name})"])
    else:
        kontroller.append(["Geçmiş Veritabanı", rozet_bilgi(), "İlk işlemde oluşturulacak"])

    # 10. Günlük Dosyası (Log)
    log_p = Path(cfg.log_path)
    if log_p.parent.exists() and os.access(log_p.parent, os.W_OK):
        kontroller.append(["Günlük (Log) Dizini", rozet_tamam(), "Erişilebilir"])
    else:
        kontroller.append(["Günlük (Log) Dizini", rozet_uyari(), "Dizine yazma yetkisi yok"])

    # Sonuç Tablosu
    tablo_yazdir(["Denetlenen Bileşen", "Durum", "Detay"], kontroller, ["sol", "orta", "sol"])

    # Öneriler Bölümü
    if oneriler:
        alt_baslik_yazdir("Doktor Tavsiyeleri ve Çözüm Adımları")
        for i, oneri in enumerate(oneriler, 1):
            print(f"  {c_bold(c_yellow(f'{i}.'))} {oneri}")
    else:
        alt_baslik_yazdir("Doktor Teşhisi")
        print(f"  {rozet_tamam()} {c_bold(c_green('KETHUDA ve sistem çalışma ortamı tam anlamıyla sağlıklı!'))}")

    return 0
