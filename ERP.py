import os as o
import json as j
from datetime import datetime

class veri_deposu:
    def __init__(self,dosya_adi):
        self.dosya_adi = dosya_adi
        self.veriler = self.dosya_oku()
     
    def dosya_oku(self):
        if o.path.exists(self.dosya_adi):
            with open(self.dosya_adi,"r") as f:
              return j.load(f)
        return[]
    
    def dosya_yaz(self):
        with open(self.dosya_adi,"w") as w:
            j.dump(self.veriler,w,indent=4)
    
    def ekle(self,kayit):
        self.veriler.append(kayit)
        self.dosya_yaz()
    
    def sil(self,id):
        self.veriler = [k for k in self.veriler if k['id'] != id]
        self.dosya_yaz()
    
    def guncelle(self, id, yeni_veri):
        for i,kayit in enumerate(self.veriler):
            if kayit['id']==id:
                self.veriler[i] = {**kayit,**yeni_veri}
                break
        self.dosya_yaz()
    
    def hepsini_getir(self):
        return self.veriler
    
    def id_ile_getir(self,id):
        for kayit in self.veriler:
            if kayit['id'] == id:
                return kayit
        return None

class urun:
    def __init__(self,id,ad,alis_fiyati,satis_fiyati,stok):
        self.id = id
        self.ad = ad
        self.alis_fiyati = alis_fiyati
        self.satis_fiyati = satis_fiyati
        self.stok = stok
        
    def to_dict(self):
        return{
            "id":self.id,
            "ad":self.ad,
            "alis_fiyati":self.alis_fiyati,
            "satis_fiyati":self.satis_fiyati,
            "stok":self.stok
        }

class musteri:
    def __init__(self,id,ad,soyad,telefon,email):
        self.id = id
        self.ad = ad
        self.soyad = soyad
        self.telefon = telefon
        self.email = email  # Düzeltildi: emali -> email
    
    def to_dict(self):
        return{
            "id":self.id,
            "ad":self.ad,
            "soyad":self.soyad,
            "telefon":self.telefon,
            "email":self.email
        }

class eleman:
    def __init__(self,id,ad,soyad,pozisyon,maas):
        self.id = id
        self.ad = ad
        self.soyad = soyad
        self.pozisyon = pozisyon
        self.maas = maas

    def to_dict(self):
        return{
            "id":self.id,
            "ad":self.ad,
            "soyad":self.soyad,
            "pozisyon":self.pozisyon,
            "maas":self.maas
        }

class satis:
    def __init__(self,id,urun_id,musteri_id,eleman_id,adet,tarih):
        self.id = id
        self.urun_id = urun_id
        self.musteri_id = musteri_id
        self.eleman_id = eleman_id
        self.adet = adet
        self.tarih = tarih  # Eksik atama eklendi
    
    def to_dict(self):
        return{
          "id":self.id,
          "urun_id":self.urun_id,
          "musteri_id":self.musteri_id,
          "eleman_id":self.eleman_id,
          "adet":self.adet,
          "tarih":self.tarih
        }

