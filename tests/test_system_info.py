"""
KETHUDA Sistem Bilgi Toplayıcı Birim Testleri
"""

import unittest
from kethuda.core.system_info import (
    os_dagitim_bilgisi,
    cpu_modeli,
    sistem_calisma_suresi,
    cpu_durumu,
    bellek_durumu,
    kok_disk_durumu,
    genel_sistem_ozeti,
)


class TestSystemInfo(unittest.TestCase):

    def test_os_dagitim_bilgisi(self):
        info = os_dagitim_bilgisi()
        self.assertIsInstance(info, dict)
        self.assertIn("ad", info)
        self.assertIn("surum", info)

    def test_cpu_modeli(self):
        model = cpu_modeli()
        self.assertIsInstance(model, str)
        self.assertGreater(len(model), 0)

    def test_sistem_calisma_suresi(self):
        uptime = sistem_calisma_suresi()
        self.assertIsInstance(uptime, float)
        self.assertGreaterEqual(uptime, 0.0)

    def test_cpu_durumu(self):
        cpu = cpu_durumu()
        self.assertIn("model", cpu)
        self.assertIn("toplam_yuzde", cpu)
        self.assertIn("fiziksel_cekirdek", cpu)
        self.assertGreaterEqual(cpu["fiziksel_cekirdek"], 1)

    def test_bellek_durumu(self):
        mem = bellek_durumu()
        self.assertIn("toplam", mem)
        self.assertIn("kullanilan", mem)
        self.assertIn("kullanilabilir", mem)
        self.assertIn("yuzde", mem)
        self.assertGreater(mem["toplam"], 0)

    def test_kok_disk_durumu(self):
        disk = kok_disk_durumu()
        self.assertIn("toplam", disk)
        self.assertIn("kullanilan", disk)
        self.assertIn("bos", disk)
        self.assertEqual(disk["baglanti_noktasi"], "/")

    def test_genel_sistem_ozeti(self):
        ozet = genel_sistem_ozeti()
        self.assertIn("bilgisayar_adi", ozet)
        self.assertIn("kullanici", ozet)
        self.assertIn("cpu", ozet)
        self.assertIn("bellek", ozet)
        self.assertIn("disk", ozet)


if __name__ == "__main__":
    unittest.main()
