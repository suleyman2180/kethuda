"""
KETHUDA Güvenlik ve İzin Birim Testleri
"""

import os
import unittest
from kethuda.core.permissions import (
    islem_kritik_mi,
    servis_kritik_mi,
    guvenli_komut_calistir,
    KRITIK_SERVISLER,
    KRITIK_PIDLER,
)


class TestPermissions(unittest.TestCase):

    def test_kritik_pid_korumasi(self):
        kritik, sebep = islem_kritik_mi(1, "systemd")
        self.assertTrue(kritik)
        self.assertIn("sistem çekirdeği", sebep.lower())

    def test_kethuda_kendi_pid_korumasi(self):
        mevcut_pid = os.getpid()
        kritik, sebep = islem_kritik_mi(mevcut_pid, "python3")
        self.assertTrue(kritik)
        self.assertIn("kendi", sebep.lower())

    def test_standart_islem_korunmaz(self):
        kritik, _ = islem_kritik_mi(987654, "benim_uygulamam")
        self.assertFalse(kritik)

    def test_kritik_servis_korumasi(self):
        for s in ("dbus", "systemd-journald", "ssh", "NetworkManager"):
            kritik, _ = servis_kritik_mi(s)
            self.assertTrue(kritik, f"{s} kritik olarak korunmalıdır.")

        kritik_degil, _ = servis_kritik_mi("ozel-servisim.service")
        self.assertFalse(kritik_degil)

    def test_guvenli_komut_calistir(self):
        kod, stdout, stderr = guvenli_komut_calistir(["echo", "kethuda_test"])
        self.assertEqual(kod, 0)
        self.assertEqual(stdout.strip(), "kethuda_test")

    def test_olmayan_komut_calistir(self):
        kod, _, hata = guvenli_komut_calistir(["olmayan_komut_123456789"])
        self.assertEqual(kod, -3)
        self.assertIn("bulunamadı", hata)


if __name__ == "__main__":
    unittest.main()