class SatisYonetimSistemi:
    def __init__(self):
        self.urun_deposu = veri_deposu('urunler.json')
        self.musteri_deposu = veri_deposu('musteriler.json')
        self.eleman_deposu = veri_deposu('elemanlar.json')
        self.satis_deposu = veri_deposu('satislar.json')

    def urun_ekle(self,urun):
        self.urun_deposu.ekle(urun.to_dict()) 
    
    def urun_sil(self,urun_id):
        self.urun_deposu.sil(urun_id)
    
    def musteri_ekle(self,musteri):
        self.musteri_deposu.ekle(musteri.to_dict())
    
    def musteri_sil(self,musteri_id):
        self.musteri_deposu.sil(musteri_id)
    
    def eleman_ekle(self, eleman):
        self.eleman_deposu.ekle(eleman.to_dict())
    
    def eleman_sil(self, eleman_id):
        self.eleman_deposu.sil(eleman_id)
    
    def satis_yap(self,satis):
        # stok kontrolü
        urun = self.urun_deposu.id_ile_getir(satis.urun_id)
        if urun and urun['stok'] >= satis.adet:
            # stok güncelle
            yeni_stok = urun['stok'] - satis.adet
            self.urun_deposu.guncelle(satis.urun_id,{'stok':yeni_stok})  # Düzeltildi: güncele -> guncelle

            # satışı kaydet
            self.satis_deposu.ekle(satis.to_dict())
            return True
        return False
    
    def en_cok_satan_urunler(self,adet=5):
        urun_sayilari = {}
        for satis in self.satis_deposu.hepsini_getir():
            urun_id = satis['urun_id']
            urun_sayilari[urun_id] = urun_sayilari.get(urun_id,0) + satis['adet']  # Düzeltildi: urun_sa -> urun_sayilari
        
        siralanan = sorted(urun_sayilari.items(), key=lambda x: x[1], reverse=True)[:adet]   

        sonuc = []  # Girinti düzeltildi
        for urun_id, satis_adet in siralanan:
            urun = self.urun_deposu.id_ile_getir(urun_id)  # Düzeltildi: posu -> deposu
            if urun:
                sonuc.append({
                    'urun': urun['ad'],
                    'satis_adet': satis_adet,
                    'toplam_kazanc': satis_adet * urun['satis_fiyati']
                })
        return sonuc
    
    def en_fazla_alis_yapan_musteriler(self, adet=5):
        musteri_sayilari = {}
        for satis in self.satis_deposu.hepsini_getir():
            musteri_id = satis['musteri_id']
            musteri_sayilari[musteri_id] = musteri_sayilari.get(musteri_id, 0) + satis['adet']
        
        siralanan = sorted(musteri_sayilari.items(), key=lambda x: x[1], reverse=True)[:adet]
        
        sonuc = []
        for musteri_id, alis_adet in siralanan:
            musteri = self.musteri_deposu.id_ile_getir(musteri_id)
            if musteri:
                sonuc.append({
                    'musteri': f"{musteri['ad']} {musteri['soyad']}",
                    'alis_adet': alis_adet
                })
        return sonuc
    
    def musteri_alis_gecmisi(self, musteri_id):
        musteri = self.musteri_deposu.id_ile_getir(musteri_id)
        if not musteri:
            return None
        
        satislar = [s for s in self.satis_deposu.hepsini_getir() if s['musteri_id'] == musteri_id]
        
        sonuc = []
        for satis in satislar:
            urun = self.urun_deposu.id_ile_getir(satis['urun_id'])
            if urun:
                sonuc.append({
                    'urun': urun['ad'],
                    'adet': satis['adet'],
                    'tarih': satis['tarih'],
                    'toplam': satis['adet'] * urun['satis_fiyati']
                })
        return {
            'musteri': f"{musteri['ad']} {musteri['soyad']}",
            'alis_gecmisi': sonuc,
            'toplam_harcama': sum(item['toplam'] for item in sonuc)
        }
    
    def eleman_performans(self, eleman_id):
        eleman = self.eleman_deposu.id_ile_getir(eleman_id)
        if not eleman:
            return None
        
        satislar = [s for s in self.satis_deposu.hepsini_getir() if s['eleman_id'] == eleman_id]
        
        sonuc = []
        toplam_kazanc = 0
        for satis in satislar:
            urun = self.urun_deposu.id_ile_getir(satis['urun_id'])
            if urun:
                kazanc = satis['adet'] * (urun['satis_fiyati'] - urun['alis_fiyati'])
                toplam_kazanc += kazanc
                sonuc.append({
                    'urun': urun['ad'],
                    'adet': satis['adet'],
                    'tarih': satis['tarih'],
                    'kazanc': kazanc
                })
        
        return {
            'eleman': f"{eleman['ad']} {eleman['soyad']}",
            'satislar': sonuc,
            'toplam_satis': len(satislar),
            'toplam_kazanc': toplam_kazanc
        }
    
    def aylik_rapor(self, yil, ay):
        satislar = []
        for satis in self.satis_deposu.hepsini_getir():
            satis_tarihi = datetime.strptime(satis['tarih'], '%Y-%m-%d')
            if satis_tarihi.year == yil and satis_tarihi.month == ay:
                satislar.append(satis)
        
        toplam_kazanc = 0
        toplam_ciro = 0
        urun_bazli = {}
        
        for satis in satislar:
            urun = self.urun_deposu.id_ile_getir(satis['urun_id'])
            if urun:
                kar = satis['adet'] * (urun['satis_fiyati'] - urun['alis_fiyati'])
                ciro = satis['adet'] * urun['satis_fiyati']
                toplam_kazanc += kar
                toplam_ciro += ciro
                
                if urun['id'] in urun_bazli:
                    urun_bazli[urun['id']]['adet'] += satis['adet']
                    urun_bazli[urun['id']]['ciro'] += ciro
                    urun_bazli[urun['id']]['kar'] += kar
                else:
                    urun_bazli[urun['id']] = {
                        'urun_adi': urun['ad'],
                        'adet': satis['adet'],
                        'ciro': ciro,
                        'kar': kar
                    }
        
        return {
            'ay': ay,
            'yil': yil,
            'toplam_satis': len(satislar),
            'toplam_ciro': toplam_ciro,
            'toplam_kazanc': toplam_kazanc,
            'urun_bazli': list(urun_bazli.values())
        }

