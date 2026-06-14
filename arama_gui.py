import os
import re
import json
from datetime import datetime
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QLineEdit, QPushButton, QTextEdit, QFileDialog,
    QCheckBox, QButtonGroup, QRadioButton, QTabWidget,
    QMessageBox, QGroupBox, QStatusBar, QSplitter
)
from PyQt5.QtGui import QFont, QColor, QTextCharFormat, QTextCursor
from PyQt5.QtCore import Qt, QThread, pyqtSignal
import sys

STYLE = """
QMainWindow, QWidget {
    background-color: #1e1e2e;
    color: #f8f8f2;
    font-family: Consolas;
}
QTabWidget::pane {
    border: 1px solid #44475a;
    background: #1e1e2e;
}
QTabBar::tab {
    background: #2a2a3e;
    color: #6272a4;
    padding: 8px 20px;
    font-size: 11px;
}
QTabBar::tab:selected {
    background: #7c6af7;
    color: #f8f8f2;
}
QLineEdit {
    background: #313145;
    border: 1px solid #7c6af7;
    border-radius: 5px;
    padding: 6px 10px;
    color: #f8f8f2;
    font-size: 12px;
}
QLineEdit:focus {
    border: 1px solid #50fa7b;
}
QPushButton {
    background: #7c6af7;
    color: #f8f8f2;
    border: none;
    border-radius: 5px;
    padding: 8px 18px;
    font-size: 12px;
    font-weight: bold;
}
QPushButton:hover { background: #9580ff; }
QPushButton:pressed { background: #5a4fcf; }
QPushButton#temizle_btn {
    background: #2a2a3e;
    color: #ff5555;
    border: 1px solid #ff5555;
}
QPushButton#temizle_btn:hover {
    background: #ff5555;
    color: #f8f8f2;
}
QTextEdit {
    background: #2a2a3e;
    border: 1px solid #44475a;
    border-radius: 5px;
    color: #f8f8f2;
    font-family: Consolas;
    font-size: 12px;
    padding: 5px;
}
QGroupBox {
    border: 1px solid #44475a;
    border-radius: 5px;
    margin-top: 10px;
    padding-top: 10px;
    color: #6272a4;
    font-size: 11px;
}
QCheckBox, QRadioButton {
    color: #f8f8f2;
    font-size: 11px;
    spacing: 6px;
}
QStatusBar {
    background: #2a2a3e;
    color: #6272a4;
    font-size: 11px;
}
"""

# ── ARAMA THREAD ──
class AramaThread(QThread):
    sonuc_sinyali = pyqtSignal(str, int, str, str)
    bitis_sinyali = pyqtSignal(int, int)
    hata_sinyali  = pyqtSignal(str)

    def __init__(self, aranan, degistir, klasor, regex, uzanti):
        super().__init__()
        self.aranan = aranan
        self.degistir = degistir
        self.klasor = klasor
        self.regex = regex
        self.uzanti = uzanti

    def run(self):
        toplam_eslesme = 0
        toplam_dosya = 0
        for kok, _, dosyalar in os.walk(self.klasor):
            for dosya in dosyalar:
                if self.uzanti != "Hepsi" and not dosya.endswith(self.uzanti):
                    continue
                yol = os.path.join(kok, dosya)
                try:
                    with open(yol, "r", encoding="utf-8") as f:
                        satirlar = f.readlines()
                except:
                    continue
                dosya_eslesme = 0
                yeni = []
                for no, satir in enumerate(satirlar, 1):
                    try:
                        eslesme = re.search(self.aranan, satir) if self.regex \
                                  else self.aranan.lower() in satir.lower()
                    except re.error as e:
                        self.hata_sinyali.emit(f"Regex hatası: {e}")
                        return
                    if eslesme:
                        self.sonuc_sinyali.emit(yol, no, satir.rstrip(), self.aranan)
                        dosya_eslesme += 1
                        toplam_eslesme += 1
                        if self.degistir is not None:
                            satir = re.sub(self.aranan, self.degistir, satir) \
                                    if self.regex else satir.replace(self.aranan, self.degistir)
                    yeni.append(satir)
                if self.degistir is not None and dosya_eslesme > 0:
                    with open(yol, "w", encoding="utf-8") as f:
                        f.writelines(yeni)
                if dosya_eslesme > 0:
                    toplam_dosya += 1
        self.bitis_sinyali.emit(toplam_eslesme, toplam_dosya)

# ── GEÇMİŞ ──
GECMIS_DOSYA = "arama_gecmisi.json"

