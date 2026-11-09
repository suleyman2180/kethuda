"""
KETHUDA Temizlik Yönetimi Modülü
Önbellek, geçici dosyalar ve çöp kutusunu güvenle analiz eder ve onay alarak temizler.
Sistem dosyalarına ve kullanıcı belgelerine kesinlikle dokunmaz.
"""

import os
import shutil
import glob
from pathlib import Path
from typing import Dict, Any, List, Tuple
from kethuda.core.database import get_database
from kethuda.core.permissions import kullanici_onayi_al, root_mu, guvenli_komut_calistir
from kethuda.interface.output import (
    baslik_yazdir,
    alt_baslik_yazdir,
    tablo_yazdir,
    bayt_bicimlendir,
    rozet_tamam,
    rozet_uyari,
    rozet_bilgi,
    rozet_hata,
)
from kethuda.interface.colors import c_bold, c_green, c_yellow, c_red, c_dim, c_white
from kethuda.logger import log_bilgi, log_uyari, log_hata


def _dizin_boyutu_hesapla(dizin: Path) -> Tuple[int, int]:
    """Bir dizindeki dosya sayısını ve toplam bayt boyutunu döndürür."""
    if not dizin.exists():
        return 0, 0
    toplam_boyut = 0
    dosya_sayisi = 0
    try:
        for kok, _, dosyalar in os.walk(dizin, followlinks=False):
            for dosya in dosyalar:
                tam_yol = os.path.join(kok, dosya)
                try:
                    toplam_boyut += os.path.getsize(tam_yol)
                    dosya_sayisi += 1
                except (PermissionError, OSError):
                    pass
    except (PermissionError, OSError):
        pass
    return dosya_sayisi, toplam_boyut


def temizlik_alanlarini_analiz_et() -> List[Dict[str, Any]]:
    """Güvenli temizlenebilir alanları tespit eder ve boyutlarını hesaplar."""
    alanlar: List[Dict[str, Any]] = []
    home = Path.home()

    # 1. Çöp Kutusu (Trash)
    trash_path = home / ".local" / "share" / "Trash"
    t_sayi, t_boyut = _dizin_boyutu_hesapla(trash_path)
    alanlar.append(
        {
            "id": "cop_kutusu",
            "ad": "Kullanıcı Çöp Kutusu",
            "yol": str(trash_path),
            "sayi": t_sayi,
            "boyut": t_boyut,
            "guvenli": True,
            "aciklama": "Geri dönüşüm kutusundaki silinmiş dosyalar",
        }
    )

    # 2. Küçük Resim Önbelleği (Thumbnails)
    thumb_path = home / ".cache" / "thumbnails"
    th_sayi, th_boyut = _dizin_boyutu_hesapla(thumb_path)
    alanlar.append(
        {
            "id": "thumbnails",
            "ad": "Küçük Resim (Thumbnail) Önbelleği",
            "yol": str(thumb_path),
            "sayi": th_sayi,
            "boyut": th_boyut,
            "guvenli": True,
            "aciklama": "Dosya yöneticisi tarafından üretilen önizleme önbelleği",
        }
    )

    # 3. Genel Kullanıcı Önbellek Günlükleri (~/.cache log dosyaları)
    cache_path = home / ".cache"
    log_sayi = 0
    log_boyut = 0
    if cache_path.exists():
        try:
            for p in cache_path.glob("**/*.log"):
                try:
                    log_boyut += p.stat().st_size
                    log_sayi += 1
                except (PermissionError, OSError):
                    pass
        except Exception:
            pass
    alanlar.append(
        {
            "id": "cache_logs",
            "ad": "Önbellek Günlük Dosyaları (*.log)",
            "yol": str(cache_path),
            "sayi": log_sayi,
            "boyut": log_boyut,
            "guvenli": True,
            "aciklama": "Uygulamaların .cache dizinindeki eski günlük dosyaları",
        }
    )

    # 4. APT İndirilen Paket Önbelleği (/var/cache/apt/archives)
    apt_archives = Path("/var/cache/apt/archives")
    apt_sayi = 0
    apt_boyut = 0
    if apt_archives.exists():
        try:
            for p in apt_archives.glob("*.deb"):
                try:
                    apt_boyut += p.stat().st_size
                    apt_sayi += 1
                except (PermissionError, OSError):
                    pass
        except Exception:
            pass
    alanlar.append(
        {
            "id": "apt_cache",
            "ad": "APT Paket Önbelleği (.deb arşivleri)",
            "yol": str(apt_archives),
            "sayi": apt_sayi,
            "boyut": apt_boyut,
            "guvenli": True,
            "root_gerekir": True,
            "aciklama": "Sistem güncellemeleri sonrasında saklanan deb paketleri",
        }
    )

    # 5. Kullanıcıya ait /tmp geçici dosyaları
    uid = os.getuid()
    tmp_path = Path("/tmp")
    u_tmp_sayi = 0
    u_tmp_boyut = 0
    if tmp_path.exists():
        try:
            for item in tmp_path.iterdir():
                try:
                    st = item.stat()
                    if st.st_uid == uid and not item.name.startswith(".X11") and not item.name.startswith(".ICE"):
                        if item.is_file():
                            u_tmp_boyut += st.st_size
                            u_tmp_sayi += 1
                except (PermissionError, OSError):
                    pass
        except Exception:
            pass
    alanlar.append(
        {
            "id": "user_tmp",
            "ad": "Kullanıcı Geçici Dosyaları (/tmp)",
            "yol": "/tmp",
            "sayi": u_tmp_sayi,
            "boyut": u_tmp_boyut,
            "guvenli": True,
            "aciklama": "Kullanıcınıza ait güvenle silinebilir geçici dosyalar",
        }
    )

    return alanlar


