import random
from datetime import datetime
from sqlalchemy import text
from db_connection import get_db_engine

def run_aws_simulation():
    engine = get_db_engine()
    
    try:
        with engine.begin() as conn:
            print("Kullanıcılar ve ürün bilgi havuzu AWS'den getiriliyor...")
            
            # 1. Tüm Müşteri ID'lerini çek
            user_rows = conn.execute(text("SELECT customer_id FROM customers;")).fetchall()
            all_user_ids = [row[0] for row in user_rows]
            
            # 2. Sadece AKTİF (is_available = True) olan ürünleri çekiyoruz
            # ONAY: WHERE is_available = TRUE filtresi eklendi. (Veri tabanın PostgreSQL olduğu için doğrudan TRUE yazabilirsin)
            product_rows = conn.execute(text("""
                SELECT product_id, price, category 
                FROM products 
                WHERE is_available = TRUE;
            """)).fetchall()
            
            if not all_user_ids or not product_rows:
                print("Hata: Kullanıcı veya sipariş verilebilecek aktif ürün bulunamadı!")
                return

            category_groups = {}
            products_dict = {}

            for row in product_rows:
                p_id, price, category = row[0], float(row[1]), row[2]
                products_dict[p_id] = price
                
                if category not in category_groups:
                    category_groups[category] = []
                category_groups[category].append(p_id)

            all_categories = list(category_groups.keys())

            # Kategori ağırlıklandırması (Karekök modeli)
            import math
            category_weights = [math.sqrt(len(category_groups[cat])) for cat in all_categories]

            # 10 ile 20 arasında rastgele bir müşteri sayısı seç
            num_customers_to_select = min(random.randint(10, 20), len(all_user_ids))
            selected_customers = random.sample(all_user_ids, num_customers_to_select)
            
            print(f"Bugün sipariş verecek {len(selected_customers)} müşteri seçildi.")
            
            simulated_orders = []
            
            # Kodun çalıştığı tam şu anın zamanı
            current_now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

            for customer_id in selected_customers:
                items_count = random.randint(1, 3)
                
                for _ in range(items_count):
                    chosen_category = random.choices(all_categories, weights=category_weights, k=1)[0]
                    product_id = random.choice(category_groups[chosen_category])
                    quantity = random.randint(1, 3)
                    
                    unit_price = products_dict[product_id]
                    total_price = unit_price * quantity
                    
                    simulated_orders.append({
                        "customer_id": customer_id,
                        "product_id": product_id,
                        "quantity": quantity,
                        "order_date": current_now, 
                        "total_price": total_price
                    })
            
            # 3. AWS'ye insert
            query = text("""
                INSERT INTO orders (customer_id, product_id, quantity, order_date, total_price) 
                VALUES (:customer_id, :product_id, :quantity, :order_date, :total_price);
            """)
            
            print(f"AWS sunucusuna tam şu anın saatiyle {len(simulated_orders)} adet aktif ürün siparişi yazılıyor...")
            conn.execute(query, simulated_orders)
            
            print(f"Simülasyon başarıyla tamamlandı! Tarih: {current_now}")

    except Exception as e:
        print(f"Hata oluştu: {e}")

run_aws_simulation()

