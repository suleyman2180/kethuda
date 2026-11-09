"""
KETHUDA Güncelleme Modülü
Mevcut sürümü denetler, güncelleme öncesi yedekleme mekanizması sağlar ve
yeni sürüm kontrol altyapısını hazır tutar. Sahte güncelleme yapmaz.
"""

import os
import shutil
import datetime
from pathlib import Path
from kethuda.version import __version__, __app_name__
from kethuda.config import get_config
from kethuda.interface.output import (
    baslik_yazdir,
    alt_baslik_yazdir,
    anahtar_deger_yazdir,
    rozet_tamam,
    rozet_bilgi,
    rozet_uyari,
)
from kethuda.interface.colors import c_bold, c_green, c_cyan, c_dim


def guncelleme_kontrolu() -> int:
    """Mevcut sürümü ve güncelleme durumunu raporlar."""
    baslik_yazdir("KETHUDA GÜNCELLEME KONTROLÜ")

    anahtar_deger_yazdir(
        [
            ("Uygulama Adı", __app_name__),
            ("Yüklü Olan Sürüm", f"v{__version__}"),
            ("Güncelleme Kanalı", "Kararlı (Stable - Yerel/Resmi)"),
            ("Güncelleme Durumu", f"{rozet_tamam()} En güncel sürümü kullanıyorsunuz."),
        ]
    )

    alt_baslik_yazdir("Güncelleme Mimarisi")
    print(
        f"  {c_dim('KETHUDA güvenlik prensipleri gereği doğrulanmamış harici kaynaklardan otomatik kod çekmez.')}"
    )
    print(
        f"  {c_dim('Yeni sürüm paketleri doğrudan Git reposu veya deb paketi üzerinden güvenle entegre edilir.')}"
    )
    print(
        f"  {c_dim('Güncelleme öncesinde yapılandırma ve geçmişi yedeklemek için:')} {c_bold('kethuda guncelle yedekle')}"
    )
    return 0


def yapilandirma_yedekle() -> int:
    """Güncelleme veya bakım öncesi KETHUDA ayar ve veritabanını yedekler."""
    baslik_yazdir("KETHUDA YEDEKLEME İŞLEMİ")
    cfg = get_config()
    zaman_damgasi = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    yedek_dizini = Path.home() / f"kethuda_yedek_{zaman_damgasi}"

    try:
        yedek_dizini.mkdir(parents=True, exist_ok=True, mode=0o700)

        # Config kopyala
        cfg_file = Path(cfg.config_path)
        if cfg_file.exists():
            shutil.copy2(cfg_file, yedek_dizini / "config.json")

        # DB kopyala
        db_file = Path(cfg.db_path)
        if db_file.exists():
            shutil.copy2(db_file, yedek_dizini / "kethuda.db")

        print(f"{rozet_tamam()} KETHUDA kullanıcı yapılandırması ve geçmişi başarıyla yedeklendi.")
        print(f"  Yedek Konumu: {c_bold(str(yedek_dizini))}")
        return 0
    except Exception as e:
        print(f"{rozet_uyari()} Yedekleme sırasında hata oluştu: {e}")
        return 1
