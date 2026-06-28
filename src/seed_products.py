#seed_products.py
import undetected_chromedriver as uc
import tls_client
import time
import logging
import random
import csv
import traceback
import os
import pandas as pd

from dotenv import load_dotenv
load_dotenv()

LOG_YOLU = os.getenv("LOG_YOLU")
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(LOG_YOLU, encoding="utf-8"),
        logging.StreamHandler()
    ]
)

SATICI_ID = "761610"  # alfa-petshop
aktif_cookies = {}
SABIT_USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/120.0.0.0 Safari/537.36"  # tls_client ile tam uyumlu UA
)
session = None

def session_yenile():
    global session
    session = tls_client.Session(
        client_identifier="chrome_120",
        random_tls_extension_order=True
    )

def cookie_yenile():
    global aktif_cookies
    # 🛠️ DÜZELTME 2: Docker uyumlu HEADLESS (Ekransız) mod aktif edildi
    print("🔄 UC Tarayıcı Docker uyumlu HEADLESS modda başlatılıyor...")
    logging.info("Cookie alma işlemi başladı")

    session_yenile()
    driver = None
    try:
        options = uc.ChromeOptions()
        
        # Docker içinde çalışabilmesi için bu parametreler ŞARTTIR:
        options.add_argument("--headless") # <-- Ekranı kapattık, Docker'da çökmeyecek
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--disable-gpu") # GPU donanım hızlandırmayı kapat
        options.add_argument("--window-size=1400,900")
        options.add_argument(f"user-agent={SABIT_USER_AGENT}")

        # Bildirimleri otomatik engelle (Sol üstte donup kalmasın)
        prefs = {"profile.default_content_setting_values.notifications": 2}
        options.add_experimental_option("prefs", prefs)

        driver = uc.Chrome(options=options, version_main=149)
        
        # Doğrudan satıcının arama katalog sayfasına giderek en güçlü çerezleri tetikliyoruz
        hedef_url = f"https://www.trendyol.com/sr?mid={SATICI_ID}&pi=1"
        driver.get(hedef_url)
        
        print("⏳ Sayfanın yüklenmesi ve çerezlerin oturması için 8 saniye bekleniyor...")
        time.sleep(8)

        # Turuncu pop-up gelirse kodun donmaması için JS ile DOM üzerinden temizlik yapalım
        try:
            driver.execute_script("""
            document.querySelectorAll('.homepage-popup, .modal, .modal-backdrop, .overlay').forEach(el => el.remove());
            document.body.style.overflow = 'auto';
            """)
        except:
            pass

        # Çerezleri topla
        yeni_cookies = {c['name']: c['value'] for c in driver.get_cookies()}
        if not yeni_cookies:
            raise Exception("Maalesef Trendyol çerez üretmedi, tarayıcı engellendi!")

        yeni_cookies.update({
            'countryCode': 'TR',
            'storefrontId': '1',
            'language': 'tr',
            'platform': 'web',
        })
        aktif_cookies = yeni_cookies
        print(f"✅ UC Başarılı: {len(aktif_cookies)} adet organik çerez toplandı.")

    except Exception as e:
        print(f"❌ Cookie alma hatası: {e}")
        logging.error(traceback.format_exc())
    finally:
        if driver:
            try:
                driver.close()
                driver.quit()
            except Exception:
                pass

def url_olustur(sayfa):
    """Genel arama motoru üzerinden satıcı ürünlerini çeken güvenli URL."""
    return (
        f"https://apigw.trendyol.com/discovery-sfint-search-service/api/search/products"
        f"?mid={SATICI_ID}"
        f"&os=1"
        f"&pathModel=sr"
        f"&channelId=1"
        f"&storefrontId=1"
        f"&culture=tr-TR"
        f"&pi={sayfa}"
    )


