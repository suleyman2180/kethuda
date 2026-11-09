"""
KETHUDA SQLite İşlem Geçmişi Veritabanı
Sistem üzerinde yapılan kritik veya bilgilendirici işlemleri kayıt altında tutar.
"""

import sqlite3
import datetime
import os
from typing import List, Dict, Any, Optional
from kethuda.config import get_config


class HistoryDatabase:
    """İşlem geçmişini yöneten SQLite veritabanı sınıfı."""

    def __init__(self, db_path: Optional[str] = None):
        if db_path:
            self.db_path = db_path
        else:
            self.db_path = get_config().db_path

        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        self._tablolari_olustur()

    def _baglanti_al(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def _tablolari_olustur(self) -> None:
        """Veritabanı tablolarını ve indekslerini oluşturur."""
        with self._baglanti_al() as conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS gecmis (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    tarih TEXT NOT NULL,
                    islem_turu TEXT NOT NULL,
                    komut TEXT NOT NULL,
                    sonuc TEXT NOT NULL,
                    kullanici_onayi INTEGER DEFAULT 1,
                    detay TEXT
                )
                """
            )
            conn.execute(
                "CREATE INDEX IF NOT EXISTS idx_gecmis_tarih ON gecmis(tarih DESC)"
            )
            conn.execute(
                "CREATE INDEX IF NOT EXISTS idx_gecmis_tur ON gecmis(islem_turu)"
            )
            conn.commit()

    def kaydet(
        self,
        islem_turu: str,
        komut: str,
        sonuc: str,
        kullanici_onayi: bool = True,
        detay: str = "",
    ) -> int:
        """Yeni bir işlem kaydı ekler ve eklenen kaydın kimliğini döndürür."""
        simdi = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        onay_int = 1 if kullanici_onayi else 0
        try:
            with self._baglanti_al() as conn:
                cursor = conn.execute(
                    """
                    INSERT INTO gecmis (tarih, islem_turu, komut, sonuc, kullanici_onayi, detay)
                    VALUES (?, ?, ?, ?, ?, ?)
                    """,
                    (simdi, islem_turu, komut, sonuc, onay_int, detay),
                )
                conn.commit()
                return cursor.lastrowid or 0
        except Exception:
            return 0

    def listele(
        self, limit: int = 50, islem_turu: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """Geçmiş kayıtları listeler."""
        try:
            with self._baglanti_al() as conn:
                if islem_turu:
                    cursor = conn.execute(
                        """
                        SELECT id, tarih, islem_turu, komut, sonuc, kullanici_onayi, detay
                        FROM gecmis
                        WHERE islem_turu = ?
                        ORDER BY id DESC
                        LIMIT ?
                        """,
                        (islem_turu.upper(), limit),
                    )
                else:
                    cursor = conn.execute(
                        """
                        SELECT id, tarih, islem_turu, komut, sonuc, kullanici_onayi, detay
                        FROM gecmis
                        ORDER BY id DESC
                        LIMIT ?
                        """,
                        (limit,),
                    )
                rows = cursor.fetchall()
                return [dict(r) for r in rows]
        except Exception:
            return []

    def temizle(self) -> bool:
        """Tüm işlem geçmişini temizler."""
        try:
            with self._baglanti_al() as conn:
                conn.execute("DELETE FROM gecmis")
                conn.commit()
            # VACUUM işlemi transaction dışı autocommit modunda çalıştırılmalıdır
            conn_vac = sqlite3.connect(self.db_path, isolation_level=None)
            try:
                conn_vac.execute("VACUUM")
            finally:
                conn_vac.close()
            return True
        except Exception:
            return False

    def istatistikler(self) -> Dict[str, Any]:
        """Geçmişe ait özet istatistikler döndürür."""
        try:
            with self._baglanti_al() as conn:
                toplam = conn.execute("SELECT COUNT(*) FROM gecmis").fetchone()[0]
                basarili = conn.execute(
                    "SELECT COUNT(*) FROM gecmis WHERE sonuc = 'BAŞARILI'"
                ).fetchone()[0]
                hatali = conn.execute(
                    "SELECT COUNT(*) FROM gecmis WHERE sonuc = 'BAŞARISIZ' OR sonuc = 'HATA'"
                ).fetchone()[0]
                return {
                    "toplam_kayit": toplam,
                    "basarili": basarili,
                    "hatali": hatali,
                }
        except Exception:
            return {"toplam_kayit": 0, "basarili": 0, "hatali": 0}


_global_db: Optional[HistoryDatabase] = None


def get_database() -> HistoryDatabase:
    """Global veritabanı örneğini döndürür."""
    global _global_db
    if _global_db is None:
        _global_db = HistoryDatabase()
    return _global_db
