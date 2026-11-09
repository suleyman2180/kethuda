"""
KETHUDA Komut Yönlendiricisi (Command Router)
Gelen kullanıcı komutlarını Türkçe karakter desteğiyle ayrıştırır ve ilgili modüllere iletir.
"""

import sys
from typing import List, Optional

# Modüller
from kethuda.modules.status import sistem_durumunu_goster
from kethuda.modules.disk import (
    disk_listesini_goster,
    buyuk_dosyalari_bul,
    buyuk_klasorleri_analiz_et,
    disk_raporu,
)
from kethuda.modules.cleanup import (
    temizlik_onizlemesini_goster,
    temizligi_calistir,
)
from kethuda.modules.processes import (
    islemleri_listele,
    islem_ara,
    islem_detayi_goster,
    islemi_sonlandir,
)
from kethuda.modules.services import (
    servisleri_listele,
    servis_durumu_goster,
    servis_baslat,
    servis_durdur,
    servis_yeniden_baslat,
    etkin_servisleri_listele,
    servis_devre_disi_birak,
)
from kethuda.modules.packages import (
    paketleri_listele,
    paket_ara,
    paket_bilgisi,
    guncellemeleri_kontrol_et,
    paket_guncelle,
    paket_kaldir,
    gereksiz_paketleri_tara,
    apt_onbellegini_goster,
)
from kethuda.modules.control import sistem_kontrolu_yap
from kethuda.modules.doctor import sistem_doktoru_calistir
from kethuda.modules.history import gecmisi_listele, gecmisi_temizle
from kethuda.modules.settings import (
    ayarlari_listele,
    ayar_getir,
    ayar_belirle,
    ayarlari_sifirla,
)
from kethuda.modules.update import guncelleme_kontrolu, yapilandirma_yedekle
from kethuda.modules.help_version import yardim_goster, surum_goster

from kethuda.interface.output import rozet_hata, rozet_uyari
from kethuda.interface.colors import c_bold, c_yellow, c_dim


def turkce_normalize(metin: str) -> str:
    """Türkçe karakterleri ASCII eşdeğerlerine ve küçük harfe dönüştürür."""
    if not metin:
        return ""
    donusum = {
        "I": "i", "İ": "i", "ı": "i",
        "Ş": "s", "ş": "s",
        "Ğ": "g", "ğ": "g",
        "Ü": "u", "ü": "u",
        "Ö": "o", "ö": "o",
        "Ç": "c", "ç": "c",
    }
    sonuc = []
    for char in metin:
        sonuc.append(donusum.get(char, char.lower()))
    return "".join(sonuc)