def urun_cek(sayfa=1):
    headers = {
        'accept': 'application/json',
        'accept-language': 'tr-TR,tr;q=0.9,en-US;q=0.8,en;q=0.7',
        'content-type': 'application/json',
        'origin': 'https://www.trendyol.com',
        'referer': f'https://www.trendyol.com/sr?mid={SATICI_ID}',
        'user-agent': SABIT_USER_AGENT,
        'x-request-source': 'single-search-result',
    }

    url = url_olustur(sayfa)
    print(f"   🔗 API URL: {url}")

    for deneme in range(1, 4):
        try:
            response = session.get(
                url,
                cookies=aktif_cookies,
                headers=headers,
                timeout_seconds=15
            )

            if response.status_code == 403:
                print(f"⚠️ 403 Yasaklandı (deneme {deneme}), çerezler tazeleniyor...")
                cookie_yenile()
                time.sleep(3)
                continue

            if response.status_code != 200:
                print(f"⚠️ API Sıra Dışı Durum Döndü: {response.status_code}")
                return None

            return response

        except Exception as e:
            print(f"💥 İstek hatası: {e} (deneme {deneme})")
            time.sleep(4)

    print(f"⛔ Sayfa {sayfa} için tüm denemeler başarısız oldu.")
    return None

def marka_coz(urun):
    """F12 Network Preview ekranındaki güncel string yapısına göre markayı çözer."""
    # 1. Eğer brandName doğrudan varsa al
    if urun.get("brandName"): 
        return urun["brandName"]
        
    # 2. Görseldeki asıl durum: brand doğrudan bir string (metin) olarak geliyor!
    brand = urun.get("brand")
    if isinstance(brand, str) and brand.strip():
        return brand.strip()
        
    # 3. Eğer nadiren de olsa nesne gelirse garantiye alalım
    if isinstance(brand, dict):
        return brand.get("name", "Bilinmiyor")
        
    return "Bilinmiyor"

def kategori_coz(urun):
    """F12 Preview ekranındaki category -> name yapısına göre kategoriyi çözer."""
    kategori_obj = urun.get("category")
    if isinstance(kategori_obj, dict) and kategori_obj.get("name"):
        return kategori_obj["name"].strip()
    return "Bilinmiyor"

def fiyat_coz(urun):
    """Görseldeki güncel fiyat kırılımlarına göre en doğru fiyatı çeker."""
    # 1. binaryPrice -> salePrice kontrolü (Örn: "294,77 TL" gelebilir)
    binary_price = urun.get("binaryPrice")
    if isinstance(binary_price, dict) and binary_price.get("salePrice"):
        fiyat_str = str(binary_price["salePrice"])
        return fiyat_str.replace("TL", "").strip()
        
    # 2. Alternatif: appPrice -> newPrice kontrolü (Örn: "279,77")
    app_price = urun.get("appPrice")
    if isinstance(app_price, dict) and app_price.get("newPrice"):
        return str(app_price["newPrice"]).strip()
        
    # 3. Eski yapı için yedek kontrol
    price_obj = urun.get("price", {})
    if isinstance(price_obj, dict):
        for alan in ["sellingPrice", "discountedPrice", "value"]:
            if price_obj.get(alan): 
                return str(price_obj[alan]).strip()
                
    return urun.get("priceText", "?")

