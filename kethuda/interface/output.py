"""
KETHUDA Çıktı ve Tablo Biçimlendirme Araçları
Terminal ekranında düzenli, hizalı ve renkli gösterim sağlar.
"""

import shutil
from typing import List, Dict, Any, Optional, Sequence
from kethuda.interface.colors import (
    c_bold,
    c_dim,
    c_green,
    c_bright_green,
    c_yellow,
    c_bright_yellow,
    c_red,
    c_bright_red,
    c_cyan,
    c_bright_cyan,
    c_white,
    c_gray,
    ansi_temizle,
)


def rozet_tamam() -> str:
    return c_bold(c_bright_green("[ TAMAM ]"))


def rozet_bilgi() -> str:
    return c_bold(c_bright_cyan("[ BİLGİ ]"))


def rozet_uyari() -> str:
    return c_bold(c_bright_yellow("[ UYARI ]"))


def rozet_hata() -> str:
    return c_bold(c_bright_red("[ HATA  ]"))


def rozet_kritik() -> str:
    return c_bold(c_bright_red("[KRİTİK]"))


def rozet_bekliyor() -> str:
    return c_bold(c_yellow("[İŞLENİYOR]"))


def bayt_bicimlendir(bayt: float) -> str:
    """Bayt değerini okunabilir boyuta dönüştürür (KB, MB, GB, TB)."""
    if bayt < 0:
        return "0 B"
    birimler = ["B", "KB", "MB", "GB", "TB", "PB"]
    deger = float(bayt)
    for birim in birimler:
        if deger < 1024.0 or birim == birimler[-1]:
            if birim in ("B", "KB"):
                return f"{deger:.1f} {birim}"
            return f"{deger:.2f} {birim}"
        deger /= 1024.0
    return f"{deger:.2f} PB"


def sure_bicimlendir(saniye: float) -> str:
    """Saniye cinsinden süreyi gün, saat, dakika cinsinden metne dönüştürür."""
    saniye = int(saniye)
    gunler = saniye // 86400
    kalan = saniye % 86400
    saatler = kalan // 3600
    kalan = kalan % 3600
    dakikalar = kalan // 60
    sn = kalan % 60

    parcalar = []
    if gunler > 0:
        parcalar.append(f"{gunler} gün")
    if saatler > 0 or gunler > 0:
        parcalar.append(f"{saatler} saat")
    if dakikalar > 0 or saatler > 0 or gunler > 0:
        parcalar.append(f"{dakikalar} dk")
    parcalar.append(f"{sn} sn")
    return " ".join(parcalar)


def cubuk(yuzde: float, genislik: int = 24) -> str:
    """Yüzde değerini görsel bir doluluk çubuğuna dönüştürür."""
    yuzde = max(0.0, min(100.0, float(yuzde)))
    dolu = int(round((yuzde / 100.0) * genislik))
    bos = genislik - dolu

    if yuzde >= 90:
        renklendir = c_bright_red
    elif yuzde >= 75:
        renklendir = c_bright_yellow
    else:
        renklendir = c_bright_green

    bar = renklendir("█" * dolu) + c_gray("░" * bos)
    return f"[{bar}] {yuzde:>5.1f}%"


def baslik_yazdir(metin: str, alt_cizgi: str = "─") -> None:
    """Bölüm başlığı yazdırır."""
    cols = shutil.get_terminal_size((80, 24)).columns
    genislik = min(cols, 80)
    cizgi = alt_cizgi * max(10, genislik - len(metin) - 4)
    print(f"\n{c_bold(c_bright_cyan('▶'))} {c_bold(c_white(metin))} {c_dim(cizgi)}")


def alt_baslik_yazdir(metin: str) -> None:
    """Alt başlık yazdırır."""
    print(f"\n{c_bold(c_cyan('●'))} {c_bold(metin)}")


def tablo_yazdir(
    basliklar: Sequence[str],
    satirlar: Sequence[Sequence[Any]],
    hizalar: Optional[Sequence[str]] = None,
) -> None:
    """
    Düzenli, ANSI duyarlı ASCII tablosu oluşturur ve ekrana basar.
    hizalar: her sütun için 'sol', 'sag', 'orta'
    """
    if not basliklar:
        return

    sutun_sayisi = len(basliklar)
    hizalar = list(hizalar) if hizalar else ["sol"] * sutun_sayisi
    if len(hizalar) < sutun_sayisi:
        hizalar.extend(["sol"] * (sutun_sayisi - len(hizalar)))

    # Metin olarak dönüştür ve sütun genişliklerini hesapla
    str_satirlar: List[List[str]] = []
    for row in satirlar:
        str_satirlar.append([str(col) for col in row])

    genislikler = [len(ansi_temizle(b)) for b in basliklar]
    for row in str_satirlar:
        for i, val in enumerate(row):
            if i < sutun_sayisi:
                temiz_uzunluk = len(ansi_temizle(val))
                if temiz_uzunluk > genislikler[i]:
                    genislikler[i] = temiz_uzunluk

    # Sütunları biçimlendir
    def hucre_formatla(metin: str, genislik: int, hiza: str) -> str:
        temiz = ansi_temizle(metin)
        fark = genislik - len(temiz)
        if fark <= 0:
            return metin
        if hiza == "sag":
            return (" " * fark) + metin
        elif hiza == "orta":
            sol = fark // 2
            sag = fark - sol
            return (" " * sol) + metin + (" " * sag)
        else:
            return metin + (" " * fark)

    # Çizgiler
    ust_cizgi = "┌" + "┬".join("─" * (w + 2) for w in genislikler) + "┐"
    ara_cizgi = "├" + "┼".join("─" * (w + 2) for w in genislikler) + "┤"
    alt_cizgi = "└" + "┴".join("─" * (w + 2) for w in genislikler) + "┘"

    print(c_gray(ust_cizgi))

    # Başlık satırı
    baslik_hucreleri = [
        " " + hucre_formatla(c_bold(c_white(b)), genislikler[i], hizalar[i]) + " "
        for i, b in enumerate(basliklar)
    ]
    print(c_gray("│") + c_gray("│").join(baslik_hucreleri) + c_gray("│"))
    print(c_gray(ara_cizgi))

    # Veri satırları
    if not str_satirlar:
        bos_metin = "(Veri bulunamadı)"
        toplam_w = sum(genislikler) + (3 * (sutun_sayisi - 1)) + 2
        pad_sol = max(0, (toplam_w - len(bos_metin)) // 2)
        pad_sag = max(0, toplam_w - len(bos_metin) - pad_sol)
        print(c_gray("│") + (" " * pad_sol) + c_dim(bos_metin) + (" " * pad_sag) + c_gray("│"))
    else:
        for row in str_satirlar:
            hucreler = []
            for i in range(sutun_sayisi):
                val = row[i] if i < len(row) else ""
                hucreler.append(" " + hucre_formatla(val, genislikler[i], hizalar[i]) + " ")
            print(c_gray("│") + c_gray("│").join(hucreler) + c_gray("│"))

    print(c_gray(alt_cizgi))


def anahtar_deger_yazdir(bilgiler: Sequence[tuple], etiket_genislik: int = 24) -> None:
    """Etiket ve Değer çiftlerini düzenli şekilde yazdırır."""
    for etiket, deger in bilgiler:
        etiket_metni = f"{etiket}:"
        temiz_len = len(ansi_temizle(etiket_metni))
        bosluk = max(1, etiket_genislik - temiz_len)
        print(f"  {c_bold(c_cyan(etiket_metni))}{' ' * bosluk}{deger}")
