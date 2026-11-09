"""
KETHUDA İşlem Geçmişi Modülü
Sistemde yapılan önceki işlemleri SQLite veritabanından okur, listeler ve yönetir.
"""

from typing import Optional
from kethuda.core.database import get_database
from kethuda.core.permissions import kullanici_onayi_al
from kethuda.interface.output import (
    baslik_yazdir,
    alt_baslik_yazdir,
    tablo_yazdir,
    rozet_tamam,
    rozet_uyari,
    rozet_hata,
    rozet_bilgi,
)
from kethuda.interface.colors import c_bold, c_green, c_yellow, c_red, c_dim


def gecmisi_listele(limit: int = 25, islem_turu: Optional[str] = None) -> int:
    """Geçmiş işlemleri listeler."""
    db = get_database()
    baslik_yazdir(
        f"İŞLEM GEÇMİŞİ (Son {limit} Kayıt" + (f" - Tür: {islem_turu})" if islem_turu else ")")
    )

    kayitlar = db.listele(limit=limit, islem_turu=islem_turu)
    if not kayitlar:
        print(f"{rozet_bilgi()} Henüz kaydedilmiş bir işlem geçmişi bulunmuyor.")
        return 0

    satirlar = []
    for k in kayitlar:
        sonuc = k["sonuc"]
        if sonuc == "BAŞARILI":
            durum_rozet = rozet_tamam()
        elif sonuc == "İPTAL_EDİLDİ":
            durum_rozet = rozet_uyari()
        else:
            durum_rozet = rozet_hata()

        onay_metni = "Evet" if k["kullanici_onayi"] else "Hayır"
        satirlar.append(
            [
                str(k["id"]),
                k["tarih"],
                k["islem_turu"],
                k["komut"][:30],
                durum_rozet,
                onay_metni,
                (k["detay"] or "-")[:25],
            ]
        )

    tablo_yazdir(
        ["No", "Tarih / Saat", "Tür", "Komut", "Sonuç", "Onay", "Detay"],
        satirlar,
        ["sag", "sol", "sol", "sol", "orta", "orta", "sol"],
    )

    stats = db.istatistikler()
    print(
        f"\n{rozet_bilgi()} Toplam {stats['toplam_kayit']} işlem kaydedildi "
        f"({stats['basarili']} başarılı, {stats['hatali']} hatalı/engellenmiş)."
    )
    print(f"  {c_dim('Geçmişi temizlemek için: kethuda gecmis temizle')}")
    return 0


def gecmisi_temizle() -> int:
    """İşlem geçmişini kullanıcı onayı ile temizler."""
    db = get_database()
    baslik_yazdir("İŞLEM GEÇMİŞİNİ TEMİZLE")

    onay = kullanici_onayi_al("Tüm geçmiş kayıtlarını kalıcı olarak silmek istediğinize emin misiniz?", varsayilan=False)
    if not onay:
        print(f"{rozet_uyari()} Temizleme işlemi iptal edildi.")
        return 0

    basarili = db.temizle()
    if basarili:
        print(f"{rozet_tamam()} İşlem geçmişi başarıyla temizlendi.")
        return 0
    else:
        print(f"{rozet_hata()} İşlem geçmişi temizlenirken hata oluştu.")
        return 1
