"""
KETHUDA Yapılandırma Birim Testleri
"""

import os
import unittest
import tempfile
from pathlib import Path
from kethuda.config import ConfigManager, VARSAYILAN_AYARLAR


class TestConfigManager(unittest.TestCase):

    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.config_path = os.path.join(self.temp_dir.name, "config.json")
        self.cfg = ConfigManager(custom_path=self.config_path)

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_varsayilan_ayarlar_yuklenir(self):
        for k, v in VARSAYILAN_AYARLAR.items():
            self.assertEqual(self.cfg.getir(k), v)

    def test_ayar_degistirme_ve_kalicilik(self):
        self.assertTrue(self.cfg.belirle("renkler", False))
        self.assertFalse(self.cfg.getir("renkler"))

        # Yeniden yükle ve kalıcılığı test et
        yeni_cfg = ConfigManager(custom_path=self.config_path)
        self.assertFalse(yeni_cfg.getir("renkler"))

    def test_sayisal_ayar_dogrulama(self):
        self.assertTrue(self.cfg.belirle("buyuk_dosya_esigi_mb", "100"))
        self.assertEqual(self.cfg.getir("buyuk_dosya_esigi_mb"), 100)

        # Geçersiz sayısal değer
        self.assertFalse(self.cfg.belirle("buyuk_dosya_esigi_mb", "gecersiz_sayi"))

    def test_gunluk_seviyesi_dogrulama(self):
        self.assertTrue(self.cfg.belirle("gunluk_seviyesi", "DEBUG"))
        self.assertEqual(self.cfg.getir("gunluk_seviyesi"), "DEBUG")
        self.assertFalse(self.cfg.belirle("gunluk_seviyesi", "YANLIS_SEVIYE"))

    def test_ayarlari_sifirla(self):
        self.cfg.belirle("disk_uyari_yuzdesi", 95)
        self.assertEqual(self.cfg.getir("disk_uyari_yuzdesi"), 95)
        self.cfg.sifirla()
        self.assertEqual(self.cfg.getir("disk_uyari_yuzdesi"), VARSAYILAN_AYARLAR["disk_uyari_yuzdesi"])


if __name__ == "__main__":
    unittest.main()
