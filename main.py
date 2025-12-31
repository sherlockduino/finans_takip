import sqlite3
import csv
import threading
import time
import requests
import xml.etree.ElementTree as ET
from datetime import datetime
import sys
import os

# --- GEREKLİ KİVY KÜTÜPHANELERİ ---
from kivy.app import App
from kivy.lang import Builder
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.popup import Popup
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
from kivy.uix.recycleview import RecycleView
from kivy.properties import ListProperty, StringProperty
from kivy.clock import Clock, mainthread
from kivy.core.window import Window
from kivy.utils import platform

# Platform kontrolü (Android mi PC mi?)
IS_ANDROID = platform == "android"

# --- VERİTABANI YOLU AYARLAMA ---
# Veritabanı yolunu global değil, dinamik belirleyeceğiz
def get_db_path():
    if IS_ANDROID:
        from android.storage import app_storage_path
        storage_path = app_storage_path()
        return os.path.join(storage_path, "finans_ultimate_v19.db")
    else:
        return "finans_ultimate_v19.db"

# --- AYARLAR ---
RENK_BG = (0.95, 0.96, 0.96, 1)      
RENK_MAVI = (0.23, 0.51, 0.96, 1)    
RENK_YESIL = (0.06, 0.72, 0.50, 1)   
RENK_KIRMIZI = (0.93, 0.26, 0.26, 1) 
RENK_TURUNCU = (0.96, 0.62, 0.04, 1)  

Window.clearcolor = RENK_BG