def kaydet(tum_urunler):
    CSV_YOLU = os.getenv("PRODUCT_DATA_YOLU")
    
    # 1. Adım: Trendyol'dan az önce API ile çekilen (anlık) verileri bir DataFrame'e toplayalım
    yeni_veriler_listesi = []
    for urun_veri in tum_urunler:
        urun  = urun_veri['urun']
        sayfa = urun_veri['sayfa']
        
        urun_id  = str(urun.get("id", "?"))  # ID'leri string yaparak eşleşme hatasını önlüyoruz
        kategori = kategori_coz(urun)
        marka    = marka_coz(urun)
        isim     = urun.get("name", "?")
        fiyat    = fiyat_coz(urun)
        zaman    = time.strftime('%Y-%m-%d %H:%M:%S')
        
        yeni_veriler_listesi.append({
            'id': urun_id,
            'kategori': kategori,
            'marka': marka,
            'ürün_adi': isim,
            'fiyat': fiyat,
            'sayfa': sayfa,
            'zaman': zaman
        })
    
    df_anlik = pd.DataFrame(yeni_veriler_listesi)

    # 2. Adım: Dosya kontrolü ve filtreleme mantığı
    if not os.path.exists(CSV_YOLU):
        # CSV dosyası daha önce hiç yoksa, anlık çekilen her şeyi direkt kaydet
        df_anlik.to_csv(CSV_YOLU, index=False, encoding='utf-8')
        print(f"\n 🎉 İlk kayıt: Toplam {len(df_anlik)} ürün '{CSV_YOLU}' dosyasına yazıldı.")
    else:
        # Diskten mevcut/eski CSV dosyasını oku
        df_eski = pd.read_csv(CSV_YOLU, dtype={'id': str})
        
        # 🟢 İSTEK 1: Sitede olmayan ama CSV'de olan ürünlerin silinmesi
        # Eski CSV içindeki ürünlerden, YALNIZCA şu an Trendyol API'sinden gelen ID'leri filtrele.
        # Böylece sitede artık yer almayan ürünler otomatik olarak elenmiş olur.
        df_eski_guncel = df_eski[df_eski['id'].isin(df_anlik['id'])].copy()
        
        # 🟢 İSTEK 2: ID'si uniq olmalı, mevcut olanlar tekrar eklenmesin (Sadece yeni ürünler eklensin)
        # Trendyol API'sinden yeni gelenlerden, eski güncel listede OLMAYANLARI filtrele.
        df_yeni_eklenecekler = df_anlik[~df_anlik['id'].isin(df_eski_guncel['id'])]
        
        # BONUS: Eğer sitede hala var olan ürünlerin fiyatı veya adı değiştiyse güncellenmesini istiyorsan,
        # eski veriyi korumak yerine direkt Trendyol'dan gelen son güncel veriyi baz alıp üstüne yazmak daha mantıklıdır.
        # Biz yine de senin istediğin gibi "eskiler aynen kalsın, sadece yeniler eklensin" mantığıyla birleştiriyoruz:
        df_final = pd.concat([df_eski_guncel, df_yeni_eklenecekler], ignore_index=True)
        
        # Her ihtimale karşı ID bazında mükerrer kayıt kontrolü (Garanti adım)
        df_final.drop_duplicates(subset=['id'], keep='first', inplace=True)
        
        # Veriyi CSV'ye kaydet (Eski dosyanın üzerine yazar)
        df_final.to_csv(CSV_YOLU, index=False, encoding='utf-8')
        
        # Konsola bilgilendirme basalım
        silinen_sayisi = len(df_eski) - len(df_eski_guncel)
        eklenen_sayisi = len(df_yeni_eklenecekler)
        print(f"\n🔄 CSV Güncellendi!")
        print(f"   ❌ Siteden kalkan (CSV'den silinen) ürün sayısı: {silinen_sayisi}")
        print(f"   ➕ Yeni eklenen benzersiz ürün sayısı: {eklenen_sayisi}")
        print(f"   📊 Toplam güncel ürün sayısı: {len(df_final)}")

def ana_gorev():
    if not aktif_cookies:
        print("⛔ Geçerli çerez havuzu yok, kazıma başlatılamıyor.")
        return

    print(f"\n🚀 API Kazıma Süreci Başlatıldı: {time.strftime('%H:%M:%S')}")
    havuz = []

    for sayfa in range(1, 100):
        response = urun_cek(sayfa)

        if response and response.status_code == 200:
            try:
                data = response.json()
                urunler = data.get("products", [])
                toplam = data.get("total", "?")

                print(f"\n📊 Sayfa {sayfa}: {len(urunler)} ürün listelendi (Toplam Mağaza Ürünü: {toplam})")

                if len(urunler) == 0:
                    print(f"   ✅ Temiz veri sonu — Mağazadaki tüm ürünler başarıyla tamamlandı.")
                    break

                for u in urunler:
                    havuz.append({'urun': u, 'sayfa': sayfa})

            except Exception as e:
                print(f"   ❌ JSON Veri Ayrıştırma Hatası: {e}")
        else:
            break

        bekleme = random.uniform(2.5, 4.5)
        print(f"   ⏳ Güvenlik koruması için {bekleme:.1f}s bekleniyor...")
        time.sleep(bekleme)

    if havuz:
        kaydet(havuz)
    else:
        print("\n⚠️ Hata: Sunucudan tek bir ürün dahi çekilemedi!")

if __name__ == "__main__":
    print("=" * 60)
    print(f"    Trendyol Satıcı Canlı API Kazıyıcı — (Satıcı ID: {SATICI_ID})")
    print("=" * 60)
    
    cookie_yenile()

    if aktif_cookies:
        ana_gorev()
    print("\n👋 Bitti.")