"""
KETHUDA Paket ve Yazılım Yönetimi Modülü
Ubuntu APT ve dpkg altyapısını kullanarak paket denetimi, arama, güncelleme ve güvenli kaldırma sağlar.
"""

import re
import shutil
from pathlib import Path
from typing import List, Dict, Any, Optional
from kethuda.core.permissions import guvenli_komut_calistir, kullanici_onayi_al
from kethuda.core.database import get_database
from kethuda.interface.output import (
    baslik_yazdir,
    alt_baslik_yazdir,
    tablo_yazdir,
    anahtar_deger_yazdir,
    bayt_bicimlendir,
    rozet_tamam,
    rozet_uyari,
    rozet_hata,
    rozet_bilgi,
)
from kethuda.interface.colors import c_bold, c_green, c_yellow, c_red, c_cyan, c_dim
from kethuda.logger import log_bilgi, log_uyari, log_hata

# Geçerli paket adı deseni (enjeksiyon engelleme)
PAKET_ADI_REGEX = re.compile(r"^[a-zA-Z0-9][a-zA-Z0-9\+\-\.:]+$")


def _paket_adi_gecerli_mi(paket_adi: str) -> bool:
    return bool(PAKET_ADI_REGEX.match(paket_adi))


def paketleri_listele(limit: int = 30) -> int:
    """Kurulu paketlerin sayısını ve ilk paketleri listeler."""
    baslik_yazdir("KURULU SİSTEM PAKETLERİ (DPKG/APT)")

    # dpkg-query ile hızlı liste al
    kod, cikti, hata = guvenli_komut_calistir(
        ["dpkg-query", "-W", "-f=${binary:Package}\t${Version}\t${Status}\n"]
    )
    if kod != 0:
        print(f"{rozet_hata()} Paketler listelenemedi: {hata}")
        return 1

    satirlar = []
    kurulu_sayisi = 0
    ornekler = []

    for satir in cikti.strip().splitlines():
        parcalar = satir.split("\t")
        if len(parcalar) >= 3 and "installed" in parcalar[2]:
            kurulu_sayisi += 1
            if len(ornekler) < limit:
                ornekler.append([parcalar[0][:28], parcalar[1][:22], rozet_tamam()])

    tablo_yazdir(["Paket Adı", "Sürüm", "Durum"], ornekler, ["sol", "sol", "orta"])
    print(
        f"\n{rozet_bilgi()} Sistemde toplam {c_bold(c_green(str(kurulu_sayisi)))} adet kurulu paket tespit edildi."
    )
    print(
        f"  {c_dim('Paket aramak için: kethuda paket ara <kelime>  |  Detay: kethuda paket bilgi <paket>')}"
    )
    return 0


def paket_ara(kelime: str, limit: int = 25) -> int:
    """APT deposunda paket arar."""
    if not _paket_adi_gecerli_mi(kelime):
        print(f"{rozet_hata()} Geçersiz arama terimi.")
        return 1

    baslik_yazdir(f"PAKET ARAMA: '{kelime}'")
    kod, cikti, hata = guvenli_komut_calistir(["apt-cache", "search", kelime])
    if kod != 0:
        print(f"{rozet_hata()} Paket arama başarısız: {hata}")
        return 1

    satirlar = []
    for satir in cikti.strip().splitlines()[:limit]:
        if " - " in satir:
            p_ad, desc = satir.split(" - ", 1)
            satirlar.append([p_ad.strip()[:26], desc.strip()[:48]])

    if not satirlar:
        print(f"{rozet_uyari()} '{kelime}' ile eşleşen bir paket bulunamadı.")
        return 0

    tablo_yazdir(["Paket", "Açıklama"], satirlar, ["sol", "sol"])
    return 0


