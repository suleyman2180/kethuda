"""
KETHUDA Servis Yönetimi Modülü
Ubuntu systemd altyapısı üzerinden servisleri güvenli bir şekilde denetler ve yönetir.
"""

import shutil
from typing import List, Dict, Any, Optional
from kethuda.core.permissions import (
    servis_kritik_mi,
    kullanici_onayi_al,
    guvenli_komut_calistir,
    root_mu,
)
from kethuda.core.database import get_database
from kethuda.interface.output import (
    baslik_yazdir,
    alt_baslik_yazdir,
    tablo_yazdir,
    anahtar_deger_yazdir,
    rozet_tamam,
    rozet_uyari,
    rozet_hata,
    rozet_bilgi,
    rozet_kritik,
)
from kethuda.interface.colors import c_bold, c_green, c_yellow, c_red, c_cyan, c_dim
from kethuda.logger import log_bilgi, log_uyari, log_hata


def systemctl_mevcut_mu() -> bool:
    """systemctl komutunun varlığını kontrol eder."""
    return shutil.which("systemctl") is not None


def servisleri_listele(sadece_calisanlar: bool = False, limit: int = 30) -> int:
    """Sistem servislerini listeler."""
    if not systemctl_mevcut_mu():
        print(f"{rozet_hata()} 'systemctl' aracı bu sistemde bulunamadı.")
        return 1

    baslik_yazdir("SYSTEMD SERVİS LİSTESİ")

    komut = [
        "systemctl",
        "list-units",
        "--type=service",
        "--all",
        "--no-legend",
        "--no-pager",
    ]
    kod, cikti, hata = guvenli_komut_calistir(komut)
    if kod != 0:
        print(f"{rozet_hata()} Servisler listelenemedi: {hata}")
        return 1

    satirlar = []
    sayac = 0
    for satir in cikti.strip().splitlines():
        parcalar = satir.split()
        if not parcalar:
            continue
        # Başındaki '●' veya '*' gibi durum işaretlerini atla
        if parcalar[0] in ("●", "*", "loaded"):
            parcalar = parcalar[1:]
        if len(parcalar) >= 4:
            birim = parcalar[0]
            if not birim.endswith(".service"):
                continue
            yuklu = parcalar[1]
            aktif = parcalar[2]
            alt = parcalar[3]
            aciklama = " ".join(parcalar[4:]) if len(parcalar) > 4 else "-"

            if sadece_calisanlar and alt != "running":
                continue

            durum_rozet = rozet_tamam() if alt == "running" else rozet_uyari()
            satirlar.append([birim[:32], aktif, alt, aciklama[:30], durum_rozet])
            sayac += 1
            if sayac >= limit:
                break

    tablo_yazdir(
        ["Servis Birimi", "Aktif", "Alt Durum", "Açıklama", "Durum"],
        satirlar,
        ["sol", "orta", "orta", "sol", "orta"],
    )
    print(
        f"\n  {c_dim('Detay görmek için: kethuda servis durum <servis_adi>  |  Tümünü listelemek için limit artırılabilir.')}"
    )
    return 0


