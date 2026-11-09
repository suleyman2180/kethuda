"""
KETHUDA Sistem Durumu Modülü
'kethuda durum' komutu için ayrıntılı ve gerçek zamanlı sistem analizi sunar.
"""

import os
import psutil
from kethuda.core.system_info import (
    os_dagitim_bilgisi,
    cpu_modeli,
    sistem_calisma_suresi,
    cpu_durumu,
    bellek_durumu,
    kok_disk_durumu,
    genel_sistem_ozeti,
)
from kethuda.interface.output import (
    baslik_yazdir,
    alt_baslik_yazdir,
    tablo_yazdir,
    anahtar_deger_yazdir,
    bayt_bicimlendir,
    sure_bicimlendir,
    cubuk,
    rozet_tamam,
    rozet_uyari,
    rozet_kritik,
)
from kethuda.interface.colors import (
    c_bold,
    c_cyan,
    c_bright_cyan,
    c_white,
    c_yellow,
    c_green,
    c_dim,
)


def sistem_durumunu_goster() -> int:
    """Gerçek zamanlı sistem durumunu ekrana basar."""
    ozet = genel_sistem_ozeti()
    cpu = ozet["cpu"]
    mem = ozet["bellek"]
    disk = ozet["disk"]

    baslik_yazdir("KETHUDA SİSTEM DURUMU")

    # Donanım ve Kimlik Bilgileri
    alt_baslik_yazdir("Sistem ve Donanım Bilgileri")
    anahtar_deger_yazdir(
        [
            ("Bilgisayar Adı", ozet["bilgisayar_adi"]),
            ("Geçerli Kullanıcı", ozet["kullanici"]),
            ("İşletim Sistemi", ozet["dagitim"]),
            ("Kernel Sürümü", ozet["kernel"]),
            ("Mimari", ozet["mimari"]),
            ("Çalışma Süresi (Uptime)", sure_bicimlendir(ozet["uptime_saniye"])),
            ("İşlemci Modeli", cpu["model"]),
            (
                "Çekirdek Sayısı",
                f"{cpu['fiziksel_cekirdek']} Fiziksel, {cpu['mantiksal_cekirdek']} Mantıksal",
            ),
        ]
    )

    # İşlemci Kullanımı
    alt_baslik_yazdir("İşlemci (CPU) Kullanım Durumu")
    print(f"  Toplam Kullanım: {cubuk(cpu['toplam_yuzde'])}")
    if cpu["cekirdek_yuzdeleri"]:
        cekirdek_satirlari = []
        for i, yuzde in enumerate(cpu["cekirdek_yuzdeleri"]):
            cekirdek_satirlari.append([f"Çekirdek #{i+1}", f"{yuzde:.1f}%", cubuk(yuzde, 16)])
        tablo_yazdir(
            ["İşlemci Çekirdeği", "Kullanım", "Grafik"],
            cekirdek_satirlari,
            ["sol", "sag", "sol"],
        )

    # Bellek Kullanımı
    alt_baslik_yazdir("Bellek (RAM & Swap) Durumu")
    ram_tablo = [
        [
            "Fiziksel RAM",
            bayt_bicimlendir(mem["toplam"]),
            bayt_bicimlendir(mem["kullanilan"]),
            bayt_bicimlendir(mem["kullanilabilir"]),
            f"{mem['yuzde']:.1f}%",
            cubuk(mem["yuzde"], 16),
        ],
        [
            "Takas (Swap)",
            bayt_bicimlendir(mem["swap_toplam"]),
            bayt_bicimlendir(mem["swap_kullanilan"]),
            bayt_bicimlendir(mem["swap_bos"]),
            f"{mem['swap_yuzde']:.1f}%",
            cubuk(mem["swap_yuzde"], 16),
        ],
    ]
    tablo_yazdir(
        ["Bellek Türü", "Toplam", "Kullanılan", "Kullanılabilir", "Yüzde", "Durum"],
        ram_tablo,
        ["sol", "sag", "sag", "sag", "sag", "sol"],
    )

    # Temel Disk Durumu
    alt_baslik_yazdir("Kök Disk (/) Durumu")
    disk_tablo = [
        [
            disk["baglanti_noktasi"],
            bayt_bicimlendir(disk["toplam"]),
            bayt_bicimlendir(disk["kullanilan"]),
            bayt_bicimlendir(disk["bos"]),
            f"{disk['yuzde']:.1f}%",
            cubuk(disk["yuzde"], 16),
        ]
    ]
    tablo_yazdir(
        ["Bağlantı Noktası", "Toplam Alan", "Kullanılan", "Boş Alan", "Doluluk", "Durum"],
        disk_tablo,
        ["sol", "sag", "sag", "sag", "sag", "sol"],
    )

    return 0