def paket_bilgisi(paket_adi: str) -> int:
    """Belirtilen paketin dpkg veya apt detaylarını görüntüler."""
    if not _paket_adi_gecerli_mi(paket_adi):
        print(f"{rozet_hata()} Geçersiz paket adı.")
        return 1

    baslik_yazdir(f"PAKET BİLGİSİ: {paket_adi}")

    # Önce sistemde kurulu mu kontrol et
    kod, cikti, _ = guvenli_komut_calistir(["dpkg", "-s", paket_adi])
    if kod == 0:
        alt_baslik_yazdir("Kurulu Paket Bilgisi")
        bilgiler = []
        for line in cikti.splitlines()[:15]:
            if ":" in line and not line.startswith(" "):
                k, v = line.split(":", 1)
                bilgiler.append((k.strip(), v.strip()[:60]))
        anahtar_deger_yazdir(bilgiler)
        return 0

    # Kurulu değilse depodan getir
    kod2, cikti2, _ = guvenli_komut_calistir(["apt-cache", "show", paket_adi])
    if kod2 == 0:
        alt_baslik_yazdir("Depo Paket Bilgisi (Kurulu Değil)")
        bilgiler = []
        for line in cikti2.splitlines()[:15]:
            if ":" in line and not line.startswith(" "):
                k, v = line.split(":", 1)
                bilgiler.append((k.strip(), v.strip()[:60]))
        anahtar_deger_yazdir(bilgiler)
        return 0

    print(f"{rozet_uyari()} '{paket_adi}' paketi bulunamadı.")
    return 1


def guncellemeleri_kontrol_et() -> int:
    """Güncellenebilir paketleri listeler."""
    baslik_yazdir("GÜNCELLENEBİLİR PAKETLER KONTROLÜ")
    print(f"  {c_dim('Paket listeleri denetleniyor (apt list --upgradable)...')}")

    kod, cikti, hata = guvenli_komut_calistir(["apt", "list", "--upgradable"])
    if kod != 0:
        print(f"{rozet_hata()} Güncelleme denetimi yapılamadı: {hata}")
        return 1

    satirlar = []
    for line in cikti.strip().splitlines():
        if line.startswith("Listing...") or not line:
            continue
        parcalar = line.split()
        if len(parcalar) >= 2:
            p_ad = parcalar[0]
            surum = parcalar[1]
            satirlar.append([p_ad[:30], surum, rozet_uyari()])

    if not satirlar:
        print(f"\n{rozet_tamam()} Tüm paketler güncel. Yeni güncelleme bulunmuyor.")
        return 0

    tablo_yazdir(["Güncellenecek Paket", "Yeni Sürüm", "Durum"], satirlar, ["sol", "sol", "orta"])
    print(
        f"\n{rozet_uyari()} Toplam {c_bold(str(len(satirlar)))} paket güncellenebilir."
    )
    print(f"  {c_dim('Güncellemek için: kethuda paket guncelle')}")
    return 0


def paket_guncelle() -> int:
    """Sistem paketlerini günceller (onay ve sudo ile)."""
    db = get_database()
    baslik_yazdir("SİSTEM PAKETLERİNİ GÜNCELLEME")

    print(f"{c_yellow('Bu işlem önce paket indekslerini yenileyecek (apt update), ardından paketleri güncelleyecektir (apt upgrade).')}")
    onay = kullanici_onayi_al("Paket güncelleme işlemini başlatmak istiyor musunuz?", varsayilan=False)
    if not onay:
        print(f"{rozet_uyari()} İşlem iptal edildi.")
        return 0

    print(f"\n{c_bold('1/2. Paket indeksleri güncelleniyor (apt update)...')}")
    kod, out, err = guvenli_komut_calistir(["apt-get", "update"], sudo_kullan=True, zaman_asimi=300)
    if kod != 0:
        print(f"{rozet_hata()} Paket indeksleri güncellenemedi: {err}")
        db.kaydet("PAKET", "paket guncelle (apt update)", "BAŞARISIZ", True, err)
        return 1

    print(f"\n{c_bold('2/2. Paketler kuruluyor (apt-get upgrade -y)...')}")
    kod2, out2, err2 = guvenli_komut_calistir(["apt-get", "upgrade", "-y"], sudo_kullan=True, zaman_asimi=600)
    if kod2 == 0:
        print(f"\n{rozet_tamam()} Tüm sistem paketleri başarıyla güncellendi.")
        db.kaydet("PAKET", "paket guncelle (apt upgrade)", "BAŞARILI", True)
        log_bilgi("Paket güncelleme başarıyla tamamlandı.")
        return 0
    else:
        print(f"\n{rozet_hata()} Paket güncelleme sırasında hata oluştu: {err2}")
        db.kaydet("PAKET", "paket guncelle (apt upgrade)", "BAŞARISIZ", True, err2)
        return 1


