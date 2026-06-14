import os
import re
import argparse
import time
import sys
from concurrent.futures import ThreadPoolExecutor, as_completed

KIRMIZI  = "\033[91m"
SARI     = "\033[93m"
YESIL    = "\033[92m"
MAVI     = "\033[94m"
MOR      = "\033[95m"
KALIN    = "\033[1m"
SIFIRLA  = "\033[0m"

def dosyada_ara(dosya_yolu, aranan, degistir=None, regex=False):
    try:
        with open(dosya_yolu, "r", encoding="utf-8", errors="ignore") as f:
            icerik = f.read()
            satirlar = icerik.splitlines()
    except:
        return 0, []

    sonuclar = []
    eslesme_sayisi = 0
    yeni_satirlar = []

    for numara, satir in enumerate(satirlar, start=1):
        if regex:
            eslesme = re.search(aranan, satir)
        else:
            eslesme = aranan.lower() in satir.lower()

        if eslesme:
            eslesme_sayisi += 1
            sonuclar.append((numara, satir))
            if degistir is not None:
                if regex:
                    satir = re.sub(aranan, degistir, satir)
                else:
                    satir = satir.replace(aranan, degistir)
        yeni_satirlar.append(satir)

    if degistir is not None and eslesme_sayisi > 0:
        with open(dosya_yolu, "w", encoding="utf-8") as f:
            f.write("\n".join(yeni_satirlar))

    return eslesme_sayisi, sonuclar


def klasorde_ara(klasor, aranan, degistir=None, regex=False, uzanti=None):
    baslangic = time.perf_counter()

    # Tüm dosyaları topla
    tum_dosyalar = []
    for kok, _, dosyalar in os.walk(klasor):
        for dosya in dosyalar:
            if uzanti and not dosya.endswith(uzanti):
                continue
            tum_dosyalar.append(os.path.join(kok, dosya))

    toplam_eslesme = 0
    toplam_dosya   = 0
    ciktilar = {}

    # Paralel arama — aynı anda 8 dosya tara
    with ThreadPoolExecutor(max_workers=8) as executor:
        gelecekler = {
            executor.submit(dosyada_ara, yol, aranan, degistir, regex): yol
            for yol in tum_dosyalar
        }
        for gelecek in as_completed(gelecekler):
            yol = gelecekler[gelecek]
            sayi, sonuclar = gelecek.result()
            if sayi > 0:
                ciktilar[yol] = sonuclar
                toplam_eslesme += sayi
                toplam_dosya   += 1

    # Sıralı çıktı
    for yol in sorted(ciktilar.keys()):
        for numara, satir in ciktilar[yol]:
            print(f"{MAVI}{yol}{SIFIRLA}:{SARI}{numara}{SIFIRLA}:", end=" ")
            if regex:
                m = re.search(aranan, satir)
                if m:
                    print(satir[:m.start()], end="")
                    print(f"{KIRMIZI}{KALIN}{satir[m.start():m.end()]}{SIFIRLA}", end="")
                    print(satir[m.end():].rstrip())
            else:
                idx = satir.lower().find(aranan.lower())
                print(satir[:idx], end="")
                print(f"{KIRMIZI}{KALIN}{satir[idx:idx+len(aranan)]}{SIFIRLA}", end="")
                print(satir[idx+len(aranan):].rstrip())

    sure = time.perf_counter() - baslangic

    print()
    print(f"{MOR}{'━'*50}{SIFIRLA}")
    print(f"{KALIN}📊  RipSearch Sonuç Raporu{SIFIRLA}")
    print(f"{MOR}{'━'*50}{SIFIRLA}")
    print(f"  {YESIL}✔  Eşleşme   :{SIFIRLA}  {KALIN}{toplam_eslesme}{SIFIRLA}")
    print(f"  {MAVI}📄  Dosya     :{SIFIRLA}  {toplam_dosya} dosyada bulundu")
    print(f"  {SARI}📁  Taranan   :{SIFIRLA}  {len(tum_dosyalar)} dosya tarandı")
    print(f"  {KIRMIZI}⏱  Süre      :{SIFIRLA}  {KALIN}{sure:.4f} saniye{SIFIRLA}")

    if sure < 0.05:
        print(f"  {YESIL}⚡ Hız       :  ÇOK HIZLI (ripgrep seviyesi!){SIFIRLA}")
    elif sure < 0.5:
        print(f"  {YESIL}✅ Hız       :  HIZLI{SIFIRLA}")
    else:
        print(f"  {SARI}⚠  Hız       :  Normal{SIFIRLA}")

    print(f"{MOR}{'━'*50}{SIFIRLA}")

    if degistir:
        print(f"{YESIL}✔  Değiştirme: '{aranan}' → '{degistir}'{SIFIRLA}")


parser = argparse.ArgumentParser(
    description="⚡ RipSearch — Ripgrep benzeri paralel Python arama aracı")
parser.add_argument("aranan",           help="Aranacak kelime veya regex")
parser.add_argument("klasor",           help="Aranacak klasör yolu")
parser.add_argument("-d", "--degistir", help="Değiştirme metni", default=None)
parser.add_argument("-r", "--regex",    help="Regex modu", action="store_true")
parser.add_argument("-u", "--uzanti",   help="Dosya uzantısı (ör: .py)", default=None)

args = parser.parse_args()
klasorde_ara(args.klasor, args.aranan, args.degistir, args.regex, args.uzanti)