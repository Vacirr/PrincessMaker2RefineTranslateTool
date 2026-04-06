import os
import io
import time
try:
    from PIL import Image
except ImportError:
    print("Hata: Pillow eksik! Lütfen 'pip install Pillow' yazarak yükleyin. 🦶🏿")

START_SIG = b'\x89\x50\x4E\x47\x0D\x0A\x1A\x0A'
END_SIG = b'\x49\x45\x4E\x44\xAE\x42\x60\x82'

def anlik_log(mesaj, tip="BILGI"):
    etiket = "    [>]"
    if tip == "HATA": etiket = "[IPTAL]"
    elif tip == "BASARI": etiket = "[TAMAM]"
    elif tip == "BASLIK": etiket = "\n>>>"
    print(f"{etiket} {mesaj}")
    time.sleep(0.02)

def dosyalari_listele():
    return [f for f in os.listdir('.') if f.endswith('.dat')]

def ayikla_islem():
    dat_listesi = dosyalari_listele()
    if not dat_listesi:
        anlik_log("Klasörde hiç .dat dosyası bulunamadı! 🦶🏿", "HATA")
        return

    for hedef_dosya in dat_listesi:
        cikti_klasoru = f"ayiklanan_{hedef_dosya.split('.')[0]}"
        if not os.path.exists(cikti_klasoru): os.makedirs(cikti_klasoru)
        
        with open(hedef_dosya, 'rb') as f: data = f.read()
        
        pos, count = 0, 0
        anlik_log(f"{hedef_dosya} ayıklanıyor... 🦶🏿", "BASLIK")
        
        while True:
            idx = data.find(START_SIG, pos)
            if idx == -1: break
            e_idx = data.find(END_SIG, idx)
            if e_idx == -1: break
            e_idx += len(END_SIG)
            
            name_area = data[max(0, idx-64):idx].replace(b'\x00', b'').decode('ascii', errors='ignore')
            base_name = name_area.split(".png")[0][-4:] if ".png" in name_area else "resim"
            
            dosya_adi = f"{hex(idx)}_{base_name}.png"
            with open(os.path.join(cikti_klasoru, dosya_adi), 'wb') as out:
                out.write(data[idx:e_idx])
            
            pos = e_idx
            count += 1
        anlik_log(f"{count} adet dosya {cikti_klasoru} içine çıkarıldı. 🦶🏿", "BASARI")

def icerideki_dosyaya_gore_klonla(kullanici_png, ori_png_ham):
    """Sadece içerideki orijinal dosyanın teknik detaylarına bakar ve resmi ona zorlar. 🦶🏿"""
    # Önce içerideki orijinal dosyanın röntgenini çekiyoruz 🦶🏿
    with Image.open(io.BytesIO(ori_png_ham)) as ori_ref:
        hedef_mod = ori_ref.mode
        
        # Kullanıcının dosyasını açıyoruz 🦶🏿
        with Image.open(kullanici_png) as yeni:
            
            # Eğer içerideki dosya 8-bit (P) paletli ise, renkleri birebir orijinalden kopyalıyoruz 🦶🏿
            if hedef_mod == 'P':
                # dither=0 parametresi eklendi, böylece siyahlar bozulup grileşmeyecek! 🦶🏿
                yeni_son = yeni.convert('RGB').quantize(palette=ori_ref, dither=0)
            else:
                # İçerideki dosya RGB veya başka bir moddaysa, direkt o moda çeviriyoruz 🦶🏿
                yeni_son = yeni.convert(hedef_mod)
                
            buffer = io.BytesIO()
            yeni_son.save(buffer, format="PNG", optimize=True)
            return buffer.getvalue(), hedef_mod

def enjekte_et_tam_kontrol():
    mod_k = 'enjekte_edilecekler'
    if not os.path.exists(mod_k):
        os.makedirs(mod_k)
        anlik_log(f"'{mod_k}' açıldı! Düzenlediğiniz PNG'leri buraya atın. 🦶🏿", "HATA")
        return

    dat_listesi = dosyalari_listele()
    resimler = [f for f in os.listdir(mod_k) if f.endswith('.png')]

    if not resimler:
        anlik_log("Klasörde enjekte edilecek resim yok! 🦶🏿", "HATA")
        return

    for resim_adi in resimler:
        try: offset = int(resim_adi.split('_')[0], 16)
        except: continue

        anlik_log(f"HEDEF: {resim_adi} (Adres: {hex(offset)}) 🦶🏿", "BASLIK")

        for dat in dat_listesi:
            with open(dat, 'r+b') as f:
                f.seek(offset)
                if f.read(8) != START_SIG:
                    anlik_log(f"{dat}: Bu adreste PNG yok. Atlandı. 🦶🏿")
                    continue
                
                # İçerideki orijinal veriyi alıyoruz 🦶🏿
                f.seek(offset)
                ori_tara = f.read(500000)
                e_pos = ori_tara.find(END_SIG) + len(END_SIG)
                ori_png_ham = ori_tara[:e_pos]
                orijinal_boyut = len(ori_png_ham)

                # KLONLAMA İŞLEMİ: Tüm yetki içerideki dosyada 🦶🏿
                yeni_veri, hedef_mod = icerideki_dosyaya_gore_klonla(os.path.join(mod_k, resim_adi), ori_png_ham)
                yeni_boyut = len(yeni_veri)

                anlik_log(f"İçerideki Dosya Modu : {hedef_mod} -> Sizin dosya buna eşitlendi. 🦶🏿")
                anlik_log(f"Boyut Kontrolü       : Orijinal {orijinal_boyut} bayt | Yeni {yeni_boyut} bayt. 🦶🏿")

                # UYUMSUZLUK KONTROLÜ VE İPTAL 🦶🏿
                if yeni_boyut > orijinal_boyut:
                    anlik_log(f"{dat}: UYUMSUZ DOSYA! Yeni dosya orijinalden büyük. 🦶🏿", "HATA")
                    anlik_log("İŞLEM İPTAL EDİLDİ. .dat dosyası bozulmadı. Lütfen resmi küçültün. 🦶🏿", "HATA")
                    continue

                # Başarılı Yazma İşlemi 🦶🏿
                f.seek(offset)
                f.write(yeni_veri)
                if yeni_boyut < orijinal_boyut:
                    temizlenen = orijinal_boyut - yeni_boyut
                    f.write(b'\x00' * temizlenen)
                    anlik_log(f"Detay               : Aradaki {temizlenen} bayt sıfırlandı. 🦶🏿")
                
                anlik_log(f"{dat} başarıyla, orijinal ayarlarla güncellendi! 🦶🏿", "BASARI")

# --- MENÜ ---
if __name__ == "__main__":
    while True:
        print("\n" + "="*50)
        print(" [ PM2 REFINE - KUSURSUZ KLON MOD ARACI v10.0 ] 🦶🏿")
        print("="*50)
        print("1- TÜM .DAT DOSYALARINI AYIKLA (Export) 🦶🏿")
        print("2- DÜZENLENENLERİ GÖM (İçerideki Dosyayı Kopyala) 🦶🏿")
        print("0- ÇIKIŞ 🦶🏿")
        print("="*50)
        
        s = input("\nSeçiminiz Mete efendim: ")
        if s == "1": ayikla_islem()
        elif s == "2": enjekte_et_tam_kontrol()
        elif s == "0": break