def paket_kaldir(paket_adi: str) -> int:
    """Bir paketi kullanıcıdan açık onay alarak sistemden kaldırır."""
    if not _paket_adi_gecerli_mi(paket_adi):
        print(f"{rozet_hata()} Geçersiz paket adı.")
        return 1

    db = get_database()
    baslik_yazdir(f"PAKET KALDIRMA: {paket_adi}")

    # Önizleme için dry-run yap
    kod, out, err = guvenli_komut_calistir(["apt-get", "--dry-run", "remove", paket_adi])
    print(c_dim("Kaldırma simülasyonu:"))
    for line in out.splitlines()[:10]:
        print(f"  {line}")

    onay = kullanici_onayi_al(
        f"'{paket_adi}' paketini ve bağımlılıklarını sistemden kaldırmak istiyor musunuz?",
        varsayilan=False,
    )
    if not onay:
        print(f"{rozet_uyari()} Kaldırma işlemi iptal edildi.")
        return 0

    kod, out, err = guvenli_komut_calistir(["apt-get", "remove", "-y", paket_adi], sudo_kullan=True)
    if kod == 0:
        print(f"{rozet_tamam()} '{paket_adi}' paketi sistemden kaldırıldı.")
        db.kaydet("PAKET", f"paket kaldir {paket_adi}", "BAŞARILI", True)
        log_bilgi(f"Paket kaldırıldı: {paket_adi}")
        return 0
    else:
        print(f"{rozet_hata()} Paket kaldırılamadı: {err}")
        db.kaydet("PAKET", f"paket kaldir {paket_adi}", "BAŞARISIZ", True, err)
        return 1


def gereksiz_paketleri_tara() -> int:
    """Kullanılmayan artık (autoremove) paketleri tespit eder."""
    baslik_yazdir("KULLANILMAYAN (ARTIK) PAKET ANALİZİ")
    print(f"  {c_dim('Gereksiz bağımlılıklar analiz ediliyor (apt-get --dry-run autoremove)...')}")

    kod, out, err = guvenli_komut_calistir(["apt-get", "--dry-run", "autoremove"])
    if kod != 0:
        print(f"{rozet_hata()} Analiz başarısız: {err}")
        return 1

    artik_paketler = []
    kaydet = False
    for line in out.splitlines():
        if "The following packages will be REMOVED" in line or "Aşağıdaki paketler KALDIRILACAK" in line:
            kaydet = True
            continue
        if kaydet:
            if line.startswith(" ") or line.startswith("\t"):
                artik_paketler.extend(line.split())
            else:
                break

    if not artik_paketler:
        print(f"\n{rozet_tamam()} Sistemde gereksiz artık paket tespit edilmedi.")
        return 0

    satirlar = [[p, "Artık Bağımlılık", rozet_uyari()] for p in artik_paketler]
    tablo_yazdir(["Paket Adı", "Tür", "Durum"], satirlar, ["sol", "sol", "orta"])

    print(f"\n{rozet_bilgi()} Toplam {len(artik_paketler)} adet artık paket temizlenebilir.")
    print(f"  {c_dim('Temizlemek için sistemde: sudo apt autoremove çalıştırabilirsiniz.')}")
    return 0


def apt_onbellegini_goster() -> int:
    """APT önbellek boyutunu ve dosya sayısını gösterir."""
    baslik_yazdir("APT ÖNBELLEK ANALİZİ")
    apt_dir = Path("/var/cache/apt/archives")
    if not apt_dir.exists():
        print(f"{rozet_uyari()} APT arşiv dizini bulunamadı.")
        return 1

    deb_sayisi = 0
    toplam_bayt = 0
    for deb in apt_dir.glob("*.deb"):
        try:
            toplam_bayt += deb.stat().st_size
            deb_sayisi += 1
        except Exception:
            pass

    anahtar_deger_yazdir(
        [
            ("APT Önbellek Dizini", str(apt_dir)),
            ("Saklanan .deb Dosya Sayısı", deb_sayisi),
            ("Toplam Önbellek Boyutu", bayt_bicimlendir(toplam_bayt)),
        ]
    )
    if deb_sayisi > 0:
        print(
            f"\n{rozet_bilgi()} Bu önbelleği temizlemek için: {c_bold('kethuda temizlik calistir')}"
        )
    return 0
