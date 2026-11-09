"""
KETHUDA ASCII Logo ve Açılış Ekranı
"""

import shutil
from kethuda.version import __app_name__, __version__, __description__
from kethuda.interface.colors import (
    c_bright_cyan,
    c_cyan,
    c_bold,
    c_dim,
    c_gray,
    c_green,
    c_white,
    ansi_temizle,
)

ASCII_LOGO = [
    " ██╗  ██╗███████╗████████╗██╗  ██╗██╗   ██╗██████╗  █████╗ ",
    " ██║ ██╔╝██╔════╝╚══██╔══╝██║  ██║██║   ██║██╔══██╗██╔══██╗",
    " █████╔╝ █████╗     ██║   ███████║██║   ██║██║  ██║███████║",
    " ██╔═██╗ ██╔══╝     ██║   ██╔══██║██║   ██║██║  ██║██╔══██║",
    " ██║  ██╗███████╗   ██║   ██║  ██║╚██████╔╝██████╔╝██║  ██║",
    " ╚═╝  ╚═╝╚══════╝   ╚═╝   ╚═╝  ╚═╝ ╚═════╝ ╚═════╝  ╚═╝  ╚═╝",
]


def logo_metni() -> str:
    """KETHUDA ASCII logosunu ve hizalanmış sürüm bilgisini oluşturur."""
    cols = shutil.get_terminal_size((80, 24)).columns
    logo_width = max(len(line) for line in ASCII_LOGO)

    # Çok dar terminaller için sade metin modu
    if cols < logo_width + 4:
        baslik = f"=== {__app_name__} v{__version__} ==="
        aciklama = __description__
        return f"\n{c_bold(c_bright_cyan(baslik))}\n{c_dim(aciklama)}\n"

    sol_bosluk = max(0, (cols - logo_width) // 2)
    indent = " " * sol_bosluk

    satirlar = []
    satirlar.append("")
    for i, line in enumerate(ASCII_LOGO):
        if i < 2:
            renkli = c_bright_cyan(line)
        elif i < 4:
            renkli = c_cyan(line)
        else:
            renkli = c_cyan(line)
        satirlar.append(f"{indent}{renkli}")

    # Sürüm satırı: Logo genişliğinde sağa hizalı
    surum_metni = f"{__app_name__} v{__version__}"
    surum_bosluk = logo_width - len(surum_metni)
    surum_satiri = f"{indent}{' ' * max(0, surum_bosluk)}{c_bold(c_green(surum_metni))}"
    satirlar.append(surum_satiri)

    # Açıklama alt satırı
    aciklama_bosluk = max(0, (logo_width - len(__description__)) // 2)
    aciklama_satiri = f"{indent}{' ' * aciklama_bosluk}{c_dim(__description__)}"
    satirlar.append(aciklama_satiri)
    satirlar.append("")

    return "\n".join(satirlar)


def kucuk_baslik() -> str:
    """Komutların başında gösterilebilecek sade başlık."""
    return f"{c_bold(c_bright_cyan(__app_name__))} {c_dim(f'v{__version__}')}"
