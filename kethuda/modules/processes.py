"""
KETHUDA İşlem (Process) Yönetimi Modülü
Çalışan süreçleri listeler, filtreler, detaylandırır ve güvenli biçimde sonlandırır.
Kritik sistem süreçleri özel olarak korunur.
"""

import os
import time
import datetime
import psutil
from typing import List, Dict, Any, Optional
from kethuda.core.permissions import islem_kritik_mi, kullanici_onayi_al
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
    rozet_kritik,
)
from kethuda.interface.colors import c_bold, c_dim, c_yellow, c_red, c_green
from kethuda.logger import log_bilgi, log_uyari, log_hata


def islem_listesi_al(sirala: str = "cpu", limit: int = 20) -> List[Dict[str, Any]]:
    """Çalışan süreçleri toplar ve CPU/RAM kullanımına göre sıralar."""
    islemler = []
    for proc in psutil.process_iter(
        ["pid", "name", "username", "cpu_percent", "memory_percent", "status"]
    ):
        try:
            info = proc.info
            islemler.append(
                {
                    "pid": info["pid"],
                    "ad": info["name"] or "bilinmeyen",
                    "kullanici": info["username"] or "-",
                    "cpu": info["cpu_percent"] or 0.0,
                    "ram": info["memory_percent"] or 0.0,
                    "durum": info["status"] or "-",
                }
            )
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            continue

    if sirala == "ram":
        islemler.sort(key=lambda x: x["ram"], reverse=True)
    else:
        islemler.sort(key=lambda x: x["cpu"], reverse=True)

    return islemler[:limit]


def islemleri_listele(sirala: str = "cpu", limit: int = 20) -> int:
    """Çalışan süreçleri ekrana tablo olarak basar."""
    baslik_yazdir(f"ÇALIŞAN SİSTEM İŞLEMLERİ (Sıralama: {sirala.upper()})")
    islemler = islem_listesi_al(sirala=sirala, limit=limit)

    satirlar = []
    for p in islemler:
        satirlar.append(
            [
                str(p["pid"]),
                p["kullanici"][:14],
                p["ad"][:24],
                f"{p['cpu']:.1f}%",
                f"{p['ram']:.1f}%",
                p["durum"],
            ]
        )

    tablo_yazdir(
        ["PID", "Kullanıcı", "İşlem Adı", "CPU %", "RAM %", "Durum"],
        satirlar,
        ["sag", "sol", "sol", "sag", "sag", "sol"],
    )
    print(
        f"\n  {c_dim('Detay görmek için: kethuda islem detay <pid>  |  Arama için: kethuda islem ara <kelime>')}"
    )
    return 0


def islem_ara(kelime: str) -> int:
    """İşlem adına veya PID'sine göre filtreleme yapar."""
    baslik_yazdir(f"İŞLEM ARAMA: '{kelime}'")
    bulunanlar = []
    kelime_lower = kelime.lower()

    for proc in psutil.process_iter(
        ["pid", "name", "username", "cpu_percent", "memory_percent", "status"]
    ):
        try:
            info = proc.info
            ad = info["name"] or ""
            pid_str = str(info["pid"])
            if kelime_lower in ad.lower() or kelime_lower == pid_str:
                bulunanlar.append(
                    [
                        pid_str,
                        (info["username"] or "-")[:14],
                        ad[:24],
                        f"{(info['cpu_percent'] or 0.0):.1f}%",
                        f"{(info['memory_percent'] or 0.0):.1f}%",
                        info["status"] or "-",
                    ]
                )
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            continue

    if not bulunanlar:
        print(f"{rozet_uyari()} '{kelime}' ile eşleşen bir işlem bulunamadı.")
        return 1

    tablo_yazdir(
        ["PID", "Kullanıcı", "İşlem Adı", "CPU %", "RAM %", "Durum"],
        bulunanlar,
        ["sag", "sol", "sol", "sag", "sag", "sol"],
    )
    return 0