def gecmis_yukle():
    if os.path.exists(GECMIS_DOSYA):
        with open(GECMIS_DOSYA, "r", encoding="utf-8") as f:
            return json.load(f)
    return []

def gecmis_kaydet(aranan, klasor, sonuc):
    g = gecmis_yukle()
    g.insert(0, {"aranan": aranan, "klasor": klasor, "sonuc": sonuc,
                 "tarih": datetime.now().strftime("%d.%m.%Y %H:%M")})
    with open(GECMIS_DOSYA, "w", encoding="utf-8") as f:
        json.dump(g[:20], f, ensure_ascii=False, indent=2)

# ── ANA PENCERE ──
class RipSearch(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("⚡ RipSearch — Python Arama Aracı")
        self.setMinimumSize(950, 700)
        self.setStyleSheet(STYLE)
        self.thread = None

        merkez = QWidget()
        self.setCentralWidget(merkez)
        ana = QVBoxLayout(merkez)
        ana.setContentsMargins(20, 15, 20, 10)

        baslik = QLabel("⚡  RipSearch")
        baslik.setFont(QFont("Consolas", 22, QFont.Bold))
        baslik.setStyleSheet("color: #7c6af7;")
        baslik.setAlignment(Qt.AlignCenter)
        ana.addWidget(baslik)

        altyazi = QLabel("Ripgrep benzeri hızlı arama & değiştirme aracı")
        altyazi.setStyleSheet("color: #6272a4; font-size: 11px;")
        altyazi.setAlignment(Qt.AlignCenter)
        ana.addWidget(altyazi)

        self.tabs = QTabWidget()
        ana.addWidget(self.tabs)
        self.tabs.addTab(self._arama_sekmesi(),  "🔍  Arama")
        self.tabs.addTab(self._regex_sekmesi(),  "🔬  Regex Tester")
        self.tabs.addTab(self._gecmis_sekmesi(), "🕐  Geçmiş")

        self.status = QStatusBar()
        self.setStatusBar(self.status)
        self.status.showMessage("Hazır")

    # ── ARAMA SEKMESİ ──
    def _arama_sekmesi(self):
        w = QWidget()
        lay = QVBoxLayout(w)

        grup = QGroupBox("Arama Parametreleri")
        g = QVBoxLayout(grup)

        r1 = QHBoxLayout()
        r1.addWidget(QLabel("Aranan Kelime :"))
        self.aranan_giris = QLineEdit()
        self.aranan_giris.setPlaceholderText("kelime veya regex yaz...")
        r1.addWidget(self.aranan_giris)
        g.addLayout(r1)

        r2 = QHBoxLayout()
        r2.addWidget(QLabel("Değiştir       :"))
        self.degistir_giris = QLineEdit()
        self.degistir_giris.setPlaceholderText("boş bırakırsan sadece arar...")
        r2.addWidget(self.degistir_giris)
        g.addLayout(r2)

        r3 = QHBoxLayout()
        r3.addWidget(QLabel("Klasör         :"))
        self.klasor_giris = QLineEdit()
        r3.addWidget(self.klasor_giris)
        gb = QPushButton("📁 Gözat")
        gb.clicked.connect(self.klasor_sec)
        r3.addWidget(gb)
        g.addLayout(r3)
        lay.addWidget(grup)

        ayar = QHBoxLayout()
        ug = QGroupBox("Dosya Uzantısı")
        ul = QHBoxLayout(ug)
        self.uzanti_grup = QButtonGroup()
        for i, u in enumerate([".txt", ".py", ".csv", ".log", ".json", ".md", "Hepsi"]):
            rb = QRadioButton(u)
            if i == 0: rb.setChecked(True)
            self.uzanti_grup.addButton(rb, i)
            ul.addWidget(rb)
        ayar.addWidget(ug)
        self.regex_cb = QCheckBox("Regex kullan")
        self.regex_cb.setStyleSheet("color: #f1fa8c; font-size: 12px;")
        ayar.addWidget(self.regex_cb)
        lay.addLayout(ayar)

        btn = QHBoxLayout()
        ab = QPushButton("⚡  Aramayı Başlat")
        ab.clicked.connect(self.aramaya_basla)
        btn.addWidget(ab)
        tb = QPushButton("🗑  Temizle")
        tb.setObjectName("temizle_btn")
        tb.clicked.connect(self.temizle)
        btn.addWidget(tb)
        btn.addStretch()
        self.eslesme_lbl = QLabel("Eşleşme: 0")
        self.eslesme_lbl.setStyleSheet("color: #50fa7b; font-weight: bold;")
        btn.addWidget(self.eslesme_lbl)
        self.dosya_lbl = QLabel("Dosya: 0")
        self.dosya_lbl.setStyleSheet("color: #8be9fd; font-weight: bold;")
        btn.addWidget(self.dosya_lbl)
        lay.addLayout(btn)

        self.sonuc_alani = QTextEdit()
        self.sonuc_alani.setReadOnly(True)
        self.sonuc_alani.setPlaceholderText("Sonuçlar burada görünecek...")
        lay.addWidget(self.sonuc_alani)
        return w

    # ── REGEX TESTER SEKMESİ (regex101 gibi) ──
    def _regex_sekmesi(self):
        w = QWidget()
        lay = QVBoxLayout(w)
        lay.setSpacing(8)

        baslik = QLabel("🔬  Regex Tester — regex101 gibi çalışır")
        baslik.setStyleSheet("color: #7c6af7; font-size: 13px; font-weight: bold;")
        lay.addWidget(baslik)

        # Regex kalıbı giriş
        kalip_lay = QHBoxLayout()
        kalip_lay.addWidget(QLabel("Regex Kalıbı :"))
        self.kalip_giris = QLineEdit()
        self.kalip_giris.setPlaceholderText(r"örn: \d{2}\.\d{2}\.\d{4}  veya  [a-zA-Z0-9]+@\S+")
        self.kalip_giris.setStyleSheet("font-size: 13px; color: #f1fa8c;")
        kalip_lay.addWidget(self.kalip_giris)

        test_btn = QPushButton("▶  Test Et")
        test_btn.clicked.connect(self.regex_test)
        kalip_lay.addWidget(test_btn)

        temizle_btn = QPushButton("🗑")
        temizle_btn.setObjectName("temizle_btn")
        temizle_btn.setFixedWidth(40)
        temizle_btn.clicked.connect(self._regex_temizle)
        kalip_lay.addWidget(temizle_btn)
        lay.addLayout(kalip_lay)

        # Hazır kalıplar
        hazir_grup = QGroupBox("Hazır Kalıplar (tıkla → kalıp kutusuna gelir)")
        hazir_lay = QHBoxLayout(hazir_grup)

        kaliplar = [
            ("📅 Tarih", r"\d{2}\.\d{2}\.\d{4}"),
            ("📧 E-posta", r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}"),
            ("📞 Telefon", r"(\+90|0)?5\d{2}[\s\-]?\d{3}[\s\-]?\d{2}[\s\-]?\d{2}"),
            ("🔢 Rakam", r"\d+"),
            ("🔤 Kelime", r"\b[a-zA-Z]+\b"),
        ]
        for ad, kalip in kaliplar:
            btn = QPushButton(ad)
            btn.setStyleSheet("QPushButton { background: #313145; color: #f8f8f2; font-size: 11px; padding: 5px 10px; } QPushButton:hover { background: #7c6af7; }")
            btn.clicked.connect(lambda checked, k=kalip: self.kalip_giris.setText(k))
            hazir_lay.addWidget(btn)
        lay.addWidget(hazir_grup)

        # Test metni + Sonuç yan yana
        split = QSplitter(Qt.Horizontal)

        # Sol: Test metni
        sol = QWidget()
        sol_lay = QVBoxLayout(sol)
        sol_lay.addWidget(QLabel("📝  Test Metni:"))
        self.test_metin = QTextEdit()
        self.test_metin.setPlaceholderText(
            "Buraya test metni yaz veya yapıştır...\n\n"
            "Örnek:\n"
            "ahmet@gmail.com\n"
            "hsn@hsn.com\n"
            "gecersiz@\n"
            "Duruşma: 15.04.2024\n"
            "Tebligat: 01.01.2023\n"
            "Fiyat: 10.000 TL\n"
            "Tel: 05321234567"
        )
        sol_lay.addWidget(self.test_metin)
        split.addWidget(sol)

        # Sağ: Eşleşme sonuçları
        sag = QWidget()
        sag_lay = QVBoxLayout(sag)
        self.mac_lbl = QLabel("Eşleşme: 0")
        self.mac_lbl.setStyleSheet("color: #50fa7b; font-weight: bold; font-size: 12px;")
        sag_lay.addWidget(self.mac_lbl)
        sag_lay.addWidget(QLabel("✅  Bulunan Eşleşmeler:"))
        self.regex_sonuc = QTextEdit()
        self.regex_sonuc.setReadOnly(True)
        self.regex_sonuc.setPlaceholderText("Eşleşmeler burada görünecek...")
        sag_lay.addWidget(self.regex_sonuc)

        # Açıklama
        self.aciklama_lbl = QLabel("")
        self.aciklama_lbl.setStyleSheet("color: #6272a4; font-size: 11px;")
        self.aciklama_lbl.setWordWrap(True)
        sag_lay.addWidget(self.aciklama_lbl)
        split.addWidget(sag)

        split.setSizes([450, 450])
        lay.addWidget(split)
        return w

    def regex_test(self):
        """Kullanıcının yazdığı regex kalıbını test metninde dene."""
        kalip = self.kalip_giris.text().strip()
        metin = self.test_metin.toPlainText()

        if not kalip:
            QMessageBox.warning(self, "Uyarı", "Lütfen regex kalıbı girin!")
            return
        if not metin.strip():
            QMessageBox.warning(self, "Uyarı", "Lütfen test metni girin!")
            return

        try:
            eslesmen = re.findall(kalip, metin)
        except re.error as e:
            QMessageBox.critical(self, "Regex Hatası", f"Geçersiz regex: {e}")
            return

        self.regex_sonuc.clear()
        cur = self.regex_sonuc.textCursor()

        fmt_ok = QTextCharFormat()
        fmt_ok.setForeground(QColor("#50fa7b"))
        fmt_ok.setFontWeight(QFont.Bold)

        fmt_no = QTextCharFormat()
        fmt_no.setForeground(QColor("#6272a4"))

        fmt_eslesme = QTextCharFormat()
        fmt_eslesme.setForeground(QColor("#f1fa8c"))
        fmt_eslesme.setBackground(QColor("#3a3a00"))
        fmt_eslesme.setFontWeight(QFont.Bold)

        fmt_n = QTextCharFormat()
        fmt_n.setForeground(QColor("#f8f8f2"))

        if eslesmen:
            self.mac_lbl.setText(f"Eşleşme: {len(eslesmen)} ✔")
            self.mac_lbl.setStyleSheet("color: #50fa7b; font-weight: bold; font-size: 12px;")

            for i, e in enumerate(eslesmen, 1):
                # Tuple ise (grup içeriyorsa) birleştir
                if isinstance(e, tuple):
                    e = "".join(e)
                cur.insertText(f"  {i:2d}.  ", fmt_no)
                cur.insertText(f"{e}\n", fmt_eslesme)

            cur.insertText(f"\nToplam {len(eslesmen)} eşleşme bulundu.\n", fmt_ok)

            # Hangi satırlarda bulundu
            cur.insertText("\nSatır bazında:\n", fmt_n)
            for no, satir in enumerate(metin.splitlines(), 1):
                if re.search(kalip, satir):
                    cur.insertText(f"  Satır {no}: ", fmt_no)
                    cur.insertText(f"{satir.strip()}\n", fmt_n)
        else:
            self.mac_lbl.setText("Eşleşme: 0 ✘")
            self.mac_lbl.setStyleSheet("color: #ff5555; font-weight: bold; font-size: 12px;")
            cur.insertText("Hiçbir eşleşme bulunamadı.\n\nKalıbı kontrol et!", fmt_no)

        self.regex_sonuc.setTextCursor(cur)

        # Açıklama
        self.aciklama_lbl.setText(f"Kullanılan kalıp:  {kalip}")

    def _regex_temizle(self):
        self.kalip_giris.clear()
        self.test_metin.clear()
        self.regex_sonuc.clear()
        self.mac_lbl.setText("Eşleşme: 0")
        self.aciklama_lbl.setText("")

    # ── GEÇMİŞ SEKMESİ ──
    def _gecmis_sekmesi(self):
        w = QWidget()
        lay = QVBoxLayout(w)
        self.gecmis_alani = QTextEdit()
        self.gecmis_alani.setReadOnly(True)
        lay.addWidget(self.gecmis_alani)
        self.gecmis_guncelle()
        return w

    def klasor_sec(self):
        k = QFileDialog.getExistingDirectory(self, "Klasör Seç")
        if k:
            self.klasor_giris.setText(k)

    def aramaya_basla(self):
        aranan   = self.aranan_giris.text().strip()
        degistir = self.degistir_giris.text().strip() or None
        klasor   = self.klasor_giris.text().strip()
        regex    = self.regex_cb.isChecked()
        uzantilar = [".txt", ".py", ".csv", ".log", ".json", ".md", "Hepsi"]
        uzanti   = uzantilar[self.uzanti_grup.checkedId()]

        if not aranan:
            QMessageBox.warning(self, "Uyarı", "Lütfen aranan kelimeyi girin!")
            return
        if not klasor:
            QMessageBox.warning(self, "Uyarı", "Lütfen klasör seçin!")
            return

        self.sonuc_alani.clear()
        self.eslesme_lbl.setText("Eşleşme: 0")
        self.dosya_lbl.setText("Dosya: 0")
        self.status.showMessage("Aranıyor...")

        self.thread = AramaThread(aranan, degistir, klasor, regex, uzanti)
        self.thread.sonuc_sinyali.connect(self.satir_ekle)
        self.thread.bitis_sinyali.connect(lambda e, d: self.arama_bitti(e, d, aranan, klasor))
        self.thread.hata_sinyali.connect(lambda h: QMessageBox.critical(self, "Hata", h))
        self.thread.start()

    def satir_ekle(self, dosya, no, satir, aranan):
        cur = self.sonuc_alani.textCursor()
        fmt_d = QTextCharFormat()
        fmt_d.setForeground(QColor("#8be9fd"))
        fmt_d.setFontWeight(QFont.Bold)
        fmt_n = QTextCharFormat()
        fmt_n.setForeground(QColor("#f8f8f2"))
        fmt_e = QTextCharFormat()
        fmt_e.setForeground(QColor("#f1fa8c"))
        fmt_e.setBackground(QColor("#3a3a00"))
        fmt_e.setFontWeight(QFont.Bold)

        cur.movePosition(QTextCursor.End)
        cur.insertText(f"{dosya}:{no}: ", fmt_d)
        idx = satir.lower().find(aranan.lower())
        if idx >= 0:
            cur.insertText(satir[:idx], fmt_n)
            cur.insertText(satir[idx:idx+len(aranan)], fmt_e)
            cur.insertText(satir[idx+len(aranan):] + "\n", fmt_n)
        else:
            cur.insertText(satir + "\n", fmt_n)
        self.sonuc_alani.setTextCursor(cur)
        self.sonuc_alani.ensureCursorVisible()

    def arama_bitti(self, eslesme, dosya, aranan, klasor):
        fmt = QTextCharFormat()
        fmt.setForeground(QColor("#50fa7b"))
        fmt.setFontWeight(QFont.Bold)
        cur = self.sonuc_alani.textCursor()
        cur.movePosition(QTextCursor.End)
        cur.insertText(f"\n━━━ {eslesme} eşleşme, {dosya} dosyada bulundu ━━━\n", fmt)
        self.eslesme_lbl.setText(f"Eşleşme: {eslesme}")
        self.dosya_lbl.setText(f"Dosya: {dosya}")
        self.status.showMessage(f"Tamamlandı — {eslesme} eşleşme")
        gecmis_kaydet(aranan, klasor, eslesme)
        self.gecmis_guncelle()

    def temizle(self):
        self.sonuc_alani.clear()
        self.eslesme_lbl.setText("Eşleşme: 0")
        self.dosya_lbl.setText("Dosya: 0")

    def gecmis_guncelle(self):
        self.gecmis_alani.clear()
        gecmis = gecmis_yukle()
        cur = self.gecmis_alani.textCursor()
        fmt_b = QTextCharFormat()
        fmt_b.setForeground(QColor("#7c6af7"))
        fmt_b.setFontWeight(QFont.Bold)
        fmt_b.setFontPointSize(13)
        fmt_k = QTextCharFormat()
        fmt_k.setForeground(QColor("#f1fa8c"))
        fmt_k.setFontWeight(QFont.Bold)
        fmt_d = QTextCharFormat()
        fmt_d.setForeground(QColor("#6272a4"))
        fmt_s = QTextCharFormat()
        fmt_s.setForeground(QColor("#50fa7b"))
        cur.insertText("Son Aramalar\n\n", fmt_b)
        if not gecmis:
            cur.insertText("Henüz arama yapılmadı.\n", fmt_d)
        else:
            for i, g in enumerate(gecmis, 1):
                cur.insertText(f"  {i:2d}.  ", fmt_d)
                cur.insertText(g["aranan"], fmt_k)
                cur.insertText(f"  →  {g['klasor']}\n", fmt_d)
                cur.insertText(f"       {g['sonuc']} eşleşme  |  {g['tarih']}\n\n", fmt_s)

app = QApplication(sys.argv)
pencere = RipSearch()
pencere.show()
sys.exit(app.exec_())