# --- KV LANGUAGE (TASARIM KATMANI) ---
KV = """
#:import hex kivy.utils.get_color_from_hex

<CustomPopup>:
    size_hint: 0.9, 0.4
    auto_dismiss: False
    title: root.title_text
    BoxLayout:
        orientation: 'vertical'
        padding: 15
        spacing: 10
        Label:
            text: root.message
            text_size: self.width, None
            size_hint_y: None
            height: self.texture_size[1] + 20
            halign: 'center'
            valign: 'middle'
            color: 1, 1, 1, 1
        Button:
            text: "Tamam"
            size_hint_y: None
            height: dp(50)
            background_color: (0.23, 0.51, 0.96, 1)
            on_release: root.dismiss()

<IslemRow>:
    orientation: 'horizontal'
    size_hint_y: None
    height: dp(60)
    spacing: 5
    padding: 5
    canvas.before:
        Color:
            rgba: (1, 1, 1, 1) if self.index % 2 == 0 else (0.92, 0.92, 0.92, 1)
        Rectangle:
            pos: self.pos
            size: self.size
    
    BoxLayout:
        orientation: 'vertical'
        size_hint_x: 0.6
        Label:
            text: root.kategori
            color: 0,0,0,1
            bold: True
            font_size: '16sp'
            text_size: self.size
            halign: 'left'
            valign: 'middle'
        Label:
            text: root.tarih
            color: 0.4, 0.4, 0.4, 1
            font_size: '12sp'
            text_size: self.size
            halign: 'left'
            valign: 'middle'
            
    Label:
        text: root.tutar
        color: root.renk
        bold: True
        font_size: '16sp'
        size_hint_x: 0.3
        text_size: self.size
        halign: 'right'
        valign: 'middle'

    Button:
        text: "Sil"
        size_hint_x: None
        width: dp(50)
        font_size: '12sp'
        background_color: (0.9, 0.2, 0.2, 1)
        on_release: root.sil_tetikle()

<LoginScreen>:
    BoxLayout:
        orientation: 'vertical'
        padding: dp(30)
        spacing: dp(20)
        canvas.before:
            Color:
                rgba: (0.26, 0.37, 0.52, 1)
            Rectangle:
                pos: self.pos
                size: self.size
        
        Widget: 
            size_hint_y: 0.2

        Label:
            text: "💎 ULTIMATE ERP"
            font_size: '26sp'
            bold: True
            size_hint_y: None
            height: dp(60)
        
        TextInput:
            id: kadi
            hint_text: "Kullanıcı Adı"
            multiline: False
            size_hint_y: None
            height: dp(50)
            padding_y: [dp(15), dp(15)]
            write_tab: False
            
        TextInput:
            id: sifre
            hint_text: "Şifre"
            password: True
            multiline: False
            size_hint_y: None
            height: dp(50)
            padding_y: [dp(15), dp(15)]
            write_tab: False
            
        Button:
            text: "GİRİŞ YAP"
            background_color: (0.23, 0.51, 0.96, 1)
            size_hint_y: None
            height: dp(55)
            bold: True
            on_release: root.giris_yap()
            
        Button:
            text: "KAYIT OL"
            background_color: (0.06, 0.72, 0.50, 1)
            size_hint_y: None
            height: dp(55)
            bold: True
            on_release: root.kayit_ol()
            
        Widget:

<MainScreen>:
    BoxLayout:
        orientation: 'vertical'
        
        BoxLayout:
            orientation: 'vertical'
            size_hint_y: None
            height: dp(90)
            canvas.before:
                Color:
                    rgba: (0.26, 0.37, 0.52, 1)
                Rectangle:
                    pos: self.pos
                    size: self.size
            
            BoxLayout:
                size_hint_y: 0.5
                padding: [10, 0]
                Label:
                    text: "Ultimate ERP"
                    font_size: '18sp'
                    bold: True
                    halign: 'left'
                    text_size: self.size
                    valign: 'middle'
                Button:
                    text: "⚙️"
                    size_hint_x: None
                    width: dp(40)
                    background_color: 0,0,0,0
                    on_release: root.admin_popup_ac()
                Button:
                    text: "Çıkış"
                    size_hint_x: None
                    width: dp(60)
                    color: 1, 0.5, 0.5, 1
                    background_color: 0,0,0,0
                    on_release: app.stop()

            GridLayout:
                cols: 4
                size_hint_y: 0.5
                canvas.before:
                    Color:
                        rgba: (0.2, 0.25, 0.3, 1)
                    Rectangle:
                        pos: self.pos
                        size: self.size
                
                Label:
                    text: root.doviz_usd
                    font_size: '12sp'
                Label:
                    text: root.doviz_eur
                    font_size: '12sp'
                Label:
                    text: root.doviz_altin
                    font_size: '12sp'
                Label:
                    text: root.doviz_gumus
                    font_size: '12sp'

        ScreenManager:
            id: sm_content
            
            Screen:
                name: 'dashboard'
                ScrollView:
                    do_scroll_x: False
                    BoxLayout:
                        orientation: 'vertical'
                        size_hint_y: None
                        height: self.minimum_height
                        padding: dp(15)
                        spacing: dp(15)

                        Label:
                            text: "Finansal Özet"
                            font_size: '22sp'
                            color: 0,0,0,1
                            size_hint_y: None
                            height: dp(40)
                            bold: True
                            halign: 'left'
                            text_size: self.size

                        GridLayout:
                            cols: 2
                            spacing: dp(10)
                            size_hint_y: None
                            height: dp(180)
                            
                            InfoCard:
                                baslik: "NET DURUM"
                                deger: root.txt_net
                                renk: (0.23, 0.51, 0.96, 1)
                            InfoCard:
                                baslik: "GELİR"
                                deger: root.txt_gelir
                                renk: (0.06, 0.72, 0.50, 1)
                            InfoCard:
                                baslik: "GİDER"
                                deger: root.txt_gider
                                renk: (0.93, 0.26, 0.26, 1)
                            
                            BoxLayout:
                                orientation: 'vertical'
                                padding: 5
                                canvas.before:
                                    Color: rgba: 0.9, 0.9, 0.9, 1
                                    Rectangle: 
                                        pos: self.pos
                                        size: self.size
                                Label:
                                    text: root.txt_durum
                                    color: root.renk_durum
                                    font_size: '14sp'
                                    bold: True
                                    text_size: self.size
                                    halign: 'center'
                                    valign: 'middle'

                        Label:
                            text: "Harcama Dağılımı (Top 5)"
                            color: 0.3, 0.3, 0.3, 1
                            size_hint_y: None
                            height: dp(30)
                            halign: 'left'
                            text_size: self.size
                        
                        GridLayout:
                            id: chart_area
                            cols: 1
                            size_hint_y: None
                            height: self.minimum_height
                            spacing: dp(5)

            Screen:
                name: 'ekle'
                ScrollView:
                    BoxLayout:
                        orientation: 'vertical'
                        padding: dp(20)
                        spacing: dp(15)
                        size_hint_y: None
                        height: self.minimum_height

                        Label:
                            text: "İşlem Ekle / Düzenle"
                            font_size: '22sp'
                            color: 0,0,0,1
                            size_hint_y: None
                            height: dp(40)
                            bold: True
                        
                        Label:
                            text: "İşlem Türü"
                            color: 0.4, 0.4, 0.4, 1
                            size_hint_y: None
                            height: dp(20)
                            text_size: self.size
                            halign: 'left'

                        Spinner:
                            id: sp_tur
                            text: 'Gider'
                            values: ('Gelir', 'Gider', 'Borç', 'Alacak')
                            background_color: (0.23, 0.51, 0.96, 1)
                            size_hint_y: None
                            height: dp(50)
                            on_text: root.tur_degisti(self.text)
                        
                        Label:
                            text: "Kategori"
                            color: 0.4, 0.4, 0.4, 1
                            size_hint_y: None
                            height: dp(20)
                            text_size: self.size
                            halign: 'left'
                        
                        Spinner:
                            id: sp_kat
                            text: 'Seçiniz'
                            values: []
                            background_color: (0.5, 0.5, 0.5, 1)
                            size_hint_y: None
                            height: dp(50)
                        
                        Label:
                            text: "Tutar"
                            color: 0.4, 0.4, 0.4, 1
                            size_hint_y: None
                            height: dp(20)
                            text_size: self.size
                            halign: 'left'

                        TextInput:
                            id: ti_tutar
                            multiline: False
                            input_filter: 'float'
                            hint_text: "0.00"
                            size_hint_y: None
                            height: dp(50)
                            write_tab: False
                            
                        Label:
                            text: "Tarih (GG/AA/YYYY)"
                            color: 0.4, 0.4, 0.4, 1
                            size_hint_y: None
                            height: dp(20)
                            text_size: self.size
                            halign: 'left'

                        TextInput:
                            id: ti_tarih
                            text: root.bugun_tarih()
                            multiline: False
                            size_hint_y: None
                            height: dp(50)
                            write_tab: False
                            
                        Label:
                            text: "Açıklama"
                            color: 0.4, 0.4, 0.4, 1
                            size_hint_y: None
                            height: dp(20)
                            text_size: self.size
                            halign: 'left'

                        TextInput:
                            id: ti_desc
                            multiline: False
                            hint_text: "Opsiyonel"
                            size_hint_y: None
                            height: dp(50)
                            write_tab: False
                        
                        Button:
                            text: "KAYDET"
                            background_color: (0.06, 0.72, 0.50, 1)
                            size_hint_y: None
                            height: dp(60)
                            bold: True
                            on_release: root.kaydet()
                        
                        Widget: 
                            size_hint_y: None
                            height: dp(100)

            Screen:
                name: 'rapor'
                BoxLayout:
                    orientation: 'vertical'
                    padding: dp(10)
                    spacing: dp(10)
                    
                    BoxLayout:
                        size_hint_y: None
                        height: dp(50)
                        spacing: dp(10)
                        TextInput:
                            id: search_box
                            hint_text: "Ara..."
                            multiline: False
                            size_hint_x: 0.6
                            on_text_validate: root.arama_yap()
                        Button:
                            text: "Ara"
                            size_hint_x: 0.2
                            on_release: root.arama_yap()
                        Button:
                            text: "Excel"
                            size_hint_x: 0.2
                            background_color: (0.1, 0.6, 0.2, 1)
                            on_release: root.excel_aktar()

                    BoxLayout:
                        size_hint_y: None
                        height: dp(30)
                        canvas.before:
                            Color:
                                rgba: 0.8, 0.8, 0.8, 1
                            Rectangle:
                                pos: self.pos
                                size: self.size
                        Label:
                            text: "Detay"
                            color: 0,0,0,1
                            size_hint_x: 0.6
                        Label:
                            text: "Tutar"
                            color: 0,0,0,1
                            size_hint_x: 0.3
                        Label:
                            text: ""
                            size_hint_x: None
                            width: dp(50)
                    
                    RecycleView:
                        id: rv_liste
                        viewclass: 'IslemRow'
                        RecycleBoxLayout:
                            default_size: None, dp(60)
                            default_size_hint: 1, None
                            size_hint_y: None
                            height: self.minimum_height
                            orientation: 'vertical'
                            spacing: dp(2)

        BoxLayout:
            orientation: 'horizontal'
            size_hint_y: None
            height: dp(60)
            canvas.before:
                Color:
                    rgba: (0.26, 0.37, 0.52, 1)
                Rectangle:
                    pos: self.pos
                    size: self.size
            
            Button:
                text: "📊\\nÖzet"
                halign: 'center'
                background_normal: ''
                background_color: (0.26, 0.37, 0.52, 1)
                on_release: root.sayfa_degis('dashboard')
            Button:
                text: "➕\\nEkle"
                halign: 'center'
                background_normal: ''
                background_color: (0.26, 0.37, 0.52, 1)
                on_release: root.sayfa_degis('ekle')
            Button:
                text: "📄\\nRapor"
                halign: 'center'
                background_normal: ''
                background_color: (0.26, 0.37, 0.52, 1)
                on_release: root.sayfa_degis('rapor')

<InfoCard@BoxLayout>:
    orientation: 'vertical'
    baslik: ""
    deger: ""
    renk: (1,1,1,1)
    padding: dp(10)
    canvas.before:
        Color:
            rgba: 1, 1, 1, 1
        Rectangle:
            pos: self.pos
            size: self.size
        Color:
            rgba: root.renk
        Rectangle:
            pos: self.pos
            size: dp(5), self.height
            
    Label:
        text: root.baslik
        color: 0.5, 0.5, 0.5, 1
        font_size: '14sp'
        halign: 'left'
        text_size: self.size
    Label:
        text: root.deger
        color: 0,0,0,1
        font_size: '18sp'
        bold: True
        halign: 'left'
        text_size: self.size

<BarChartItem@BoxLayout>:
    kategori: ""
    tutar: ""
    oran: 0
    renk: (0.2, 0.2, 0.2, 1)
    size_hint_y: None
    height: dp(40)
    Label:
        text: root.kategori
        size_hint_x: 0.3
        color: 0,0,0,1
        halign: 'right'
        valign: 'middle'
        text_size: self.size
        font_size: '13sp'
    BoxLayout:
        size_hint_x: 0.5
        padding: [10, 10, 10, 10]
        canvas:
            Color:
                rgba: root.renk
            Rectangle:
                pos: self.pos[0] + 10, self.pos[1] + 10
                size: (self.width * root.oran), self.height - 20
    Label:
        text: root.tutar
        size_hint_x: 0.2
        color: 0,0,0,1
        font_size: '13sp'
"""

