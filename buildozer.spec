[app]
# Uygulama Adı ve Paketi
title = Finans Ultimate
package.name = finansultimate
package.domain = org.finans

# Kaynak kodun yeri (Nokta şu anki klasör demek)
source.dir = .
source.include_exts = py,png,jpg,kv,atlas

# Versiyon
version = 0.1

# GEREKLİ KÜTÜPHANELER (Çok Önemli!)
# Kodunda 'requests' ve 'sqlite3' var. Sqlite3 standarttır ama requests eklenmeli.
# requirements satırını bununla değiştir:
requirements = python3,kivy,requests,urllib3,chardet,idna,certifi,openssl,android

# İzinler (İnternetten döviz çektiğin için INTERNET izni şart)
android.permissions = INTERNET

# Ekran Yönü (Dikey kullanım için)
orientation = portrait

# Android Ayarları
android.api = 31
android.minapi = 21
android.ndk = 25b
android.accept_sdk_license = True
android.archs = arm64-v8a

[buildozer]
log_level = 2
warn_on_root = 1

