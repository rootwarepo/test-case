from fastapi import FastAPI, HTTPException
from typing import Optional
from pydantic import BaseModel
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

app = FastAPI()

class Kullanici(BaseModel):
    id: int
    tam_ad: str
    sifre: str
    email: str
    rol: str

class Gorev(BaseModel):
    id: Optional[int] = None
    gorev_zamani: Optional[str] = None
    gorev_basligi: Optional[str] = None
    gorev_konusu: Optional[str] = None
    durum: Optional[str] = None
    silinmis_mi: Optional[bool] = False

kullanicilar = []
gorevler = []

def email_gonder(email):
    gonderen_email = "ornek@gmail.com"  
    gonderen_sifre = "sifre"   

    konu = "Yeni Görev Eklendi"
    icerik = "Başarılı!"

    mesaj = MIMEMultipart()
    mesaj['From'] = gonderen_email
    mesaj['To'] = email
    mesaj['Subject'] = konu
    mesaj.attach(MIMEText(icerik, 'plain'))

    with smtplib.SMTP('smtp.gmail.com', 587) as sunucu:  
        sunucu.starttls()
        sunucu.login(gonderen_email, gonderen_sifre)
        metin = mesaj.as_string()
        sunucu.sendmail(gonderen_email, email, metin)

def giris_kontrol(email: str, sifre: str):
    for kullanici in kullanicilar:
        if kullanici.email == email and kullanici.sifre == sifre:
            return kullanici.rol
    return None

@app.post("/kullanici_ekle/")
def kullanici_ekle(kullanici: Kullanici):
    kullanicilar.append(kullanici)
    return {"message": "Kullanıcı başarıyla eklendi"}

@app.post("/gorev_ekle/")
def gorev_ekle(email: str, sifre: str, gorev: Gorev):
    rol = giris_kontrol(email, sifre)
    if not rol:
        raise HTTPException(status_code=401, detail="Giriş başarısız")
    if rol != "admin":
        raise HTTPException(status_code=403, detail="Sadece yönetici görev ekleyebilir")
    gorevler.append(gorev)
    for kullanici in kullanicilar:
        #email_gonder(kullanici.email)
        pass
    return {"message": "Görev başarıyla eklendi"}

@app.patch("/gorev_guncelle/{gorev_id}")
def gorev_guncelle(email: str, sifre: str, gorev_id: int, guncellenmis_gorev: Gorev):
    rol = giris_kontrol(email, sifre)
    if not rol:
        raise HTTPException(status_code=401, detail="Giriş başarısız")
    if rol == "admin":
        for gorev in gorevler:
            if gorev.id == gorev_id:
                gorev.gorev_zamani = guncellenmis_gorev.gorev_zamani
                gorev.gorev_basligi = guncellenmis_gorev.gorev_basligi
                gorev.gorev_konusu = guncellenmis_gorev.gorev_konusu
                gorev.durum = guncellenmis_gorev.durum  
                return {"message": f"Görev {gorev_id} başarıyla güncellendi"}
    else:
        for gorev in gorevler:
            if gorev.id == gorev_id:
                gorev.durum = guncellenmis_gorev.durum  
                return {"message": f"Görev {gorev_id} durumu başarıyla güncellendi"}
    raise HTTPException(status_code=404, detail=f"ID'si {gorev_id} olan görev bulunamadı")

@app.delete("/gorev_sil/{gorev_id}")
def gorev_sil(email: str, sifre: str, gorev_id: int):
    rol = giris_kontrol(email, sifre)
    if not rol:
        raise HTTPException(status_code=401, detail="Giriş başarısız")
    if rol != "admin":
        raise HTTPException(status_code=403, detail="Sadece yönetici görev silebilir")
    for gorev in gorevler:
        if gorev.id == gorev_id:
            gorev.silinmis_mi = True
            return {"message": f"Görev {gorev_id} başarıyla silindi"}
    raise HTTPException(status_code=404, detail=f"ID'si {gorev_id} olan görev bulunamadı")