class CustomPopup(Popup):
    title_text = StringProperty("")
    message = StringProperty("")

def show_popup(title, msg):
    p = CustomPopup(title_text=title, message=msg)
    p.open()

class IslemRow(BoxLayout, RecycleView):
    id = 0
    tarih = StringProperty("")
    tur = StringProperty("")
    kategori = StringProperty("")
    tutar = StringProperty("")
    renk = ListProperty([0, 0, 0, 1])
    index = 0

    def sil_tetikle(self):
        App.get_running_app().root.get_screen('main').islem_sil(self.id)

class LoginScreen(Screen):
    def db_baglan(self):
        # Hata önleyici: DB yolunu her seferinde taze al
        return sqlite3.connect(get_db_path())

    def giris_yap(self):
        kadi = self.ids.kadi.text
        sifre = self.ids.sifre.text
        
        conn = self.db_baglan()
        cur = conn.cursor()
        cur.execute("CREATE TABLE IF NOT EXISTS kullanicilar (id INTEGER PRIMARY KEY, kadi TEXT UNIQUE, sifre TEXT)")
        
        # Test kullanıcısı oluştur (İlk açılış için)
        cur.execute("SELECT count(*) FROM kullanicilar")
        if cur.fetchone()[0] == 0:
            cur.execute("INSERT INTO kullanicilar (kadi, sifre) VALUES ('admin', '1234')")
            conn.commit()
            
        cur.execute("SELECT * FROM kullanicilar WHERE kadi=? AND sifre=?", (kadi, sifre))
        user = cur.fetchone()
        conn.close()
        
        if user:
            self.manager.current = 'main'
            self.manager.get_screen('main').dashboard_guncelle()
        else:
            show_popup("Hata", "Kullanıcı adı veya şifre yanlış!\n(Default: admin / 1234)")

    def kayit_ol(self):
        kadi = self.ids.kadi.text
        sifre = self.ids.sifre.text
        
        if not kadi or not sifre:
            show_popup("Uyarı", "Alanları doldurunuz.")
            return

        conn = self.db_baglan()
        cur = conn.cursor()
        try:
            cur.execute("INSERT INTO kullanicilar (kadi, sifre) VALUES (?,?)", (kadi, sifre))
            conn.commit()
            show_popup("Başarılı", "Kayıt olundu. Giriş yapabilirsiniz.")
        except sqlite3.IntegrityError:
            show_popup("Hata", "Bu kullanıcı adı zaten var.")
        finally:
            conn.close()

