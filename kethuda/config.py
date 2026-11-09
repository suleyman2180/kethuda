"""
KETHUDA Yapılandırma Yöneticisi
Kullanıcı tercihlerini kalıcı olarak saklar ve yönetir.
"""

import os
import json
from pathlib import Path
from typing import Dict, Any, Optional

VARSAYILAN_AYARLAR: Dict[str, Any] = {
    "renkler": True,
    "cikti_bicimi": "standart",
    "gunluk_seviyesi": "INFO",
    "onay_istensin": True,
    "buyuk_dosya_esigi_mb": 50,
    "buyuk_klasor_esigi_mb": 100,
    "disk_uyari_yuzdesi": 85,
    "kritik_islem_korumasi": True,
    "kritik_servis_korumasi": True,
    "gelistirici_notu": "KETHUDA Ubuntu Sistem Yöneticisi",
}


class ConfigManager:
    """KETHUDA merkezi yapılandırma yöneticisi."""

    def __init__(self, custom_path: Optional[str] = None):
        if custom_path:
            self.config_file = Path(custom_path)
            self.config_dir = self.config_file.parent
        else:
            home = Path.home()
            self.config_dir = home / ".config" / "kethuda"
            self.config_file = self.config_dir / "config.json"

        self.data_dir = Path.home() / ".local" / "share" / "kethuda"
        self.state_dir = Path.home() / ".local" / "state" / "kethuda"

        self._ayarlar: Dict[str, Any] = dict(VARSAYILAN_AYARLAR)
        self._dizinleri_olustur()
        self.yukle()

    def _dizinleri_olustur(self) -> None:
        """Gereken kullanıcı dizinlerini güvenli izinlerle oluşturur."""
        for d in (self.config_dir, self.data_dir, self.state_dir):
            try:
                d.mkdir(parents=True, exist_ok=True, mode=0o700)
            except OSError:
                pass

    def yukle(self) -> None:
        """Yapılandırma dosyasını yükler, yoksa varsayılanları kaydeder."""
        if not self.config_file.exists():
            self.kaydet()
            return

        try:
            with open(self.config_file, "r", encoding="utf-8") as f:
                veriler = json.load(f)
                if isinstance(veriler, dict):
                    # Eksik anahtarları varsayılanlarla tamamla
                    for k, v in VARSAYILAN_AYARLAR.items():
                        self._ayarlar[k] = veriler.get(k, v)
        except Exception:
            # Okuma hatasında varsayılanlara dön
            self._ayarlar = dict(VARSAYILAN_AYARLAR)

    def kaydet(self) -> bool:
        """Mevcut ayarları JSON dosyasına yazar."""
        try:
            self._dizinleri_olustur()
            with open(self.config_file, "w", encoding="utf-8") as f:
                json.dump(self._ayarlar, f, ensure_ascii=False, indent=2)
            return True
        except Exception:
            return False

    def getir(self, anahtar: str, varsayilan: Any = None) -> Any:
        """Belirtilen ayar değerini döndürür."""
        return self._ayarlar.get(anahtar, varsayilan)

    def belirle(self, anahtar: str, deger: Any) -> bool:
        """Bir ayarı günceller ve kaydeder."""
        # Tip dönüşümlerini ve doğrulamalarını yap
        if anahtar in ("renkler", "onay_istensin", "kritik_islem_korumasi", "kritik_servis_korumasi"):
            if isinstance(deger, str):
                deger = deger.strip().lower() in ("1", "true", "evet", "e", "acik", "aktif", "on")
            else:
                deger = bool(deger)
        elif anahtar in ("buyuk_dosya_esigi_mb", "buyuk_klasor_esigi_mb", "disk_uyari_yuzdesi"):
            try:
                deger = int(deger)
            except (ValueError, TypeError):
                return False
        elif anahtar == "gunluk_seviyesi":
            deger = str(deger).upper()
            if deger not in ("DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"):
                return False
        elif anahtar == "cikti_bicimi":
            deger = str(deger).lower()
            if deger not in ("standart", "tablo", "sade"):
                return False

        self._ayarlar[anahtar] = deger
        return self.kaydet()

    def sifirla(self) -> bool:
        """Ayarları varsayılan değerlere döndürür."""
        self._ayarlar = dict(VARSAYILAN_AYARLAR)
        return self.kaydet()

    def tumunu_al(self) -> Dict[str, Any]:
        """Tüm ayarların bir kopyasını döndürür."""
        return dict(self._ayarlar)

    @property
    def config_path(self) -> str:
        return str(self.config_file)

    @property
    def db_path(self) -> str:
        return str(self.data_dir / "kethuda.db")

    @property
    def log_path(self) -> str:
        return str(self.state_dir / "kethuda.log")


# Global konfigürasyon tekil örneği (singleton)
_global_config: Optional[ConfigManager] = None


def get_config() -> ConfigManager:
    """Merkezi yapılandırma nesnesini döndürür."""
    global _global_config
    if _global_config is None:
        _global_config = ConfigManager()
    return _global_config
