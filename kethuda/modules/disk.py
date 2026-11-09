"""
KETHUDA Disk Yönetimi Modülü
Disk bölümlerini listeler, büyük dosya ve klasörleri analiz eder ve doluluk uyarıları üretir.
"""

import os
import psutil
from pathlib import Path
from typing import List, Dict, Any, Optional
from kethuda.config import get_config
from kethuda.interface.output import (
    baslik_yazdir,
    alt_baslik_yazdir,
    tablo_yazdir,
    bayt_bicimlendir,
    cubuk,
    rozet_tamam,
    rozet_uyari,
    rozet_kritik,
    rozet_bilgi,
)
from kethuda.interface.colors import c_bold, c_yellow, c_red, c_green, c_cyan, c_dim


def disk_bolumlerini_al() -> List[Dict[str, Any]]:
    """Sistemdeki tüm fiziksel ve ana disk bölümlerini döndürür."""
    bolumler = []
    # Yalancı dosya sistemlerini (squashfs, tmpfs gibi aşırı kalabalık snap mountlarını) filtrele
    yoksayilan_turler = {"squashfs", "tmpfs", "devtmpfs", "overlay"}

    for part in psutil.disk_partitions(all=False):
        if part.fstype in yoksayilan_turler:
            continue
        try:
            kullanim = psutil.disk_usage(part.mountpoint)
            bolumler.append(
                {
                    "aygit": part.device,
                    "baglanti": part.mountpoint,
                    "dosya_sistemi": part.fstype,
                    "secenekler": part.opts,
                    "toplam": kullanim.total,
                    "kullanilan": kullanim.used,
                    "bos": kullanim.free,
                    "yuzde": kullanim.percent,
                }
            )
        except (PermissionError, OSError):
            continue
    return bolumler


def disk_listesini_goster() -> int:
    """Bağlı disk bölümlerini ve doluluk oranlarını gösterir."""
    baslik_yazdir("DİSK BÖLÜMLERİ VE BAĞLANTI NOKTALARI")
    bolumler = disk_bolumlerini_al()
    cfg = get_config()
    uyari_esigi = float(cfg.getir("disk_uyari_yuzdesi", 85))

    satirlar = []
    uyari_sayisi = 0

    for b in bolumler:
        yuzde = b["yuzde"]
        if yuzde >= 90:
            durum_rozet = rozet_kritik()
            uyari_sayisi += 1
        elif yuzde >= uyari_esigi:
            durum_rozet = rozet_uyari()
            uyari_sayisi += 1
        else:
            durum_rozet = rozet_tamam()

        satirlar.append(
            [
                b["aygit"],
                b["baglanti"],
                b["dosya_sistemi"],
                bayt_bicimlendir(b["toplam"]),
                bayt_bicimlendir(b["kullanilan"]),
                bayt_bicimlendir(b["bos"]),
                f"{yuzde:.1f}%",
                durum_rozet,
            ]
        )

    tablo_yazdir(
        [
            "Aygıt",
            "Bağlantı Noktası",
            "Dosya Sistemi",
            "Toplam",
            "Kullanılan",
            "Boş Alan",
            "Doluluk",
            "Durum",
        ],
        satirlar,
        ["sol", "sol", "sol", "sag", "sag", "sag", "sag", "orta"],
    )

    if uyari_sayisi > 0:
        print(
            f"\n{rozet_uyari()} {c_bold(f'{uyari_sayisi} disk bölümünde yüksek doluluk tespit edildi (%{uyari_esigi:.0f} üzeri).')}"
        )
    else:
        print(f"\n{rozet_tamam()} Tüm disk bölümleri normal doluluk sınırları içerisinde.")

    return 0


def buyuk_dosyalari_bul(
    hedef_dizin: Optional[str] = None,
    esik_mb: Optional[int] = None,
    limit: int = 15,
) -> int:
    """Belirtilen dizindeki büyük dosyaları tarar ve boyutlarına göre listeler."""
    cfg = get_config()
    if not hedef_dizin:
        hedef_dizin = str(Path.home())
    if esik_mb is None:
        esik_mb = int(cfg.getir("buyuk_dosya_esigi_mb", 50))

    esik_bayt = esik_mb * 1024 * 1024
    baslik_yazdir(f"BÜYÜK DOSYA ANALİZİ ({hedef_dizin} - Eşik: {esik_mb} MB)")
    print(f"  {c_dim('Dizin taranıyor, lütfen bekleyiniz...')}")

    bulunanlar = []
    taranan_sayac = 0

    try:
        for kok, dirs, dosyalar in os.walk(hedef_dizin, followlinks=False):
            # Gizli .git veya cache gibi aşırı döngü oluşturan dizinleri atla
            dirs[:] = [d for d in dirs if not d.startswith(".cache") and d != ".git"]
            for dosya in dosyalar:
                taranan_sayac += 1
                tam_yol = os.path.join(kok, dosya)
                try:
                    st = os.lstat(tam_yol)
                    if st.st_size >= esik_bayt:
                        bulunanlar.append((tam_yol, st.st_size))
                except (PermissionError, OSError):
                    continue
    except (PermissionError, OSError) as e:
        print(f"{rozet_uyari()} Bazı dizinlere erişilemedi: {e}")

    bulunanlar.sort(key=lambda x: x[1], reverse=True)
    listelenecek = bulunanlar[:limit]

    satirlar = []
    for yol, boyut in listelenecek:
        satirlar.append([yol, bayt_bicimlendir(boyut)])

    tablo_yazdir(["Dosya Yolu", "Boyut"], satirlar, ["sol", "sag"])

    print(
        f"\n  Toplam {taranan_sayac} dosya tarandı. {esik_mb} MB üzeri {len(bulunanlar)} büyük dosya bulundu."
    )
    return 0


def buyuk_klasorleri_analiz_et(hedef_dizin: Optional[str] = None) -> int:
    """Belirtilen dizinin alt klasörlerinin boyutlarını analiz eder."""
    if not hedef_dizin:
        hedef_dizin = str(Path.home())

    baslik_yazdir(f"BÜYÜK KLASÖR ANALİZİ ({hedef_dizin})")
    print(f"  {c_dim('Alt klasör boyutları hesaplanıyor...')}")

    klasor_boyutlari = []
    try:
        with os.scandir(hedef_dizin) as entries:
            for entry in entries:
                if entry.is_dir(follow_symlinks=False):
                    toplam_boyut = 0
                    try:
                        for kok, _, dosyalar in os.walk(entry.path, followlinks=False):
                            for dosya in dosyalar:
                                try:
                                    toplam_boyut += os.path.getsize(os.path.join(kok, dosya))
                                except (PermissionError, OSError):
                                    pass
                    except (PermissionError, OSError):
                        pass
                    klasor_boyutlari.append((entry.name, entry.path, toplam_boyut))
    except (PermissionError, OSError) as e:
        print(f"{rozet_uyari()} Dizin listelenirken hata: {e}")
        return 1

    klasor_boyutlari.sort(key=lambda x: x[2], reverse=True)

    satirlar = []
    for ad, yol, boyut in klasor_boyutlari[:15]:
        satirlar.append([ad, yol, bayt_bicimlendir(boyut)])

    tablo_yazdir(["Klasör Adı", "Tam Yol", "Toplam Boyut"], satirlar, ["sol", "sol", "sag"])
    return 0


def disk_raporu() -> int:
    """Kapsamlı depolama kullanım raporu oluşturur."""
    baslik_yazdir("DEPOLAMA KULLANIM RAPORU")
    disk_listesini_goster()
    print()
    buyuk_klasorleri_analiz_et(str(Path.home()))
    return 0
