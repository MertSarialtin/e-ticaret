# Trendyol Data Pipeline Simulation

Bu projede Trendyol benzeri bir e-ticaret sisteminin veri akışını simüle etmeyi amaçladım. Amaç, gerçek hayatta bir e-ticaret platformunda oluşabilecek müşteri, ürün ve sipariş verilerini belirli zaman aralıklarında üretip bir veri tabanına aktarmak ve bu süreci otomatik hale getirmektir.

## Kullanılan Teknolojiler

- Python
- PostgreSQL
- Apache Airflow
- Docker & Docker Compose
- AWS
- DBeaver

## Proje Yapısı

Sistem AWS üzerinde çalışmaktadır. Veriler Python ile üretilip PostgreSQL veritabanına kaydedilmektedir. Airflow kullanılarak veri üretme ve veri tabanına aktarma işlemleri belirli zamanlarda otomatik olarak tetiklenmektedir.

Veritabanındaki tablolar ve veriler DBeaver üzerinden takip edilmektedir.

## Veri Akışı

Projede farklı veri tipleri farklı zamanlarda oluşturulmaktadır:

### Sipariş Verileri

Her saat başı yeni sipariş kayıtları oluşturulur ve veritabanına eklenir.

### Müşteri Verileri

Her 3 saatte bir sisteme yeni müşteriler eklenir.

### Ürün Verileri

Ürün bilgileri, stok ve fiyat değişikliklerini simüle etmek amacıyla her gün saat 12:00'de güncellenir.

## Veri Modeli

Projede temel olarak üç tablo bulunmaktadır:

### Customer

Müşteri bilgilerini tutar. Yeni müşteriler belirli aralıklarla eklenir.

### Product

Ürün bilgileri, kategori, fiyat ve stok verilerini içerir.

### Order

Müşteri ve ürün tablolarıyla ilişkili sipariş kayıtlarını tutar.

## Kazanımlar

Bu proje sayesinde:

- Apache Airflow ile DAG geliştirme ve zamanlama işlemlerini öğrendim.
- PostgreSQL üzerinde ilişkisel veri modeli tasarladım.
- Docker kullanarak uygulamaları container ortamında çalıştırdım.
- AWS üzerinde çalışan bir veri pipeline'ı kurdum.
- Veri üretimi, veri tabanı yönetimi ve ETL süreçleri konusunda deneyim kazandım.
