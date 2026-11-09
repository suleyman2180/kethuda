"""
KETHUDA Güvenlik, İzinler ve Sistem Koruma Modülü
Yıkıcı işlemler için onay mekanizması, kritik servis/süreç koruması ve güvenli subprocess yönetimi sağlar.
"""

import os
import sys
import shutil
import subprocess
from typing import List, Optional, Tuple
from kethuda.config import get_config
from kethuda.interface.colors import c_bold, c_yellow, c_red, c_green, c_bright_red

# Kritik korunan servis adları (küçük harflerle)
KRITIK_SERVISLER = {
    "dbus",
    "dbus.service",
    "systemd-journald",
    "systemd-journald.service",
    "systemd-logind",
    "systemd-logind.service",
    "systemd-udevd",
    "systemd-udevd.service",
    "systemd-resolved",
    "systemd-resolved.service",
    "systemd-networkd",
    "systemd-networkd.service",
    "networkmanager",
    "networkmanager.service",
    "networking",
    "networking.service",
    "ssh",
    "ssh.service",
    "sshd",
    "sshd.service",
    "ufw",
    "ufw.service",
    "login",
    "gdm",
    "lightdm",
    "sddm",
}

# Kritik korunan işlem PID ve adları
KRITIK_ISLEM_ADLARI = {
    "systemd",
    "init",
    "kthreadd",
    "dbus-daemon",
    "systemd-journald",
    "systemd-logind",
    "sshd",
    "kethuda",
}

KRITIK_PIDLER = {0, 1, 2}


def root_mu() -> bool:
    """Mevcut kullanıcının root olup olmadığını kontrol eder."""
    try:
        return os.geteuid() == 0
    except AttributeError:
        return False


def sudo_mevcut_mu() -> bool:
    """Sistemde 'sudo' komutunun yüklü olup olmadığını kontrol eder."""
    return shutil.which("sudo") is not None


def kullanici_onayi_al(mesaj: str, varsayilan: bool = False) -> bool:
    """
    Kullanıcıdan açık onay (evet/hayır) ister.
    Varsayılan 'Hayır'dır ([e/H]).
    Eğer onay_istensin ayarı kapalıysa doğrudan varsayılanı değil True döner,
    ancak kritik işlemlerde her zaman sorulmalıdır.
    """
    cfg = get_config()
    onay_istensin = cfg.getir("onay_istensin", True)

    if not onay_istensin:
        return True

    secenek_metni = "[e/H]" if not varsayilan else "[E/h]"
    tam_mesaj = f"\n{c_bold(c_yellow('?'))} {mesaj} {c_bold(secenek_metni)}: "

    try:
        cevap = input(tam_mesaj).strip().lower()
        if not cevap:
            return varsayilan
        return cevap in ("e", "evet", "y", "yes")
    except (KeyboardInterrupt, EOFError):
        print()
        return False


def islem_kritik_mi(pid: int, ad: Optional[str] = None) -> Tuple[bool, str]:
    """Bir işlemin sonlandırılmasının yasak / kritik olup olmadığını kontrol eder."""
    cfg = get_config()
    if not cfg.getir("kritik_islem_korumasi", True):
        return False, ""

    mevcut_pid = os.getpid()
    if pid == mevcut_pid:
        return True, "KETHUDA'nın kendi sürecini sonlandıramazsınız."

    if pid in KRITIK_PIDLER or pid < 10:
        return True, f"PID {pid} sistem çekirdeği veya init sürecine aittir, sonlandırılamaz."

    if ad:
        temiz_ad = ad.lower().strip()
        if temiz_ad in KRITIK_ISLEM_ADLARI:
            return True, f"'{ad}' kritik bir sistem sürecidir, sonlandırılamaz."

    return False, ""


def servis_kritik_mi(servis_adi: str) -> Tuple[bool, str]:
    """Bir servisin kritik sistem servisi olup olmadığını kontrol eder."""
    cfg = get_config()
    if not cfg.getir("kritik_servis_korumasi", True):
        return False, ""

    temiz_ad = servis_adi.lower().strip()
    if temiz_ad in KRITIK_SERVISLER or f"{temiz_ad}.service" in KRITIK_SERVISLER:
        return True, f"'{servis_adi}' kritik bir sistem servisidir. Durdurulması sistem kararsızlığına yol açabilir."

    return False, ""


def guvenli_komut_calistir(
    komut_listesi: List[str],
    sudo_kullan: bool = False,
    zaman_asimi: int = 60,
    girdi: Optional[str] = None,
) -> Tuple[int, str, str]:
    """
    Subprocess üzerinden GÜVENLİ bir şekilde komut çalıştırır.
    Asla shell=True KULLANMAZ, komut enjeksiyonunu engeller.
    """
    calistirilacak = list(komut_listesi)

    if sudo_kullan and not root_mu():
        if not sudo_mevcut_mu():
            return -1, "", "Bu işlem yönetici (root) yetkisi gerektirir ancak sudo bulunamadı."
        calistirilacak = ["sudo"] + calistirilacak

    try:
        sonuc = subprocess.run(
            calistirilacak,
            capture_output=True,
            text=True,
            timeout=zaman_asimi,
            input=girdi,
            check=False,
        )
        return sonuc.returncode, sonuc.stdout, sonuc.stderr
    except subprocess.TimeoutExpired:
        return -2, "", f"Komut zaman aşımına uğradı ({zaman_asimi} saniye)."
    except FileNotFoundError:
        return -3, "", f"Komut bulunamadı: {calistirilacak[0]}"
    except Exception as e:
        return -4, "", f"Komut çalıştırılırken beklenmeyen hata: {str(e)}"
