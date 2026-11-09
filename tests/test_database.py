"""
KETHUDA SQLite İşlem Geçmişi Birim Testleri
"""

import os
import unittest
import tempfile
from kethuda.core.database import HistoryDatabase


class TestHistoryDatabase(unittest.TestCase):

    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.db_path = os.path.join(self.temp_dir.name, "test_kethuda.db")
        self.db = HistoryDatabase(db_path=self.db_path)

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_kayit_ekleme_ve_listeleme(self):
        kayit_id = self.db.kaydet("TEMİZLİK", "kethuda temizlik", "BAŞARILI", True, "50 MB temizlendi")
        self.assertGreater(kayit_id, 0)

        kayitlar = self.db.listele(limit=10)
        self.assertEqual(len(kayitlar), 1)
        self.assertEqual(kayitlar[0]["islem_turu"], "TEMİZLİK")
        self.assertEqual(kayitlar[0]["sonuc"], "BAŞARILI")
        self.assertEqual(kayitlar[0]["kullanici_onayi"], 1)

    def test_filtreleme_ve_istatistikler(self):
        self.db.kaydet("İŞLEM", "islem sonlandir 9999", "BAŞARISIZ", True, "Hata")
        self.db.kaydet("SERVİS", "servis baslat test", "BAŞARILI", True, "")

        islem_kayitlari = self.db.listele(islem_turu="İŞLEM")
        self.assertEqual(len(islem_kayitlari), 1)
        self.assertEqual(islem_kayitlari[0]["islem_turu"], "İŞLEM")

        stats = self.db.istatistikler()
        self.assertEqual(stats["toplam_kayit"], 2)
        self.assertEqual(stats["basarili"], 1)
        self.assertEqual(stats["hatali"], 1)

    def test_gecmis_temizleme(self):
        self.db.kaydet("TEMİZLİK", "komut", "BAŞARILI", True)
        self.assertTrue(self.db.temizle())
        self.assertEqual(len(self.db.listele()), 0)


if __name__ == "__main__":
    unittest.main()
