"""
KETHUDA Sistem Kontrolü Modülü
'kethuda kontrol' komutu ile tek adımda CPU, RAM, Disk, Servisler ve Paketleri denetler.
Genel bir sistem sağlık raporu üretir.
"""

import os
import psutil
from kethuda.config import get_config
from kethuda.core.system_info import (
    cpu_durumu,
    bellek_durumu,
    kok_disk_durumu,
    genel_sistem_ozeti,
)
from kethuda.modules.disk import disk_bolumlerini_al
from kethuda.core.permissions import guvenli_komut_calistir
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
from kethuda.interface.colors import c_bold, c_white, c_green, c_yellow, c_red, c_dim


def sistem_kontrolu_yap() -> int:
    """Tüm temel sistem metriklerini denetler ve sonuç raporu sunar."""
    baslik_yazdir("GENEL SİSTEM KONTROL VE SAĞLIK RAPORU")
    cfg = get_config()
    disk_esigi = float(cfg.getir("disk_uyari_yuzdesi", 85))

    denetim_sonuclari = []
    uyari_sayisi = 0
    kritik_sayisi = 0

    # 1. CPU Kontrolü
    cpu = cpu_durumu()
    cpu_yuzde = cpu["toplam_yuzde"]
    if cpu_yuzde >= 90:
        cpu_durum = rozet_kritik()
        cpu_mesaj = f"İşlemci yükü aşırı yüksek (%{cpu_yuzde:.1f})"
        kritik_sayisi += 1
    elif cpu_yuzde >= 75:
        cpu_durum = rozet_uyari()
        cpu_mesaj = f"İşlemci yükü yüksek (%{cpu_yuzde:.1f})"
        uyari_sayisi += 1
    else:
        cpu_durum = rozet_tamam()
        cpu_mesaj = f"Normal (%{cpu_yuzde:.1f})"
    denetim_sonuclari.append(["İşlemci (CPU)", cpu_durum, cpu_mesaj])

    # 2. RAM Kontrolü
    mem = bellek_durumu()
    ram_yuzde = mem["yuzde"]
    if ram_yuzde >= 90:
        ram_durum = rozet_kritik()
        ram_mesaj = f"Kritik seviyede RAM kullanımı (%{ram_yuzde:.1f})"
        kritik_sayisi += 1
    elif ram_yuzde >= 80:
        ram_durum = rozet_uyari()
        ram_mesaj = f"RAM kullanımı yüksek (%{ram_yuzde:.1f})"
        uyari_sayisi += 1
    else:
        ram_durum = rozet_tamam()
        ram_mesaj = f"Yeterli boş bellek ({bayt_bicimlendir(mem['kullanilabilir'])})"
    denetim_sonuclari.append(["Bellek (RAM)", ram_durum, ram_mesaj])

    # 3. Disk Doluluk Kontrolü
    bolumler = disk_bolumlerini_al()
    disk_sorunlu = False
    for b in bolumler:
        if b["yuzde"] >= 90:
            denetim_sonuclari.append(
                [f"Disk ({b['baglanti']})", rozet_kritik(), f"Aşırı doluluk (%{b['yuzde']:.1f})"]
            )
            kritik_sayisi += 1
            disk_sorunlu = True
        elif b["yuzde"] >= disk_esigi:
            denetim_sonuclari.append(
                [f"Disk ({b['baglanti']})", rozet_uyari(), f"Doluluk eşiği aşıldı (%{b['yuzde']:.1f})"]
            )
            uyari_sayisi += 1
            disk_sorunlu = True
    if not disk_sorunlu:
        denetim_sonuclari.append(["Disk Bölümleri", rozet_tamam(), "Tüm bölümler güvenli aralıkta"])

    # 4. Başarısız (Failed) Servisler Kontrolü
    kod, out, _ = guvenli_komut_calistir(
        ["systemctl", "--failed", "--no-legend", "--no-pager"]
    )
    failed_servisler = [l for l in out.strip().splitlines() if l.strip()]
    if failed_servisler:
        denetim_sonuclari.append(
            ["Sistem Servisleri", rozet_uyari(), f"{len(failed_servisler)} servis başarısız (failed) durumda"]
        )
        uyari_sayisi += 1
    else:
        denetim_sonuclari.append(["Sistem Servisleri", rozet_tamam(), "Başarısız servis bulunamadı"])

    # 5. Güncellenebilir Paket Kontrolü
    kod, apt_out, _ = guvenli_komut_calistir(["apt", "list", "--upgradable"])
    upgradables = [
        l for l in apt_out.strip().splitlines()
        if l and not l.startswith("Listing...")
    ]
    if upgradables:
        denetim_sonuclari.append(
            ["Paket Güncellemeleri", rozet_uyari(), f"{len(upgradables)} paket güncellenmeyi bekliyor"]
        )
        uyari_sayisi += 1
    else:
        denetim_sonuclari.append(["Paket Güncellemeleri", rozet_tamam(), "Tüm sistem paketleri güncel"])

    # Tabloyu bas
    tablo_yazdir(["Bileşen", "Durum", "Denetim Sonucu"], denetim_sonuclari, ["sol", "orta", "sol"])

    # Genel Sonuç Değerlendirmesi
    alt_baslik_yazdir("Genel Değerlendirme")
    if kritik_sayisi > 0:
        print(f"  {rozet_kritik()} {c_bold(c_red(f'Sistemde {kritik_sayisi} kritik problem tespit edildi! Lütfen acil müdahale edin.'))}")
    elif uyari_sayisi > 0:
        print(f"  {rozet_uyari()} {c_bold(c_yellow(f'Sistem genel olarak çalışır durumda ancak {uyari_sayisi} uyarı dikkat gerektiriyor.'))}")
    else:
        print(f"  {rozet_tamam()} {c_bold(c_green('Tebrikler! Sistem son derece sağlıklı durumda, hiçbir sorun tespit edilmedi.'))}")

    return 0
