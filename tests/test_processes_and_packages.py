"""
KETHUDA İşlem ve Paket Yönetimi Birim Testleri
"""

import os
import unittest
from kethuda.modules.processes import islem_listesi_al
from kethuda.modules.packages import _paket_adi_gecerli_mi


class TestProcessesAndPackages(unittest.TestCase):

    def test_islem_listesi_al(self):
        islemler = islem_listesi_al(sirala="cpu", limit=5)
        self.assertIsInstance(islemler, list)
        self.assertGreater(len(islemler), 0)
        p = islemler[0]
        self.assertIn("pid", p)
        self.assertIn("ad", p)
        self.assertIn("cpu", p)
        self.assertIn("ram", p)

    def test_paket_adi_dogrulama(self):
        self.assertTrue(_paket_adi_gecerli_mi("python3"))
        self.assertTrue(_paket_adi_gecerli_mi("libssl-dev"))
        self.assertTrue(_paket_adi_gecerli_mi("g++"))
        self.assertTrue(_paket_adi_gecerli_mi("linux-headers-generic"))

        # Komut enjeksiyonu engelleme testleri
        self.assertFalse(_paket_adi_gecerli_mi("python; rm -rf /"))
        self.assertFalse(_paket_adi_gecerli_mi("paket | ls"))
        self.assertFalse(_paket_adi_gecerli_mi("paket & touch test"))
        self.assertFalse(_paket_adi_gecerli_mi("`whoami`"))
        self.assertFalse(_paket_adi_gecerli_mi("$(reboot)"))


if __name__ == "__main__":
    unittest.main()