def urun_islemleri(sistem):
    while True:
        print("\n--- Ürün İşlemleri ---")
        print("1. Ürün Ekle")
        print("2. Ürün Sil")
        print("3. Ürün Listesi")
        print("0. Geri")
        
        secim = input("Seçiminiz: ")
        
        if secim == "0":
            break
        
        elif secim == "1":
            print("\nYeni Ürün Bilgileri:")
            id = int(input("ID: "))
            ad = input("Ad: ")
            alis_fiyati = float(input("Alış Fiyatı: "))
            satis_fiyati = float(input("Satış Fiyatı: "))
            stok = int(input("Stok: "))
            
            yeni_urun = urun(id, ad, alis_fiyati, satis_fiyati, stok)
            sistem.urun_ekle(yeni_urun)
            print("Ürün eklendi!")
        
        elif secim == "2":
            urun_id = int(input("Silinecek Ürün ID: "))
            sistem.urun_sil(urun_id)
            print("Ürün silindi!")
        
        elif secim == "3":
            urunler = sistem.urun_deposu.hepsini_getir()
            print("\n--- Tüm Ürünler ---")
            for urun in urunler:
                print(f"ID: {urun['id']}, Ad: {urun['ad']}, Alış: {urun['alis_fiyati']}, Satış: {urun['satis_fiyati']}, Stok: {urun['stok']}")
        
        else:
            print("Geçersiz seçim!")

def musteri_islemleri(sistem):
    while True:
        print("\n--- Müşteri İşlemleri ---")
        print("1. Müşteri Ekle")
        print("2. Müşteri Sil")
        print("3. Müşteri Listesi")
        print("4. Müşteri Alış Geçmişi")
        print("0. Geri")
        
        secim = input("Seçiminiz: ")
        
        if secim == "0":
            break
        
        elif secim == "1":
            print("\nYeni Müşteri Bilgileri:")
            id = int(input("ID: "))
            ad = input("Ad: ")
            soyad = input("Soyad: ")
            telefon = input("Telefon: ")
            email = input("Email: ")
            
            yeni_musteri = musteri(id, ad, soyad, telefon, email)
            sistem.musteri_ekle(yeni_musteri)
            print("Müşteri eklendi!")
        
        elif secim == "2":
            musteri_id = int(input("Silinecek Müşteri ID: "))
            sistem.musteri_sil(musteri_id)
            print("Müşteri silindi!")
        
        elif secim == "3":
            musteriler = sistem.musteri_deposu.hepsini_getir()
            print("\n--- Tüm Müşteriler ---")
            for musteri in musteriler:
                print(f"ID: {musteri['id']}, Ad-Soyad: {musteri['ad']} {musteri['soyad']}, Tel: {musteri['telefon']}")
        
        elif secim == "4":
            musteri_id = int(input("Müşteri ID: "))
            gecmis = sistem.musteri_alis_gecmisi(musteri_id)
            if gecmis:
                print(f"\n--- {gecmis['musteri']} Alış Geçmişi ---")
                for alis in gecmis['alis_gecmisi']:
                    print(f"Ürün: {alis['urun']}, Adet: {alis['adet']}, Tarih: {alis['tarih']}, Toplam: {alis['toplam']}")
                print(f"Toplam Harcama: {gecmis['toplam_harcama']}")
            else:
                print("Müşteri bulunamadı!")
        
        else:
            print("Geçersiz seçim!")