def islem_detayi_goster(pid: int) -> int:
    """Belirtilen PID'ye sahip sürecin derinlemesine bilgilerini gösterir."""
    try:
        proc = psutil.Process(pid)
    except psutil.NoSuchProcess:
        print(f"{rozet_hata()} PID {pid} ile çalışan bir işlem bulunamadı.")
        return 1
    except psutil.AccessDenied:
        print(f"{rozet_uyari()} PID {pid} bilgilerine erişim yetkisi yetersiz.")
        return 1

    baslik_yazdir(f"İŞLEM DETAYI: PID {pid}")
    try:
        with proc.oneshot():
            ad = proc.name()
            ppid = proc.ppid()
            kullanici = proc.username()
            durum = proc.status()
            olusturulma = datetime.datetime.fromtimestamp(proc.create_time()).strftime(
                "%Y-%m-%d %H:%M:%S"
            )
            komut = " ".join(proc.cmdline()) or ad
            bellek = proc.memory_info()
            cpu_yuzde = proc.cpu_percent(interval=0.1)
            ram_yuzde = proc.memory_percent()
            is_parcacigi = proc.num_threads()

            # Açık dosya sayısı
            try:
                acik_dosyalar = len(proc.open_files())
            except (psutil.AccessDenied, Exception):
                acik_dosyalar = "Erişim kısıtlı"

        kritik, sebep = islem_kritik_mi(pid, ad)
        koruma_metni = (
            f"{rozet_kritik()} {sebep}" if kritik else f"{rozet_tamam()} Standart süreç (Sonlandırılabilir)"
        )

        anahtar_deger_yazdir(
            [
                ("İşlem Kimliği (PID)", pid),
                ("Üst Süreç (PPID)", ppid),
                ("İşlem Adı", ad),
                ("Çalıştıran Kullanıcı", kullanici),
                ("Durum", durum),
                ("Başlangıç Zamanı", olusturulma),
                ("CPU Kullanımı", f"%{cpu_yuzde:.1f}"),
                ("RAM Kullanımı", f"%{ram_yuzde:.1f} ({bayt_bicimlendir(bellek.rss)})"),
                ("Sanal Bellek (VMS)", bayt_bicimlendir(bellek.vms)),
                ("İş Parçacığı (Threads)", is_parcacigi),
                ("Açık Dosyalar", acik_dosyalar),
                ("Tam Komut Satırı", komut[:80]),
                ("Koruma Durumu", koruma_metni),
            ]
        )
        return 0
    except Exception as e:
        print(f"{rozet_hata()} İşlem detayları alınamadı: {e}")
        return 1


def islemi_sonlandir(pid: int, zorla: bool = False) -> int:
    """Bir süreci güvenlik kontrollerinden geçirerek ve onay alarak sonlandırır."""
    db = get_database()
    try:
        proc = psutil.Process(pid)
        ad = proc.name()
    except psutil.NoSuchProcess:
        print(f"{rozet_hata()} PID {pid} mevcut değil.")
        return 1

    # Kritik işlem koruma kontrolü
    kritik, sebep = islem_kritik_mi(pid, ad)
    if kritik:
        print(f"\n{rozet_kritik()} {c_bold('İŞLEM ENGELLENDİ!')}")
        print(f"  {sebep}")
        db.kaydet("İŞLEM", f"islem sonlandir {pid}", "ENGELLENDİ", False, sebep)
        log_uyari(f"Kritik işlem sonlandırma girişimi engellendi: PID {pid} ({ad}) - {sebep}")
        return 1

    print(f"\nSonlandırılacak Süreç: {c_bold(ad)} (PID: {pid})")
    onay = kullanici_onayi_al(
        f"'{ad}' (PID: {pid}) işlemini sonlandırmak istediğinize emin misiniz?",
        varsayilan=False,
    )
    if not onay:
        print(f"{rozet_uyari()} İşlem kullanıcı tarafından iptal edildi.")
        db.kaydet("İŞLEM", f"islem sonlandir {pid}", "İPTAL_EDİLDİ", False, "Kullanıcı vazgeçti.")
        return 0

    try:
        if zorla:
            proc.kill()
        else:
            proc.terminate()

        # Sürecin durmasını bekle
        gone, alive = psutil.wait_procs([proc], timeout=3)
        if alive:
            print(f"{rozet_uyari()} İşlem SIGTERM ile kapanmadı. Zorla kapatma (SIGKILL) gerekiyor.")
            zorla_onay = kullanici_onayi_al("Zorla sonlandırılsın mı (SIGKILL)?", varsayilan=False)
            if zorla_onay:
                for p in alive:
                    p.kill()
                psutil.wait_procs(alive, timeout=2)

        print(f"{rozet_tamam()} PID {pid} ({ad}) süreci başarıyla sonlandırıldı.")
        db.kaydet("İŞLEM", f"islem sonlandir {pid}", "BAŞARILI", True, f"{ad} sonlandırıldı.")
        log_bilgi(f"İşlem sonlandırıldı: PID {pid} ({ad})")
        return 0
    except psutil.AccessDenied:
        print(f"{rozet_hata()} Yetki yetersiz. Bu işlemi sonlandırmak için yönetici yetkisi (sudo) gerekebilir.")
        db.kaydet("İŞLEM", f"islem sonlandir {pid}", "BAŞARISIZ", True, "Yetki yetersiz.")
        return 1
    except Exception as e:
        print(f"{rozet_hata()} İşlem sonlandırılırken hata: {e}")
        db.kaydet("İŞLEM", f"islem sonlandir {pid}", "BAŞARISIZ", True, str(e))
        return 1
