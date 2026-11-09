"""
KETHUDA Ayarlar (Yapılandırma) Modülü
'kethuda ayar' komutu ile merkezi yapılandırmayı görüntüler, düzenler ve yönetir.
"""

from typing import Optional
from kethuda.config import get_config, VARSAYILAN_AYARLAR
from kethuda.core.permissions import kullanici_onayi_al
from kethuda.interface.output import (
    baslik_yazdir,
    alt_baslik_yazdir,
    tablo_yazdir,
    anahtar_deger_yazdir,
    rozet_tamam,
    rozet_uyari,
    rozet_hata,
    rozet_bilgi,
)
from kethuda.interface.colors import c_bold, c_green, c_yellow, c_cyan, c_dim

AYAR_ACIKLAMALARI = {
    "renkler": "Terminal ANSI renk çıktılarını etkinleştirir (True/False)",
    "cikti_bicimi": "Varsayılan çıktı biçimi (standart, tablo, sade)",
    "gunluk_seviyesi": "Dosya günlüğü detay seviyesi (DEBUG, INFO, WARNING, ERROR)",
    "onay_istensin": "Kritik ve silme işlemlerinde kullanıcıdan onay ister (True/False)",
    "buyuk_dosya_esigi_mb": "Büyük dosya taraması için megabayt eşiği",
    "buyuk_klasor_esigi_mb": "Büyük klasör taraması için megabayt eşiği",
    "disk_uyari_yuzdesi": "Disk doluluk uyarısı verilecek yüzde eşiği",
    "kritik_islem_korumasi": "Sistem çekirdeği ve init süreçlerini korur (True/False)",
    "kritik_servis_korumasi": "Kritik ağ/dbus/ssh servislerini korur (True/False)",
    "gelistirici_notu": "Kullanıcı veya geliştirici tanımlı not",
}


def ayarlari_listele() -> int:
    """Tüm yapılandırma ayarlarını tablo halinde listeler."""
    cfg = get_config()
    baslik_yazdir("KETHUDA MERKEZİ YAPILANDIRMA AYARLARI")
    print(f"  {c_dim('Yapılandırma Dosyası:')} {c_bold(cfg.config_path)}\n")

    mevcut = cfg.tumunu_al()
    satirlar = []

    for k, v in mevcut.items():
        aciklama = AYAR_ACIKLAMALARI.get(k, "-")
        satirlar.append([k, str(v), aciklama])

    tablo_yazdir(["Ayar Anahtarı", "Mevcut Değer", "Açıklama"], satirlar, ["sol", "sol", "sol"])
    print(
        f"\n  {c_dim('Ayar değiştirmek için : kethuda ayar belirle <anahtar> <değer>')}"
    )
    print(
        f"  {c_dim('Varsayılana dönmek için : kethuda ayar sifirla')}\n"
    )
    return 0


def ayar_getir(anahtar: str) -> int:
    """Belirli bir ayarın değerini görüntüler."""
    cfg = get_config()
    mevcut = cfg.tumunu_al()
    if anahtar not in mevcut:
        print(f"{rozet_uyari()} '{anahtar}' adında bir ayar bulunamadı.")
        return 1

    deger = mevcut[anahtar]
    aciklama = AYAR_ACIKLAMALARI.get(anahtar, "-")
    baslik_yazdir(f"AYAR DETAYI: {anahtar}")
    anahtar_deger_yazdir([("Ayar", anahtar), ("Değer", str(deger)), ("Açıklama", aciklama)])
    return 0


def ayar_belirle(anahtar: str, deger: str) -> int:
    """Bir ayarın değerini günceller ve kaydeder."""
    cfg = get_config()
    mevcut = cfg.tumunu_al()
    if anahtar not in mevcut:
        print(f"{rozet_hata()} Geçersiz ayar anahtarı: '{anahtar}'")
        print(f"  {c_dim('Geçerli anahtarları görmek için: kethuda ayar')}")
        return 1

    basarili = cfg.belirle(anahtar, deger)
    if basarili:
        yeni_deger = cfg.getir(anahtar)
        print(f"{rozet_tamam()} '{anahtar}' ayarı başarıyla güncellendi: {c_bold(str(yeni_deger))}")
        return 0
    else:
        print(f"{rozet_hata()} '{anahtar}' için girilen '{deger}' değeri geçersiz.")
        return 1


def ayarlari_sifirla() -> int:
    """Tüm ayarları varsayılanlara sıfırlar."""
    baslik_yazdir("AYARLARI VARSAYILANA SIFIRLA")
    onay = kullanici_onayi_al("Tüm ayarları varsayılan fabrika değerlerine döndürmek istiyor musunuz?", varsayilan=False)
    if not onay:
        print(f"{rozet_uyari()} Sıfırlama işlemi iptal edildi.")
        return 0

    cfg = get_config()
    if cfg.sifirla():
        print(f"{rozet_tamam()} Tüm ayarlar varsayılan değerlere başarıyla sıfırlandı.")
        return 0
    else:
        print(f"{rozet_hata()} Ayarlar sıfırlanırken hata oluştu.")
        return 1
