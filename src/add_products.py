#add_products.py
import os
import pandas as pd
from sqlalchemy import text

# Airflow docker ortamına uyumlu import
from db_connection import get_db_engine


from dotenv import load_dotenv
load_dotenv()
CSV_YOLU = os.getenv("PRODUCT_DATA_YOLU")

if not os.path.exists(CSV_YOLU):
    print(f"❌ '{CSV_YOLU}' dosyası bulunamadı!")
    exit()

df = pd.read_csv(CSV_YOLU)
orijinal_sutunlar = ["id", "kategori", "marka", "ürün_adi", "fiyat", "zaman"] 
df = df[orijinal_sutunlar]

# Veri Tipi Temizliği
df["fiyat"] = df["fiyat"].astype(str).str.replace(".", "", regex=False).str.replace(",", ".", regex=False).astype(float)

sutun_haritasi = {
    "id": "product_id",
    "kategori": "category",
    "marka": "brand",
    "ürün_adi": "product_name",
    "fiyat": "price",
    "zaman": "scrape_date"
}
df = df.rename(columns=sutun_haritasi)
df["product_id"] = df["product_id"].astype(int)

# CSV içindeki mükerrer verileri temizle
df = df.drop_duplicates(subset=["product_id"], keep="last")
df["is_available"] = True

engine = get_db_engine()

# --- 🛰️ VERİTABANI KONTROL ADIMI ---
with engine.begin() as conn:
    conn.execute(text("ALTER TABLE products ADD COLUMN IF NOT EXISTS is_available BOOLEAN DEFAULT TRUE;"))
    conn.execute(text("UPDATE products SET is_available = TRUE WHERE is_available IS NULL;"))

# Veri setlerini hazırlayalım
df_yeni = pd.DataFrame()

try:
    db_idler = pd.read_sql("SELECT product_id FROM products", con=engine)["product_id"].tolist()
    csv_idler = df["product_id"].tolist()
    
    # 🔴 1. ADIM: Siteden kalkanlar -> is_available = FALSE yap
    kalkan_idler = [pid for pid in db_idler if pid not in csv_idler]
    if kalkan_idler:
        with engine.begin() as conn:
            formatli_idler = ",".join(map(str, kalkan_idler))
            conn.execute(text(f"UPDATE products SET is_available = FALSE WHERE product_id IN ({formatli_idler})"))
        print(f"⚠️ Siteden kalkan {len(kalkan_idler)} ürün veritabanında 'Tükenmiş (False)' yapıldı.")
    
    # 🟡 2. ADIM: Sitede aktif olanlar -> TOPLU GÜNCELLEME (Hızlı ve Profesyonel)
    mevcut_olanlar_df = df[df["product_id"].isin(db_idler)]
    if not mevcut_olanlar_df.empty:
        # Sorguya göndermek için veriyi sözlük listesi haline getiriyoruz
        guncellenecek_veriler = mevcut_olanlar_df[["price", "scrape_date", "product_id"]].to_dict(orient="records")
        
        with engine.begin() as conn:
            conn.execute(
                text("""
                    UPDATE products 
                    SET price = :price, scrape_date = :scrape_date, is_available = TRUE 
                    WHERE product_id = :product_id
                """),
                guncellenecek_veriler # Tek seferde tüm listeyi gömüyoruz, tek tek dönmüyoruz!
            )
        print(f"🔄 Sitede aktif olan {len(mevcut_olanlar_df)} ürünün verileri toplu güncellendi.")

    # ➕ 3. ADIM: Yeni eklenecek ürünleri ayıkla
    df_yeni = df[~df["product_id"].isin(db_idler)]

except Exception as e:
    print(f"⚠️ İşlem sırasında bir hata oluştu, yeni ürünler ana tablodan kontrol edilecek: {e}")
    # Hata durumunda güvenli kalmak için db_idler boşmuş gibi davranmıyoruz, insert'ü pas geçebiliriz veya loglarız.
    df_yeni = pd.DataFrame() 

# --- 💾 YENİ VERİLERİ VERİTABANINA YAZMA ---
if not df_yeni.empty:
    df_yeni.to_sql(name="products", con=engine, if_exists="append", index=False)
    print(f"➕ {len(df_yeni)} yepyeni ürün veritabanına eklendi.")
else:
    print("✨ Eklenecek yeni bir ürün yok, mevcutların tamamı senkronize edildi.")

print("📊 Tüm işlemler başarıyla tamamlandı!")