# KETHUDA (v1.0.0)

**Ubuntu/Linux Modüler Bilgisayar ve Sistem Yönetim Aracı**

```
 ██╗  ██╗███████╗████████╗██╗  ██╗██╗   ██╗██████╗  █████╗ 
 ██║ ██╔╝██╔════╝╚══██╔══╝██║  ██║██║   ██║██╔══██╗██╔══██╗
 █████╔╝ █████╗     ██║   ███████║██║   ██║██║  ██║███████║
 ██╔═██╗ ██╔══╝     ██║   ██╔══██║██║   ██║██║  ██║██╔══██║
 ██║  ██╗███████╗   ██║   ██║  ██║╚██████╔╝██████╔╝██║  ██║
 ╚═╝  ╚═╝╚══════╝   ╚═╝   ╚═╝  ╚═╝ ╚═════╝ ╚═════╝  ╚═╝  ╚═╝
                                                KETHUDA v1.0.0
```

---

## 📌 Proje Hakkında

**KETHUDA**, Linux sistem yöneticileri, geliştiriciler ve ileri düzey kullanıcılar için tasarlanmış, bilgisayarın tüm temel yönetim ve denetim bileşenlerini tek bir çatı altında toplayan **tamamen Türkçe**, **CLI (Komut Satırı)** tabanlı, modüler bir sistem yönetim aracıdır.

KETHUDA basit bir temizlik aracı değildir; sistem izleme, süreç yönetimi, systemd servis denetimi, APT paket idaresi, sağlık teşhisi (doktor), SQLite tabanlı işlem geçmişi ve merkezi yapılandırma özelliklerini bir araya getiren kurumsal bir terminal çözümüdür.

### Temel İlkeler:
- ❌ **Grafik Arayüz (GUI) / Web Paneli Yoktur:** Bütün işlemler doğrudan Linux terminali üzerinden gerçekleştirilir.
- 🇹🇷 **Tamamen Türkçe Arayüz:** Tüm komutlar, alt komutlar, sistem raporları ve hata iletileri Türkçe olarak hazırlanmıştır. Türkçe karakter esnekliği (ör. `işlem`/`islem`, `geçmiş`/`gecmis`) desteklenir.
- 🛡️ **Güvenlik ve Koruma:** Salt-okunur işlemler sudo gerektirmez. Kritik süreçler (PID 1, init, dbus, kethuda vb.) ve hayati servisler (systemd-*, ssh, NetworkManager vb.) koruma altındadır. Hiçbir yıkıcı işlem kullanıcı onayı alınmadan yapılmaz.
- 📊 **Gerçek Sistem Verileri:** Sahte veya simüle veriler üretilmez; Ubuntu Linux `/proc`, `/sys`, `systemctl`, `apt` ve `psutil` altyapısı doğrudan okunur.

---

## 🌳 Komut Ağacı

```
KETHUDA
├── durum          # Gerçek zamanlı CPU, RAM, Disk, Uptime ve Donanım analizi
├── disk           # Bölüm listeleme, büyük dosya/klasör analizi ve doluluk raporu
│   ├── liste
│   ├── buyuk-dosyalar [dizin] [esik_mb]
│   ├── buyuk-klasorler [dizin]
│   └── rapor
├── temizlik       # Güvenli önbellek, çöp kutusu ve geçici dosya temizliği
│   ├── analiz / onizleme
│   └── calistir
├── islem          # Çalışan süreçleri izleme, filtreleme ve güvenli sonlandırma
│   ├── liste [cpu|ram]
│   ├── ara <kelime>
│   ├── detay <pid>
│   └── sonlandir <pid> [--zorla]
├── servis         # Ubuntu systemd servis yönetimi
│   ├── liste [calisan]
│   ├── durum <servis_adi>
│   ├── baslat <servis_adi>
│   ├── durdur <servis_adi>
│   ├── yeniden-baslat <servis_adi>
│   ├── etkin
│   └── devre-disi <servis_adi>
├── paket          # Ubuntu APT ve dpkg paket yönetimi
│   ├── liste
│   ├── ara <kelime>
│   ├── bilgi <paket_adi>
│   ├── kontrol
│   ├── guncelle
│   ├── kaldir <paket_adi>
│   ├── gereksiz
│   └── onbellek
├── kontrol        # Tek komutla sistem sağlık denetimi
├── doktor         # KETHUDA bağımlılıkları, izinler ve sistem teşhisi
├── gecmis         # SQLite tabanlı işlem kayıtları
│   ├── liste [tur]
│   └── temizle
├── ayar           # Merkezi yapılandırma yöneticisi
│   ├── liste
│   ├── getir <anahtar>
│   ├── belirle <anahtar> <deger>
│   └── sifirla
├── guncelle       # Sürüm denetimi ve yedekleme mekanizması
│   ├── kontrol
│   └── yedekle
├── yardim         # Kapsamlı yardım kılavuzu
└── surum          # Detaylı sürüm ve ortam bilgisi
```

---

## 💻 Kullanım Biçimleri

### 1. Etkileşimli Terminal Kabuğu (REPL)
Herhangi bir argüman vermeden çalıştırdığınızda KETHUDA etkileşimli kabuğu açılır:
```bash
kethuda
```
Kabuk içinde doğrudan komutları çalıştırabilirsiniz:
```text
kethuda > durum
kethuda > disk
kethuda > islem liste
kethuda > servis liste
kethuda > paket kontrol
kethuda > doktor
kethuda > cikis
```
*Not: Tab tuşu ile komut tamamlama desteklenir.*

### 2. Doğrudan CLI Komutları
```bash
kethuda durum
kethuda disk buyuk-dosyalar ~ 100
kethuda temizlik
kethuda islem ara python
kethuda servis durum ssh
kethuda kontrol
kethuda doktor
kethuda gecmis
kethuda ayar
kethuda surum
```

---

## ⚙️ Kurulum ve Kaldırma

### Gereksinimler
- Ubuntu Linux (veya Debian tabanlı dağıtımlar)
- Python 3.8 veya üzeri
- `psutil` Python kütüphanesi

### Kurulum:
```bash
cd ~/Masaüstü/kethuda
chmod +x install.sh
./install.sh
```
Kurulum betiği işletim sistemi sürümünü, Python sürümünü ve bağımlılıkları kontrol eder; `~/.local/bin/kethuda` çalıştırılabilir dosyasını ve gerekli kullanıcı dizinlerini oluşturur.

### Kaldırma:
```bash
./uninstall.sh
```
Kaldırma işlemi komut kısayollarını kaldırır; kullanıcı yapılandırması ve geçmiş kayıtlarını varsayılan olarak silmez (ancak kullanıcı isterse açık onayla silebilir).

---

## 🧪 Testlerin Çalıştırılması

Tüm temel modüller standart Python `unittest` altyapısı ile test edilebilir:
```bash
cd ~/Masaüstü/kethuda
python3 -m unittest discover -s tests -p "test_*.py" -v
```

---

## 🔒 Güvenlik Notları
- Komut çalıştırmalarında asla `shell=True` kullanılmaz; güvenli bağımsız argüman listeleri (`subprocess.run(["cmd", "arg"])`) ile komut enjeksiyonu engellenmiştir.
- Süreç ve servis sonlandırmalarında kritik bileşenler (systemd, kernel, dbus, network) program tarafından filtrelenir ve kullanıcıdan açık onay istenir.
- Yapılandırma ve işlem geçmişi yalnızca geçerli kullanıcının erişebileceği `0700` izinli güvenli dizinlerde (`~/.config/kethuda`, `~/.local/share/kethuda`) saklanır.