def eleman_islemleri(sistem):
    while True:
        print("\n--- Eleman İşlemleri ---")
        print("1. Eleman Ekle")
        print("2. Eleman Sil")
        print("3. Eleman Listesi")
        print("4. Eleman Performansı")
        print("0. Geri")
        
        secim = input("Seçiminiz: ")
        
        if secim == "0":
            break
        
        elif secim == "1":
            print("\nYeni Eleman Bilgileri:")
            id = int(input("ID: "))
            ad = input("Ad: ")
            soyad = input("Soyad: ")
            pozisyon = input("Pozisyon: ")
            maas = float(input("Maaş: "))
            
            yeni_eleman = eleman(id, ad, soyad, pozisyon, maas)
            sistem.eleman_ekle(yeni_eleman)
            print("Eleman eklendi!")
        
        elif secim == "2":
            eleman_id = int(input("Silinecek Eleman ID: "))
            sistem.eleman_sil(eleman_id)
            print("Eleman silindi!")
        
        elif secim == "3":
            elemanlar = sistem.eleman_deposu.hepsini_getir()
            print("\n--- Tüm Elemanlar ---")
            for eleman in elemanlar:
                print(f"ID: {eleman['id']}, Ad-Soyad: {eleman['ad']} {eleman['soyad']}, Pozisyon: {eleman['pozisyon']}, Maaş: {eleman['maas']}")
        
        elif secim == "4":
            eleman_id = int(input("Eleman ID: "))
            performans = sistem.eleman_performans(eleman_id)
            if performans:
                print(f"\n--- {performans['eleman']} Performans Raporu ---")
                print(f"Toplam Satış: {performans['toplam_satis']}")
                print(f"Toplam Kazanç: {performans['toplam_kazanc']}")
                print("\nSatış Detayları:")
                for satis in performans['satislar']:
                    print(f"Ürün: {satis['urun']}, Adet: {satis['adet']}, Tarih: {satis['tarih']}, Kazanç: {satis['kazanc']}")
            else:
                print("Eleman bulunamadı!")
        
        else:
            print("Geçersiz seçim!")

def satis_islemleri(sistem):
    while True:
        print("\n--- Satış İşlemleri ---")
        print("1. Yeni Satış")
        print("2. Satış Listesi")
        print("0. Geri")
        
        secim = input("Seçiminiz: ")
        
        if secim == "0":
            break
        
        elif secim == "1":
            print("\nYeni Satış Bilgileri:")
            id = int(input("Satış ID: "))
            urun_id = int(input("Ürün ID: "))
            musteri_id = int(input("Müşteri ID: "))
            eleman_id = int(input("Eleman ID: "))
            adet = int(input("Adet: "))
            tarih = input("Tarih (YYYY-AA-GG): ")
            
            yeni_satis = satis(id, urun_id, musteri_id, eleman_id, adet, tarih)
            if sistem.satis_yap(yeni_satis):
                print("Satış başarılı!")
            else:
                print("Satış başarısız! Stok yetersiz veya ürün bulunamadı.")
        
        elif secim == "2":
            satislar = sistem.satis_deposu.hepsini_getir()
            print("\n--- Tüm Satışlar ---")
            for satis_kaydi in satislar:
                urun = sistem.urun_deposu.id_ile_getir(satis_kaydi['urun_id'])
                musteri = sistem.musteri_deposu.id_ile_getir(satis_kaydi['musteri_id'])
                eleman = sistem.eleman_deposu.id_ile_getir(satis_kaydi['eleman_id'])
                
                urun_ad = urun['ad'] if urun else "Bilinmiyor"
                musteri_ad = f"{musteri['ad']} {musteri['soyad']}" if musteri else "Bilinmiyor"
                eleman_ad = f"{eleman['ad']} {eleman['soyad']}" if eleman else "Bilinmiyor"
                
                print(f"ID: {satis_kaydi['id']}, Ürün: {urun_ad}, Müşteri: {musteri_ad}, Eleman: {eleman_ad}, Adet: {satis_kaydi['adet']}, Tarih: {satis_kaydi['tarih']}")
        
        else:
            print("Geçersiz seçim!")