class CommandRouter:
    """Komutları ayrıştıran ve uygun işlevlere yönlendiren sınıf."""

    @classmethod
    def calistir(cls, args: List[str]) -> int:
        """Verilen komut satırı argüman listesini çalıştırır."""
        if not args:
            return yardim_goster()

        ana_komut = turkce_normalize(args[0])
        alt_args = args[1:]
        alt_komut = turkce_normalize(alt_args[0]) if alt_args else ""

        # 1. DURUM
        if ana_komut == "durum":
            return sistem_durumunu_goster()

        # 2. DİSK
        elif ana_komut == "disk":
            if not alt_komut or alt_komut == "liste":
                return disk_listesini_goster()
            elif alt_komut in ("buyuk-dosyalar", "buyuk_dosyalar"):
                dizin = alt_args[1] if len(alt_args) > 1 else None
                esik = int(alt_args[2]) if len(alt_args) > 2 and alt_args[2].isdigit() else None
                return buyuk_dosyalari_bul(dizin, esik)
            elif alt_komut in ("buyuk-klasorler", "buyuk_klasorler"):
                dizin = alt_args[1] if len(alt_args) > 1 else None
                return buyuk_klasorleri_analiz_et(dizin)
            elif alt_komut == "rapor":
                return disk_raporu()
            else:
                print(f"{rozet_hata()} Geçersiz disk alt komutu: '{alt_args[0]}'")
                print(f"  {c_dim('Kullanılabilir: kethuda disk [liste | buyuk-dosyalar | buyuk-klasorler | rapor]')}")
                return 1

        # 3. TEMİZLİK
        elif ana_komut == "temizlik":
            if not alt_komut or alt_komut in ("analiz", "onizleme"):
                return temizlik_onizlemesini_goster()
            elif alt_komut in ("calistir", "temizle"):
                return temizligi_calistir()
            else:
                print(f"{rozet_hata()} Geçersiz temizlik alt komutu: '{alt_args[0]}'")
                print(f"  {c_dim('Kullanılabilir: kethuda temizlik [analiz | onizleme | calistir]')}")
                return 1

        # 4. İŞLEM (PROCESS)
        elif ana_komut == "islem":
            if not alt_komut or alt_komut == "liste":
                sirala = "cpu"
                if len(alt_args) > 1 and turkce_normalize(alt_args[1]) in ("ram", "bellek"):
                    sirala = "ram"
                return islemleri_listele(sirala=sirala)
            elif alt_komut == "ara":
                if len(alt_args) < 2:
                    print(f"{rozet_hata()} Lütfen aranacak işlem adını belirtin: kethuda islem ara <kelime>")
                    return 1
                return islem_ara(alt_args[1])
            elif alt_komut == "detay":
                if len(alt_args) < 2 or not alt_args[1].isdigit():
                    print(f"{rozet_hata()} Lütfen geçerli bir PID belirtin: kethuda islem detay <pid>")
                    return 1
                return islem_detayi_goster(int(alt_args[1]))
            elif alt_komut in ("sonlandir", "kill", "durdur"):
                if len(alt_args) < 2 or not alt_args[1].isdigit():
                    print(f"{rozet_hata()} Lütfen sonlandırılacak PID'yi belirtin: kethuda islem sonlandir <pid>")
                    return 1
                zorla = len(alt_args) > 2 and alt_args[2] in ("--zorla", "-f", "zorla")
                return islemi_sonlandir(int(alt_args[1]), zorla=zorla)
            else:
                print(f"{rozet_hata()} Geçersiz işlem alt komutu: '{alt_args[0]}'")
                print(f"  {c_dim('Kullanılabilir: kethuda islem [liste | ara <kelime> | detay <pid> | sonlandir <pid>]')}")
                return 1

        # 5. SERVİS
        elif ana_komut == "servis":
            if not alt_komut or alt_komut == "liste":
                sadece_calisanlar = len(alt_args) > 1 and turkce_normalize(alt_args[1]) in ("calisan", "aktif")
                return servisleri_listele(sadece_calisanlar=sadece_calisanlar)
            elif alt_komut == "durum":
                if len(alt_args) < 2:
                    print(f"{rozet_hata()} Lütfen servis adını belirtin: kethuda servis durum <servis_adi>")
                    return 1
                return servis_durumu_goster(alt_args[1])
            elif alt_komut == "baslat":
                if len(alt_args) < 2:
                    print(f"{rozet_hata()} Lütfen servis adını belirtin: kethuda servis baslat <servis_adi>")
                    return 1
                return servis_baslat(alt_args[1])
            elif alt_komut == "durdur":
                if len(alt_args) < 2:
                    print(f"{rozet_hata()} Lütfen servis adını belirtin: kethuda servis durdur <servis_adi>")
                    return 1
                return servis_durdur(alt_args[1])
            elif alt_komut in ("yeniden-baslat", "yeniden_baslat", "restart"):
                if len(alt_args) < 2:
                    print(f"{rozet_hata()} Lütfen servis adını belirtin: kethuda servis yeniden-baslat <servis_adi>")
                    return 1
                return servis_yeniden_baslat(alt_args[1])
            elif alt_komut in ("etkin", "enabled"):
                return etkin_servisleri_listele()
            elif alt_komut in ("devre-disi", "devre_disi", "disable"):
                if len(alt_args) < 2:
                    print(f"{rozet_hata()} Lütfen servis adını belirtin: kethuda servis devre-disi <servis_adi>")
                    return 1
                return servis_devre_disi_birak(alt_args[1])
            else:
                print(f"{rozet_hata()} Geçersiz servis alt komutu: '{alt_args[0]}'")
                print(f"  {c_dim('Kullanılabilir: kethuda servis [liste | durum | baslat | durdur | yeniden-baslat | etkin | devre-disi]')}")
                return 1

        # 6. PAKET
        elif ana_komut == "paket":
            if not alt_komut or alt_komut == "liste":
                return paketleri_listele()
            elif alt_komut == "ara":
                if len(alt_args) < 2:
                    print(f"{rozet_hata()} Lütfen aranacak paketi belirtin: kethuda paket ara <kelime>")
                    return 1
                return paket_ara(alt_args[1])
            elif alt_komut == "bilgi":
                if len(alt_args) < 2:
                    print(f"{rozet_hata()} Lütfen paket adını belirtin: kethuda paket bilgi <paket_adi>")
                    return 1
                return paket_bilgisi(alt_args[1])
            elif alt_komut in ("kontrol", "guncellenebilir"):
                return guncellemeleri_kontrol_et()
            elif alt_komut == "guncelle":
                return paket_guncelle()
            elif alt_komut in ("kaldir", "sil"):
                if len(alt_args) < 2:
                    print(f"{rozet_hata()} Lütfen kaldırılacak paketi belirtin: kethuda paket kaldir <paket_adi>")
                    return 1
                return paket_kaldir(alt_args[1])
            elif alt_komut in ("gereksiz", "artik"):
                return gereksiz_paketleri_tara()
            elif alt_komut in ("onbellek", "cache"):
                return apt_onbellegini_goster()
            else:
                print(f"{rozet_hata()} Geçersiz paket alt komutu: '{alt_args[0]}'")
                print(f"  {c_dim('Kullanılabilir: kethuda paket [liste | ara | bilgi | kontrol | guncelle | kaldir | gereksiz | onbellek]')}")
                return 1

        # 7. KONTROL
        elif ana_komut == "kontrol":
            return sistem_kontrolu_yap()

        # 8. DOKTOR
        elif ana_komut == "doktor":
            return sistem_doktoru_calistir()

        # 9. GEÇMİŞ
        elif ana_komut == "gecmis":
            if not alt_komut or alt_komut == "liste":
                tur = alt_args[1] if len(alt_args) > 1 else None
                return gecmisi_listele(limit=30, islem_turu=tur)
            elif alt_komut in ("temizle", "sil"):
                return gecmisi_temizle()
            else:
                print(f"{rozet_hata()} Geçersiz geçmiş alt komutu: '{alt_args[0]}'")
                print(f"  {c_dim('Kullanılabilir: kethuda gecmis [liste | temizle]')}")
                return 1

        # 10. AYAR
        elif ana_komut == "ayar":
            if not alt_komut or alt_komut == "liste":
                return ayarlari_listele()
            elif alt_komut == "getir":
                if len(alt_args) < 2:
                    print(f"{rozet_hata()} Lütfen ayar anahtarını belirtin: kethuda ayar getir <anahtar>")
                    return 1
                return ayar_getir(alt_args[1])
            elif alt_komut in ("belirle", "set", "degistir"):
                if len(alt_args) < 3:
                    print(f"{rozet_hata()} Lütfen anahtar ve değeri belirtin: kethuda ayar belirle <anahtar> <değer>")
                    return 1
                return ayar_belirle(alt_args[1], alt_args[2])
            elif alt_komut in ("sifirla", "reset"):
                return ayarlari_sifirla()
            else:
                print(f"{rozet_hata()} Geçersiz ayar alt komutu: '{alt_args[0]}'")
                print(f"  {c_dim('Kullanılabilir: kethuda ayar [liste | getir <anahtar> | belirle <anahtar> <değer> | sifirla]')}")
                return 1

        # 11. GÜNCELLE
        elif ana_komut == "guncelle":
            if not alt_komut or alt_komut == "kontrol":
                return guncelleme_kontrolu()
            elif alt_komut == "yedekle":
                return yapilandirma_yedekle()
            else:
                print(f"{rozet_hata()} Geçersiz güncelle alt komutu: '{alt_args[0]}'")
                print(f"  {c_dim('Kullanılabilir: kethuda guncelle [kontrol | yedekle]')}")
                return 1

        # 12. YARDIM
        elif ana_komut in ("yardim", "help", "-h", "--help"):
            return yardim_goster()

        # 13. SÜRÜM
        elif ana_komut in ("surum", "version", "-v", "--version"):
            return surum_goster()

        else:
            print(f"{rozet_hata()} Bilinmeyen komut: '{args[0]}'")
            print(f"  {c_dim('Kullanılabilir tüm komutları görmek için:')} {c_bold('kethuda yardim')}")
            return 1
