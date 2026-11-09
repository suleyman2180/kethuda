"""
KETHUDA Komut Yönlendirici Birim Testleri
"""

import unittest
from kethuda.core.command_router import CommandRouter, turkce_normalize


class TestCommandRouter(unittest.TestCase):

    def test_turkce_normalize(self):
        self.assertEqual(turkce_normalize("İŞLEM"), "islem")
        self.assertEqual(turkce_normalize("Geçmiş"), "gecmis")
        self.assertEqual(turkce_normalize("yardım"), "yardim")
        self.assertEqual(turkce_normalize("SÜRÜM"), "surum")
        self.assertEqual(turkce_normalize("çıkış"), "cikis")
        self.assertEqual(turkce_normalize("güncelle"), "guncelle")
        self.assertEqual(turkce_normalize("devre-dışı"), "devre-disi")

    def test_router_bos_arguman_yardim_doner(self):
        kod = CommandRouter.calistir([])
        self.assertEqual(kod, 0)

    def test_router_surum(self):
        kod = CommandRouter.calistir(["surum"])
        self.assertEqual(kod, 0)

    def test_router_yardim(self):
        kod = CommandRouter.calistir(["yardim"])
        self.assertEqual(kod, 0)

    def test_router_gecersiz_komut(self):
        kod = CommandRouter.calistir(["olmayan_komut_xyz"])
        self.assertEqual(kod, 1)

    def test_router_turkce_karakterli_komutlar(self):
        self.assertEqual(CommandRouter.calistir(["sürüm"]), 0)
        self.assertEqual(CommandRouter.calistir(["yardım"]), 0)


if __name__ == "__main__":
    unittest.main()