def rapor_islemleri(sistem):
    while True:
        print("\n--- Rapor İşlemleri ---")
        print("1. En Çok Satan Ürünler")
        print("2. En Fazla Alış Yapan Müşteriler")
        print("3. Aylık Rapor")
        print("0. Geri")
        
        secim = input("Seçiminiz: ")
        
        if secim == "0":
            break
        
        elif secim == "1":
            adet = int(input("Kaç ürün listelensin? (Varsayılan: 5) ") or 5)
            urunler = sistem.en_cok_satan_urunler(adet)
            print("\n--- En Çok Satan Ürünler ---")
            for i, urun in enumerate(urunler, 1):
                print(f"{i}. Ürün: {urun['urun']}, Satış Adet: {urun['satis_adet']}, Toplam Kazanç: {urun['toplam_kazanc']}")
        
        elif secim == "2":
            adet = int(input("Kaç müşteri listelensin? (Varsayılan: 5) ") or 5)
            musteriler = sistem.en_fazla_alis_yapan_musteriler(adet)
            print("\n--- En Fazla Alış Yapan Müşteriler ---")
            for i, musteri in enumerate(musteriler, 1):
                print(f"{i}. Müşteri: {musteri['musteri']}, Alış Adet: {musteri['alis_adet']}")
        
        elif secim == "3":
            yil = int(input("Yıl: "))
            ay = int(input("Ay: "))
            rapor = sistem.aylik_rapor(yil, ay)
            print(f"\n--- {ay}/{yil} Aylık Rapor ---")
            print(f"Toplam Satış: {rapor['toplam_satis']}")
            print(f"Toplam Ciro: {rapor['toplam_ciro']}")
            print(f"Toplam Kazanç: {rapor['toplam_kazanc']}")
            print("\nÜrün Bazlı Satışlar:")
            for urun in rapor['urun_bazli']:
                print(f"Ürün: {urun['urun_adi']}, Adet: {urun['adet']}, Ciro: {urun['ciro']}, Kar: {urun['kar']}")
        
        else:
            print("Geçersiz seçim!")

def main():
    sistem = SatisYonetimSistemi()
    print("""      
    ███████╗██████╗ ██████╗ 
    ██╔════╝██╔══██╗██╔══██╗
    █████╗ ██████╔╝██████╔╝
    ██╔══╝ ██╔══██╗██╔═══╝ 
    ███████╗██║ ██║██║     
    ╚══════╝╚═╝ ╚═╝╚═╝     
    """)
    while True:
        print("\n-----Satış Yönetimi Sistemi-----")  # Düzeltildi: kaçış karakteri
        print("1. Ürün İşlemleri")
        print("2. Müşteri İşlemleri")
        print("3. Eleman İşlemleri")
        print("4. Satış İşlemleri")
        print("5. Raporlar")
        print("q. Çıkış")
        
        mesaj = input("=> ")  # Düzeltildi: meseaj -> mesaj

        if mesaj == "q":
            break
        elif mesaj == "1":
            urun_islemleri(sistem)
        elif mesaj == "2":
            musteri_islemleri(sistem)
        elif mesaj == "3":
            eleman_islemleri(sistem)
        elif mesaj == "4":
            satis_islemleri(sistem)
        elif mesaj == "5":
            rapor_islemleri(sistem)
        else:
            print("Geçersiz seçim!")

if __name__ == "__main__":
    main()