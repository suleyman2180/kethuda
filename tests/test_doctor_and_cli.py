"""
KETHUDA Doktor ve CLI Entegrasyon Testleri
"""

import unittest
from kethuda.cli import cli_calistir
from kethuda.modules.doctor import sistem_doktoru_calistir
from kethuda.modules.control import sistem_kontrolu_yap
from kethuda.modules.status import sistem_durumunu_goster


class TestDoctorAndCli(unittest.TestCase):

    def test_sistem_durumu_calistir(self):
        kod = sistem_durumunu_goster()
        self.assertEqual(kod, 0)

    def test_sistem_kontrolu_yap(self):
        kod = sistem_kontrolu_yap()
        self.assertEqual(kod, 0)

    def test_sistem_doktoru_calistir(self):
        kod = sistem_doktoru_calistir()
        self.assertEqual(kod, 0)

    def test_cli_calistir_surum(self):
        kod = cli_calistir(["surum"])
        self.assertEqual(kod, 0)

    def test_cli_calistir_yardim(self):
        kod = cli_calistir(["yardim"])
        self.assertEqual(kod, 0)


if __name__ == "__main__":
    unittest.main()
