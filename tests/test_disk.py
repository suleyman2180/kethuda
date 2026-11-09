"""
KETHUDA Disk ve Temizlik Modülleri Birim Testleri
"""

import os
import unittest
import tempfile
from pathlib import Path
from kethuda.modules.disk import disk_bolumlerini_al, buyuk_dosyalari_bul
from kethuda.modules.cleanup import temizlik_alanlarini_analiz_et, _dizin_boyutu_hesapla
from kethuda.interface.output import bayt_bicimlendir, sure_bicimlendir, cubuk


class TestDiskAndCleanup(unittest.TestCase):

    def test_bayt_bicimlendir(self):
        self.assertEqual(bayt_bicimlendir(500), "500.0 B")
        self.assertEqual(bayt_bicimlendir(1024), "1.0 KB")
        self.assertEqual(bayt_bicimlendir(1024 * 1024 * 5), "5.00 MB")
        self.assertEqual(bayt_bicimlendir(1024 * 1024 * 1024 * 2.5), "2.50 GB")

    def test_sure_bicimlendir(self):
        self.assertIn("30 sn", sure_bicimlendir(30))
        self.assertIn("1 dk", sure_bicimlendir(90))
        self.assertIn("1 saat", sure_bicimlendir(3665))
        self.assertIn("1 gün", sure_bicimlendir(90000))

    def test_cubuk(self):
        bar = cubuk(50, genislik=10)
        self.assertIn("50.0%", bar)

    def test_disk_bolumleri_al(self):
        bolumler = disk_bolumlerini_al()
        self.assertIsInstance(bolumler, list)
        if bolumler:
            b = bolumler[0]
            self.assertIn("aygit", b)
            self.assertIn("baglanti", b)
            self.assertIn("toplam", b)

    def test_dizin_boyutu_hesapla(self):
        with tempfile.TemporaryDirectory() as tmp:
            test_file = Path(tmp) / "test.txt"
            test_file.write_text("A" * 1024)
            sayi, boyut = _dizin_boyutu_hesapla(Path(tmp))
            self.assertEqual(sayi, 1)
            self.assertEqual(boyut, 1024)

    def test_temizlik_alanlari_analizi(self):
        alanlar = temizlik_alanlarini_analiz_et()
        self.assertIsInstance(alanlar, list)
        self.assertGreater(len(alanlar), 0)
        for a in alanlar:
            self.assertIn("id", a)
            self.assertIn("ad", a)
            self.assertIn("sayi", a)
            self.assertIn("boyut", a)


if __name__ == "__main__":
    unittest.main()