def temizlik_onizlemesini_goster() -> int:
    """Temizlik analizini ve önizleme tablosunu yazdırır."""
    baslik_yazdir("GÜVENLİ TEMİZLİK ANALİZİ VE ÖNİZLEMESİ")
    print(f"  {c_dim('Sistem taranıyor, silinebilecek güvenli alanlar hesaplanıyor...')}\n")

    alanlar = temizlik_alanlarini_analiz_et()
    toplam_kazanc = sum(a["boyut"] for a in alanlar)
    toplam_dosya = sum(a["sayi"] for a in alanlar)

    satirlar = []
    for a in alanlar:
        satirlar.append(
            [
                a["ad"],
                str(a["sayi"]),
                bayt_bicimlendir(a["boyut"]),
                a["aciklama"],
            ]
        )

    tablo_yazdir(
        ["Temizlik Alanı", "Dosya Sayısı", "Kazanılabilir Alan", "Açıklama"],
        satirlar,
        ["sol", "sag", "sag", "sol"],
    )

    print(
        f"\n{rozet_bilgi()} Toplam {toplam_dosya} dosya temizlenebilir. "
        f"Kazanılacak yaklaşık alan: {c_bold(c_green(bayt_bicimlendir(toplam_kazanc)))}"
    )
    print(
        f"  {c_dim('Not: Temizlik işlemini gerçekleştirmek için: kethuda temizlik calistir')}\n"
    )
    return 0


def temizligi_calistir(otomatik_onay: bool = False) -> int:
    """Kullanıcı onayı alarak temizlik işlemini güvenle yürütür."""
    baslik_yazdir("GÜVENLİ TEMİZLİK İŞLEMİ")
    alanlar = temizlik_alanlarini_analiz_et()
    toplam_kazanc = sum(a["boyut"] for a in alanlar)
    toplam_dosya = sum(a["sayi"] for a in alanlar)

    if toplam_dosya == 0 or toplam_kazanc == 0:
        print(f"{rozet_tamam()} Temizlenecek gereksiz veya önbellek dosyası bulunamadı. Sistem zaten temiz.")
        return 0

    print(f"Toplam {toplam_dosya} dosya ({bayt_bicimlendir(toplam_kazanc)}) temizlenecektir.")
    print(f"{c_yellow('Dikkat: Bu işlem çöp kutusu ve önbellek içeriklerini kaldıracaktır.')}")

    if not otomatik_onay:
        onay = kullanici_onayi_al("Temizlik işlemini onaylıyor musunuz?", varsayilan=False)
        if not onay:
            print(f"{rozet_uyari()} Temizlik işlemi kullanıcı tarafından iptal edildi.")
            get_database().kaydet("TEMİZLİK", "kethuda temizlik calistir", "İPTAL_EDİLDİ", False, "Kullanıcı reddetti.")
            return 0

    silinen_bayt = 0
    silinen_dosya = 0
    db = get_database()
    home = Path.home()

    # 1. Çöp Kutusu
    trash_path = home / ".local" / "share" / "Trash"
    if trash_path.exists():
        for sub in ("files", "info"):
            target_sub = trash_path / sub
            if target_sub.exists():
                for item in target_sub.iterdir():
                    try:
                        if item.is_file() or item.is_symlink():
                            sz = item.stat().st_size
                            item.unlink()
                            silinen_bayt += sz
                            silinen_dosya += 1
                        elif item.is_dir():
                            shutil.rmtree(item, ignore_errors=True)
                            silinen_dosya += 1
                    except Exception:
                        pass

    # 2. Thumbnails
    thumb_path = home / ".cache" / "thumbnails"
    if thumb_path.exists():
        for item in thumb_path.glob("**/*"):
            if item.is_file():
                try:
                    sz = item.stat().st_size
                    item.unlink()
                    silinen_bayt += sz
                    silinen_dosya += 1
                except Exception:
                    pass

    # 3. Cache Logs
    cache_path = home / ".cache"
    if cache_path.exists():
        for item in cache_path.glob("**/*.log"):
            if item.is_file():
                try:
                    sz = item.stat().st_size
                    item.unlink()
                    silinen_bayt += sz
                    silinen_dosya += 1
                except Exception:
                    pass

    # 4. APT Cache (clean)
    kod, out, err = guvenli_komut_calistir(["apt-get", "clean"], sudo_kullan=True)
    if kod == 0:
        log_bilgi("APT önbelleği 'apt-get clean' ile temizlendi.")

    detay = f"{silinen_dosya} dosya temizlendi, {bayt_bicimlendir(silinen_bayt)} alan kazanıldı."
    db.kaydet("TEMİZLİK", "kethuda temizlik calistir", "BAŞARILI", True, detay)
    log_bilgi(f"Temizlik tamamlandı: {detay}")

    print(f"\n{rozet_tamam()} Temizlik işlemi başarıyla tamamlandı!")
    print(f"  Silinen dosya sayısı : {silinen_dosya}")
    print(f"  Kazanılan alan       : {bayt_bicimlendir(silinen_bayt)}")
    return 0