class MainScreen(Screen):
    doviz_usd = StringProperty("$: ...")
    doviz_eur = StringProperty("€: ...")
    doviz_altin = StringProperty("Au: ...")
    doviz_gumus = StringProperty("Ag: ...")
    
    txt_net = StringProperty("0.00 ₺")
    txt_gelir = StringProperty("0.00 ₺")
    txt_gider = StringProperty("0.00 ₺")
    txt_durum = StringProperty("Hesaplanıyor...")
    renk_durum = ListProperty([0,0,0,1])

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.calisiyor = True
        # Hemen başlatma, UI çizilince başlat
        Clock.schedule_once(self.baslat, 1)

    def baslat(self, dt):
        self.veritabani_kur()
        self.tur_degisti("Gider")
        threading.Thread(target=self.doviz_motoru, daemon=True).start()

    def veritabani_kur(self):
        self.conn = sqlite3.connect(get_db_path(), check_same_thread=False)
        self.cursor = self.conn.cursor()
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS islemler (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                tarih TEXT,
                vade_tarihi TEXT,
                tur TEXT,
                hesap_turu TEXT,
                kategori TEXT,
                tutar REAL,
                para_birimi TEXT,
                aciklama TEXT,
                durum TEXT DEFAULT 'Aktif',
                tekrar_eden INTEGER DEFAULT 0
            )
        """)
        self.conn.commit()
        self.dashboard_guncelle()

    def bugun_tarih(self):
        return datetime.now().strftime("%d/%m/%Y")

    def sayfa_degis(self, sayfa_adi):
        self.ids.sm_content.current = sayfa_adi
        if sayfa_adi == 'dashboard':
            self.dashboard_guncelle()
        elif sayfa_adi == 'rapor':
            self.arama_yap()

    def tur_degisti(self, tur_degeri):
        sp_kat = self.ids.sp_kat
        if tur_degeri == "Gelir":
            sp_kat.values = ["Maaş", "Satış", "Ek Gelir", "Yatırım"]
        elif tur_degeri == "Gider":
            sp_kat.values = ["Market", "Kira", "Fatura", "Eğlence", "Ulaşım", "Giyim", "Sağlık"]
        else:
            sp_kat.values = ["Şahıs", "Banka", "Diğer"]
        
        if sp_kat.values:
            sp_kat.text = sp_kat.values[0]

    def kaydet(self):
        tur = self.ids.sp_tur.text
        kat = self.ids.sp_kat.text
        tutar_str = self.ids.ti_tutar.text
        tarih = self.ids.ti_tarih.text
        aciklama = self.ids.ti_desc.text
        
        try:
            tutar = float(tutar_str)
        except ValueError:
            show_popup("Hata", "Tutar geçerli bir sayı olmalıdır.")
            return

        self.cursor.execute("""
            INSERT INTO islemler (tarih, tur, kategori, tutar, para_birimi, aciklama) 
            VALUES (?,?,?,?,'TL',?)
        """, (tarih, tur, kat, tutar, aciklama))
        self.conn.commit()
        
        show_popup("Başarılı", "İşlem Kaydedildi.")
        self.ids.ti_tutar.text = ""
        self.ids.ti_desc.text = ""
        self.sayfa_degis('dashboard')

    def dashboard_guncelle(self):
        try:
            self.cursor.execute("SELECT SUM(tutar) FROM islemler WHERE tur='Gelir'")
            res = self.cursor.fetchone()[0]
            gelir = res if res else 0.0

            self.cursor.execute("SELECT SUM(tutar) FROM islemler WHERE tur='Gider'")
            res = self.cursor.fetchone()[0]
            gider = res if res else 0.0

            net = gelir - gider

            self.txt_gelir = f"+{gelir:,.2f} ₺"
            self.txt_gider = f"-{gider:,.2f} ₺"
            self.txt_net = f"{net:,.2f} ₺"

            if net >= 0:
                self.txt_durum = "Durum İyi"
                self.renk_durum = RENK_YESIL
            else:
                self.txt_durum = "Dikkat: Eksi Bakiye"
                self.renk_durum = RENK_KIRMIZI

            self.grafik_ciz(gider)
        except Exception as e:
            print("Dashboard hata:", e)

    def grafik_ciz(self, toplam_gider):
        chart_area = self.ids.chart_area
        chart_area.clear_widgets()
        
        self.cursor.execute("SELECT kategori, SUM(tutar) FROM islemler WHERE tur='Gider' GROUP BY kategori ORDER BY SUM(tutar) DESC LIMIT 5")
        rows = self.cursor.fetchall()
        
        from kivy.factory import Factory
        colors = [RENK_MAVI, RENK_YESIL, RENK_TURUNCU, RENK_KIRMIZI, (0.5, 0, 0.5, 1)]
        
        for i, (kat, tutar) in enumerate(rows):
            oran = (tutar / toplam_gider) if toplam_gider > 0 else 0
            bar = Factory.BarChartItem()
            bar.kategori = kat
            bar.tutar = f"{tutar:.0f}"
            bar.oran = oran
            bar.renk = colors[i % len(colors)]
            chart_area.add_widget(bar)

    def arama_yap(self):
        keyword = self.ids.search_box.text.lower()
        self.cursor.execute("SELECT id, tarih, tur, kategori, tutar FROM islemler ORDER BY id DESC")
        rows = self.cursor.fetchall()
        
        data_list = []
        renk_map = {"Gelir": RENK_YESIL, "Gider": RENK_KIRMIZI, "Borç": RENK_MAVI}
        
        for i, r in enumerate(rows):
            full_str = f"{r[1]} {r[2]} {r[3]}".lower()
            if keyword in full_str:
                data_list.append({
                    'id': r[0],
                    'tarih': r[1],
                    'tur': r[2],
                    'kategori': r[3],
                    'tutar': f"{r[4]:.2f} ₺",
                    'renk': renk_map.get(r[2], (0,0,0,1)),
                    'index': i
                })
        
        self.ids.rv_liste.data = data_list

    def islem_sil(self, islem_id):
        self.cursor.execute("DELETE FROM islemler WHERE id=?", (islem_id,))
        self.conn.commit()
        self.arama_yap()

    def excel_aktar(self):
        path = "finans_raporu.csv"
        if IS_ANDROID:
            from android.storage import app_storage_path
            path = os.path.join(app_storage_path(), "finans_raporu.csv")
            
        try:
            with open(path, 'w', newline='', encoding='utf-8-sig') as f:
                w = csv.writer(f, delimiter=';')
                w.writerow(["ID", "Tarih", "Tür", "Kategori", "Tutar", "Açıklama"])
                self.cursor.execute("SELECT id, tarih, tur, kategori, tutar, aciklama FROM islemler")
                w.writerows(self.cursor.fetchall())
            show_popup("Başarılı", f"Dosya kaydedildi:\n{path}")
        except Exception as e:
            show_popup("Hata", str(e))

    def admin_popup_ac(self):
        content = BoxLayout(orientation='vertical', padding=10, spacing=10)
        t_user = TextInput(hint_text="Kullanıcı Adı", multiline=False, size_hint_y=None, height=dp(40))
        t_pass = TextInput(hint_text="Şifre", password=True, multiline=False, size_hint_y=None, height=dp(40))
        btn = Button(text="Doğrula", size_hint_y=None, height=dp(40), background_color=RENK_MAVI)
        
        popup = Popup(title="Yönetici", content=content, size_hint=(0.8, 0.4))
        
        def check(instance):
            if t_user.text == "admin" and t_pass.text == "1234":
                popup.dismiss()
                show_popup("Admin", "Giriş başarılı.")
            else:
                show_popup("Hata", "Yetkisiz Erişim")

        btn.bind(on_release=check)
        content.add_widget(t_user)
        content.add_widget(t_pass)
        content.add_widget(btn)
        popup.open()

    def doviz_motoru(self):
        while self.calisiyor:
            try:
                # TCMB ve API'den veri çekme (SSL GEREKTİRİR)
                r_xml = requests.get("https://www.tcmb.gov.tr/kurlar/today.xml", timeout=5)
                tree = ET.fromstring(r_xml.content)
                usd = tree.find("./Currency[@CurrencyCode='USD']/ForexSelling").text
                eur = tree.find("./Currency[@CurrencyCode='EUR']/ForexSelling").text
                
                r_json = requests.get("https://finans.truncgil.com/v4/today.json", timeout=5)
                data = r_json.json()
                altin = data.get("GRA", {}).get("Selling", "0")
                gumus = data.get("GUMUS", {}).get("Selling", "0")

                self.ui_doviz_guncelle(usd, eur, altin, gumus)
            except Exception as e:
                # Hata olsa bile programı çökertme, sadece bekle
                print("Doviz hatasi:", e)
                pass
            
            time.sleep(60)

    @mainthread
    def ui_doviz_guncelle(self, usd, eur, altin, gumus):
        self.doviz_usd = f"$ {usd}"
        self.doviz_eur = f"€ {eur}"
        self.doviz_altin = f"Au {altin}"
        self.doviz_gumus = f"Ag {gumus}"

    def on_stop(self):
        self.calisiyor = False

class FinansApp(App):
    def build(self):
        self.title = "Ultimate ERP"
        Builder.load_string(KV)
        sm = ScreenManager()
        sm.add_widget(LoginScreen(name='login'))
        sm.add_widget(MainScreen(name='main'))
        return sm

    def on_start(self):
        # KRİTİK DÜZELTME: İzinleri uygulama açıldıktan SONRA iste
        if IS_ANDROID:
            from android.permissions import request_permissions, Permission
            request_permissions([
                Permission.INTERNET,
                Permission.READ_EXTERNAL_STORAGE,
                Permission.WRITE_EXTERNAL_STORAGE
            ])

if __name__ == "__main__":
    FinansApp().run()