def servis_durumu_goster(servis_adi: str) -> int:
    """Belirtilen servisin detaylı durumunu görüntüler."""
    if not systemctl_mevcut_mu():
        print(f"{rozet_hata()} 'systemctl' aracı bu sistemde bulunamadı.")
        return 1

    if not servis_adi.endswith(".service"):
        servis_adi_tam = f"{servis_adi}.service"
    else:
        servis_adi_tam = servis_adi

    baslik_yazdir(f"SERVİS DURUMU: {servis_adi_tam}")

    # systemctl status
    komut = ["systemctl", "status", servis_adi_tam, "--no-pager", "-n", "10"]
    kod, cikti, hata = guvenli_komut_calistir(komut)

    # is-active, is-enabled kontrolleri
    _, is_active, _ = guvenli_komut_calistir(["systemctl", "is-active", servis_adi_tam])
    _, is_enabled, _ = guvenli_komut_calistir(["systemctl", "is-enabled", servis_adi_tam])

    kritik, sebep = servis_kritik_mi(servis_adi)
    koruma = f"{rozet_kritik()} {sebep}" if kritik else f"{rozet_tamam()} Normal Servis"

    anahtar_deger_yazdir(
        [
            ("Servis Adı", servis_adi_tam),
            ("Çalışma Durumu", is_active.strip() or "bilinmiyor"),
            ("Açılışta Etkin mi?", is_enabled.strip() or "bilinmiyor"),
            ("Kritik Koruma", koruma),
        ]
    )

    alt_baslik_yazdir("Son Sistem Günlüğü (Journal) Çıktıları")
    print(c_dim(cikti.strip() if cikti else "(Günlük çıktısı yok)"))
    return 0


def servis_baslat(servis_adi: str) -> int:
    """Bir servisi başlatır (sudo yetkisi gerekebilir)."""
    db = get_database()
    if not servis_adi.endswith(".service"):
        servis_adi_tam = f"{servis_adi}.service"
    else:
        servis_adi_tam = servis_adi

    baslik_yazdir(f"SERVİS BAŞLAT: {servis_adi_tam}")
    onay = kullanici_onayi_al(f"'{servis_adi_tam}' servisini başlatmak istiyor musunuz?", varsayilan=True)
    if not onay:
        print(f"{rozet_uyari()} İşlem iptal edildi.")
        return 0

    kod, cikti, hata = guvenli_komut_calistir(["systemctl", "start", servis_adi_tam], sudo_kullan=True)
    if kod == 0:
        print(f"{rozet_tamam()} '{servis_adi_tam}' servisi başarıyla başlatıldı.")
        db.kaydet("SERVİS", f"servis baslat {servis_adi_tam}", "BAŞARILI", True)
        log_bilgi(f"Servis başlatıldı: {servis_adi_tam}")
        return 0
    else:
        print(f"{rozet_hata()} Servis başlatılamadı: {hata}")
        db.kaydet("SERVİS", f"servis baslat {servis_adi_tam}", "BAŞARISIZ", True, hata)
        return 1


def servis_durdur(servis_adi: str) -> int:
    """Bir servisi kritik kontrollerden geçirerek durdurur."""
    db = get_database()
    if not servis_adi.endswith(".service"):
        servis_adi_tam = f"{servis_adi}.service"
    else:
        servis_adi_tam = servis_adi

    kritik, sebep = servis_kritik_mi(servis_adi)
    if kritik:
        print(f"\n{rozet_kritik()} {c_bold('DURDURMA ENGELLENDİ!')}")
        print(f"  {sebep}")
        db.kaydet("SERVİS", f"servis durdur {servis_adi_tam}", "ENGELLENDİ", False, sebep)
        return 1

    baslik_yazdir(f"SERVİS DURDUR: {servis_adi_tam}")
    onay = kullanici_onayi_al(f"'{servis_adi_tam}' servisini durdurmak istediğinize emin misiniz?", varsayilan=False)
    if not onay:
        print(f"{rozet_uyari()} İşlem iptal edildi.")
        return 0

    kod, cikti, hata = guvenli_komut_calistir(["systemctl", "stop", servis_adi_tam], sudo_kullan=True)
    if kod == 0:
        print(f"{rozet_tamam()} '{servis_adi_tam}' servisi başarıyla durduruldu.")
        db.kaydet("SERVİS", f"servis durdur {servis_adi_tam}", "BAŞARILI", True)
        log_bilgi(f"Servis durduruldu: {servis_adi_tam}")
        return 0
    else:
        print(f"{rozet_hata()} Servis durdurulamadı: {hata}")
        db.kaydet("SERVİS", f"servis durdur {servis_adi_tam}", "BAŞARISIZ", True, hata)
        return 1


