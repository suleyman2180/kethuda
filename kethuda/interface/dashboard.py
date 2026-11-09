"""
KETHUDA Başlangıç Paneli (Dashboard)
Açılış ekranında kısa sistem durumunu ve kullanılabilir komutları gösterir.
"""

from kethuda.core.system_info import genel_sistem_ozeti
from kethuda.interface.colors import (
    c_bold,
    c_cyan,
    c_bright_cyan,
    c_green,
    c_white,
    c_gray,
    c_dim,
    c_yellow,
)
from kethuda.interface.output import bayt_bicimlendir, sure_bicimlendir, cubuk


def sistem_ozet_paneli() -> None:
    """Açılışta gösterilen şık sistem özet kartı."""
    ozet = genel_sistem_ozeti()
    cpu = ozet["cpu"]
    mem = ozet["bellek"]
    disk = ozet["disk"]
    yuk = ozet["yuk_ortalama"]

    print(f"  {c_bold(c_white('SİSTEM ÖZETİ'))} {c_gray('──────────────────────────────────────────────────────')}")
    print(
        f"  {c_cyan('Bilgisayar')}: {c_bold(ozet['bilgisayar_adi'])}  │  "
        f"{c_cyan('Kullanıcı')}: {c_bold(ozet['kullanici'])}  │  "
        f"{c_cyan('İşletim Sistemi')}: {ozet['dagitim']}"
    )
    print(
        f"  {c_cyan('Kernel')}: {ozet['kernel']} ({ozet['mimari']})  │  "
        f"{c_cyan('Çalışma Süresi')}: {sure_bicimlendir(ozet['uptime_saniye'])}"
    )
    print(
        f"  {c_cyan('İşlemci')}: {cpu['model']} ({cpu['mantiksal_cekirdek']} çekirdek)"
    )
    print(
        f"  {c_cyan('Sistem Yükü (1/5/15 dk)')}: {yuk[0]:.2f}, {yuk[1]:.2f}, {yuk[2]:.2f}"
    )
    print(f"  {c_gray('─' * 54)}")
    print(f"  {c_bold('CPU Kullanımı')} : {cubuk(cpu['toplam_yuzde'])}")
    print(
        f"  {c_bold('RAM Kullanımı')} : {cubuk(mem['yuzde'])}  "
        f"({bayt_bicimlendir(mem['kullanilan'])} / {bayt_bicimlendir(mem['toplam'])})"
    )
    print(
        f"  {c_bold('Disk (Kök /)')} : {cubuk(disk['yuzde'])}  "
        f"({bayt_bicimlendir(disk['kullanilan'])} / {bayt_bicimlendir(disk['toplam'])})"
    )
    print(f"  {c_gray('──────────────────────────────────────────────────────')}\n")


def hizli_komut_listesi() -> None:
    """Açılış ekranında gösterilen temel komut ipuçları."""
    print(f"  {c_bold(c_white('TEMEL KOMUTLAR:'))}")
    komutlar = [
        ("durum", "Gerçek zamanlı sistem durumu (CPU, RAM, Disk, Donanım)"),
        ("disk", "Bölümler, büyük dosyalar ve depolama kullanım analizi"),
        ("temizlik", "Önbellek, geçici dosyalar ve çöp kutusu temizlik analizi"),
        ("islem liste", "Çalışan süreçleri izleme, arama ve güvenli sonlandırma"),
        ("servis liste", "systemd servislerini listeleme ve durum kontrolü"),
        ("paket kontrol", "Kurulu paketler ve APT güncellemelerini denetleme"),
        ("kontrol", "Tek komutla genel sistem denetim raporu"),
        ("doktor", "KETHUDA ve sistem bileşenleri sağlık kontrolü"),
        ("gecmis", "Yapılan işlemlerin geçmiş kayıtları (SQLite)"),
        ("ayar", "Yapılandırma ayarlarını görüntüleme ve değiştirme"),
        ("yardim", "Kapsamlı yardım kılavuzu ve komut sözlüğü"),
        ("cikis", "Etkileşimli kabuktan çıkış yap"),
    ]
    for cmd, desc in komutlar:
        print(f"    {c_bold(c_bright_cyan(f'{cmd:<14}'))} {c_dim(desc)}")
    print()
