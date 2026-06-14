# ⚡ RipSearch — Ripgrep Benzeri Python Arama Aracı

> Ripgrep'ten ilham alınarak Python ile geliştirilmiş, hızlı ve kullanıcı dostu bir arama/değiştirme aracı.

## 📌 Proje Hakkında
Rust ile yazılmış Ripgrep (rg) aracının Python ile yeniden yorumlanmış halidir. Hem konsol (terminal) hem de görsel arayüz (GUI) olmak üzere iki farklı kullanım seçeneği sunar.

## 🚀 Özellikler
- ⚡ Paralel thread ile hızlı dosya tarama
- 🎨 Renkli terminal çıktısı
- 🔢 Satır numarası gösterimi
- 🔍 Regex desteği
- 🔄 Arama & değiştirme özelliği
- 📊 Hız raporu
- 📁 Çoklu dosya uzantısı desteği (.txt, .py, .csv, .log, .json, .md)
- 🕐 Arama geçmişi
- 🔬 Regex Tester — regex101 benzeri test ekranı
- 📦 Windows için .exe desteği

## 🛠️ Kurulum
```bash
pip install PyQt5
```

## 📖 Kullanım
```bash
# Basit arama
python arama.py "kelime" .

# Değiştirme
python arama.py "kelime" . -d "yeni"

# Regex
python arama.py "\d+" . -r

# Uzantı filtresi
python arama.py "import" . -u .py

# GUI
python arama_gui.py
```

## 📂 Dosya Yapısı
```
ripsearch/
├── arama.py        # Konsol versiyonu
├── arama_gui.py    # GUI versiyonu (PyQt5)
└── README.md
```

## 🔬 Regex Tester
GUI'deki Regex Tester sekmesi, regex101.com benzeri test ortamı sunar.

## 🏫 Proje Bilgisi
- **Ders:** Sistem Programlama / Görsel Programlama Uygulamaları 
- **Dil:** Python 3
- **Kütüphaneler:** PyQt5, re, argparse, concurrent.futures
- **Geliştirici:** Merve Sarı
