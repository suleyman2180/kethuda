"""
KETHUDA Yardım ve Sürüm Modülü
Komut sözlüğünü, kullanım örneklerini ve detaylı sürüm bilgilerini gösterir.
"""

import sys
import platform
from kethuda.version import __app_name__, __version__, __description__, __author__, __license__
from kethuda.config import get_config
from kethuda.core.system_info import os_dagitim_bilgisi
from kethuda.interface.output import (
    baslik_yazdir,
    alt_baslik_yazdir,
    tablo_yazdir,
    anahtar_deger_yazdir,
    rozet_tamam,
    rozet_bilgi,
)
from kethuda.interface.colors import c_bold, c_bright_cyan, c_cyan, c_white, c_dim, c_green


def yardim_goster(alt_konu: str = "") -> int:
    """KETHUDA kapsamlı yardım kılavuzunu görüntüler."""
    baslik_yazdir("KETHUDA YARDIM VE KOMUT KILAVUZU")
    print(f"  {c_dim('Kullanım:')} {c_bold('kethuda')} [komut] [alt-komut] [parametreler]\n")

    komutlar = [
        ("durum", "Sistem durumu", "kethuda durum", "CPU, RAM, Disk, Çalışma süresi ve donanım özeti"),
        ("disk", "Disk yönetimi", "kethuda disk [liste|buyuk-dosyalar|buyuk-klasorler|rapor]", "Disk doluluk, büyük dosya ve klasör analizleri"),
        ("temizlik", "Temizlik", "kethuda temizlik [analiz|onizleme|calistir]", "Güvenli önbellek, çöp kutusu ve geçici dosya temizliği"),
        ("islem", "Süreç yönetimi", "kethuda islem [liste|ara|detay|sonlandir]", "Çalışan süreçleri listeleme, filtreleme ve sonlandırma"),
        ("servis", "Servis yönetimi", "kethuda servis [liste|durum|baslat|durdur|yeniden-baslat|etkin|devre-disi]", "systemd servislerini başlatma, durdurma ve denetleme"),
        ("paket", "Paket yönetimi", "kethuda paket [liste|ara|bilgi|kontrol|guncelle|kaldir|gereksiz|onbellek]", "APT/DPKG paket yönetimi, güncelleme ve arama"),
        ("kontrol", "Sistem denetimi", "kethuda kontrol", "Tek komutla genel sistem kontrol raporu"),
        ("doktor", "Sistem doktoru", "kethuda doktor", "KETHUDA bağımlılıkları, sistem sağlığı ve izin denetimi"),
        ("gecmis", "İşlem geçmişi", "kethuda gecmis [liste|temizle]", "SQLite tabanlı işlem ve komut geçmişi kayıtları"),
        ("ayar", "Yapılandırma", "kethuda ayar [liste|getir|belirle|sifirla]", "Merkezi KETHUDA tercihlerini kalıcı olarak yönetme"),
        ("guncelle", "Güncelleme", "kethuda guncelle [kontrol|yedekle]", "Sürüm denetimi ve yapılandırma yedekleme"),
        ("surum", "Sürüm bilgisi", "kethuda surum", "Program, Python ve çekirdek sürüm detayları"),
        ("yardim", "Yardım kılavuzu", "kethuda yardim", "Komut listesini ve yardım dökümantasyonunu gösterir"),
    ]

    satirlar = []
    for k, tur, ornek, aciklama in komutlar:
        satirlar.append([c_bold(c_bright_cyan(k)), ornek, aciklama])

    tablo_yazdir(["Komut", "Kullanım Örneği", "Açıklama"], satirlar, ["sol", "sol", "sol"])

    print(f"\n  {c_bold('İpucu:')} Argümansız olarak sadece {c_bold('kethuda')} yazarak etkileşimli kabuğa geçebilirsiniz.")
    print(f"  {c_dim('Türkçe karakterli (ör. işlem, geçmiş) veya İngilizce karakterli (islem, gecmis) komutlar eşit şekilde desteklenir.')}\n")
    return 0


def surum_goster() -> int:
    """Detaylı sürüm ve ortam bilgilerini görüntüler."""
    os_info = os_dagitim_bilgisi()
    cfg = get_config()
    gelistirici_notu = cfg.getir("gelistirici_notu", "KETHUDA Ekibi")

    baslik_yazdir("KETHUDA SÜRÜM BİLGİLERİ")
    anahtar_deger_yazdir(
        [
            ("Yazılım Adı", __app_name__),
            ("Sürüm", f"v{__version__}"),
            ("Açıklama", __description__),
            ("Geliştirici", __author__),
            ("Lisans", __license__),
            ("Geliştirici Notu", gelistirici_notu),
            ("Python Sürümü", platform.python_version()),
            ("İşletim Sistemi", f"{os_info['ad']} {os_info['surum']}".strip()),
            ("Linux Kernel", platform.release()),
            ("Sistem Mimarisi", platform.machine()),
        ]
    )
    return 0