def servis_yeniden_baslat(servis_adi: str) -> int:
    """Bir servisi yeniden başlatır."""
    db = get_database()
    if not servis_adi.endswith(".service"):
        servis_adi_tam = f"{servis_adi}.service"
    else:
        servis_adi_tam = servis_adi

    baslik_yazdir(f"SERVİS YENİDEN BAŞLAT: {servis_adi_tam}")
    onay = kullanici_onayi_al(f"'{servis_adi_tam}' servisini yeniden başlatmak istiyor musunuz?", varsayilan=True)
    if not onay:
        print(f"{rozet_uyari()} İşlem iptal edildi.")
        return 0

    kod, cikti, hata = guvenli_komut_calistir(["systemctl", "restart", servis_adi_tam], sudo_kullan=True)
    if kod == 0:
        print(f"{rozet_tamam()} '{servis_adi_tam}' servisi başarıyla yeniden başlatıldı.")
        db.kaydet("SERVİS", f"servis yeniden-baslat {servis_adi_tam}", "BAŞARILI", True)
        return 0
    else:
        print(f"{rozet_hata()} Servis yeniden başlatılamadı: {hata}")
        db.kaydet("SERVİS", f"servis yeniden-baslat {servis_adi_tam}", "BAŞARISIZ", True, hata)
        return 1


def etkin_servisleri_listele() -> int:
    """Sistem açılışında otomatik başlayan (enabled) servisleri listeler."""
    baslik_yazdir("AÇILIŞTA ETKİN SERVİSLER (ENABLED)")
    komut = [
        "systemctl",
        "list-unit-files",
        "--type=service",
        "--state=enabled",
        "--no-legend",
        "--no-pager",
    ]
    kod, cikti, hata = guvenli_komut_calistir(komut)
    if kod != 0:
        print(f"{rozet_hata()} Etkin servisler okunamadı: {hata}")
        return 1

    satirlar = []
    for satir in cikti.strip().splitlines()[:35]:
        parcalar = satir.split()
        if len(parcalar) >= 2:
            satirlar.append([parcalar[0], parcalar[1], rozet_tamam()])

    tablo_yazdir(["Birim Dosyası", "Durum", "Öncelik"], satirlar, ["sol", "orta", "orta"])
    return 0


def servis_devre_disi_birak(servis_adi: str) -> int:
    """Bir servisin açılışta başlamasını engeller (disable)."""
    db = get_database()
    if not servis_adi.endswith(".service"):
        servis_adi_tam = f"{servis_adi}.service"
    else:
        servis_adi_tam = servis_adi

    kritik, sebep = servis_kritik_mi(servis_adi)
    if kritik:
        print(f"\n{rozet_kritik()} {c_bold('DEVRE DIŞI BIRAKMA ENGELLENDİ!')}")
        print(f"  {sebep}")
        return 1

    baslik_yazdir(f"SERVİS DEVRE DIŞI BIRAK: {servis_adi_tam}")
    onay = kullanici_onayi_al(
        f"'{servis_adi_tam}' servisinin açılışta başlamasını engellemek istiyor musunuz?",
        varsayilan=False,
    )
    if not onay:
        print(f"{rozet_uyari()} İşlem iptal edildi.")
        return 0

    kod, cikti, hata = guvenli_komut_calistir(["systemctl", "disable", servis_adi_tam], sudo_kullan=True)
    if kod == 0:
        print(f"{rozet_tamam()} '{servis_adi_tam}' servisi açılışta devre dışı bırakıldı.")
        db.kaydet("SERVİS", f"servis devre-disi {servis_adi_tam}", "BAŞARILI", True)
        return 0
    else:
        print(f"{rozet_hata()} İşlem başarısız: {hata}")
        db.kaydet("SERVİS", f"servis devre-disi {servis_adi_tam}", "BAŞARISIZ", True, hata)
        return 1
