"""
Import Tafsir References from classical sources
These are cross-references mentioned by classical scholars (Ibn Kathir, Tabari, etc.)
"""
from sqlalchemy import Column, Integer, String, Text, Table
from sqlalchemy.orm import Session
from database import SessionLocal, engine, Base

# Create tafsir reference table
tafsir_reference = Table(
    "tafsir_reference",
    Base.metadata,
    Column("id", Integer, primary_key=True, autoincrement=True),
    Column("source_surah", Integer, nullable=False),
    Column("source_ayat", Integer, nullable=False),
    Column("target_surah", Integer, nullable=False),
    Column("target_ayat", Integer, nullable=False),
    Column("mufassir", String, nullable=True),  # Scholar name
    Column("note_tr", Text, nullable=True),  # Turkish note
)

# Classical tafsir cross-references from Ibn Kathir, Tabari, Qurtubi
TAFSIR_REFS = [
    # Fatiha references
    (1, 5, 51, 56, "İbn Kesir", "Yalnız Sana kulluk ederiz - yaratılış amacı"),
    (1, 6, 6, 87, "Taberi", "Doğru yol - peygamberlerin yolu"),
    (1, 7, 7, 16, "İbn Kesir", "Sapıklar - şeytanın yolundan gidenler"),
    
    # Bakara opening
    (2, 1, 10, 1, "İbn Kesir", "Huruf-u mukattaa - benzer sureler"),
    (2, 2, 10, 57, "Kurtubi", "Muttakiler için hidayet - Yunus'taki açıklama"),
    (2, 3, 8, 2, "Taberi", "Gayba iman - gerçek müminlerin niteliği"),
    (2, 30, 7, 11, "İbn Kesir", "Hz. Adem'in yaratılışı - A'raf'taki detay"),
    (2, 30, 15, 28, "İbn Kesir", "Hz. Adem'in yaratılışı - Hicr'deki detay"),
    (2, 30, 38, 71, "İbn Kesir", "Hz. Adem'in yaratılışı - Sad'daki detay"),
    
    # Trust and reliance
    (2, 45, 2, 153, "Kurtubi", "Sabır ve namaz yardımı"),
    (2, 153, 2, 45, "İbn Kesir", "Sabır nasıl yardım eder - önceki ayet bağlantısı"),
    
    # Musa stories
    (2, 51, 7, 142, "İbn Kesir", "40 gece - A'raf'taki detay"),
    (2, 60, 7, 160, "Taberi", "12 pınar - kabile sayısı bağlantısı"),
    (2, 67, 7, 153, "İbn Kesir", "İnek kıssası - pişmanlık teması"),
    
    # Kıble change
    (2, 142, 2, 150, "Kurtubi", "Kıble değişimi - tekrar vurgu"),
    (2, 144, 2, 149, "İbn Kesir", "Her yerden Mescid-i Haram'a yönelme"),
    
    # Fasting
    (2, 183, 2, 185, "Taberi", "Oruç - Ramazan ayı açıklaması"),
    
    # Hajj
    (2, 196, 22, 28, "İbn Kesir", "Hac - Hacc suresindeki faydalar"),
    (2, 197, 22, 27, "Kurtubi", "Hac ayları - ezan"),
    
    # Ayetel Kursi connections
    (2, 255, 3, 2, "İbn Kesir", "El-Hayy el-Kayyum - Al-i İmran başı"),
    (2, 255, 20, 111, "İbn Kesir", "El-Hayy el-Kayyum - Taha'daki kullanım"),
    (2, 255, 40, 65, "Kurtubi", "El-Hayy - Mümin suresindeki çağrı"),
    
    # Charity
    (2, 261, 2, 265, "Taberi", "İnfak örnekleri - parralel teşbihler"),
    (2, 267, 9, 60, "İbn Kesir", "Zekat - kimlere verilir"),
    
    # Riba / Interest
    (2, 275, 3, 130, "Kurtubi", "Faiz yasağı - Al-i İmran'daki uyarı"),
    (2, 278, 4, 161, "İbn Kesir", "Faiz - Yahudilere yasak"),
    
    # Contract witnesses
    (2, 282, 4, 135, "Taberi", "Şahitlik adaletle yapılmalı"),
    (2, 283, 4, 58, "Kurtubi", "Emanet - güvenilir olma"),
    
    # Al-i Imran
    (3, 7, 11, 1, "İbn Kesir", "Muhkem ve müteşabih - Hud suresi açılışı"),
    (3, 28, 60, 1, "Taberi", "Kafirleri dost edinme - Mümtehine açıklaması"),
    (3, 159, 42, 38, "İbn Kesir", "İstişare - Şura suresi bağlantısı"),
    
    # Women's rights
    (4, 1, 49, 13, "Kurtubi", "Tek nefisten yaratılış - eşitlik"),
    (4, 19, 2, 228, "Taberi", "Kadınlara güzel davranma"),
    (4, 34, 2, 228, "İbn Kesir", "Aile içi sorumluluklar"),
    
    # Justice
    (4, 58, 5, 8, "Kurtubi", "Adalet emri - Maide'deki genişleme"),
    (4, 135, 5, 8, "İbn Kesir", "Adalet şahitliği - paralel"),
    
    # Forgiveness
    (4, 110, 39, 53, "İbn Kesir", "Allah'ın bağışlaması - Zümer rahmeti"),
    (4, 17, 6, 54, "Taberi", "Tövbe kabul şartları"),
    
    # Maide
    (5, 3, 6, 145, "İbn Kesir", "Haram yiyecekler - En'am detayı"),
    (5, 32, 17, 33, "Taberi", "Adam öldürme yasağı - İsra"),
    (5, 38, 24, 2, "Kurtubi", "Hırsızlık cezası - Nur suresi paraleli"),
    
    # En'am connections
    (6, 12, 6, 54, "İbn Kesir", "Rahmet kendisine yazılmış"),
    (6, 151, 17, 23, "Taberi", "On emir listesi - İsra karşılaştırması"),
    
    # Ibrahim story
    (6, 75, 21, 51, "İbn Kesir", "Hz. İbrahim yıldızları görme - Enbiya"),
    (6, 79, 3, 67, "Taberi", "Hanif din - Al-i İmran"),
    
    # Creation
    (7, 54, 10, 3, "İbn Kesir", "Arş'a istiva - Yunus"),
    (7, 54, 32, 4, "Kurtubi", "Altı günde yaratılış - Secde"),
    
    # Adam and Satan
    (7, 11, 2, 30, "İbn Kesir", "Hz. Adem'e secde - Bakara"),
    (7, 12, 38, 76, "Taberi", "Şeytan'ın kibrı - Sad suresi"),
    (7, 23, 20, 121, "İbn Kesir", "Adem'in tövbesi - Taha"),
    
    # Prophets sequence
    (7, 59, 11, 25, "İbn Kesir", "Hz. Nuh - Hud karşılaştırması"),
    (7, 65, 11, 50, "Taberi", "Hz. Hud - Hud suresi detayı"),
    (7, 73, 11, 61, "İbn Kesir", "Hz. Salih - Hud suresi"),
    (7, 85, 11, 84, "Kurtubi", "Hz. Şuayb - Hud suresi"),
    
    # Anfal - Jihad
    (8, 15, 3, 156, "Taberi", "Savaştan kaçmama - Al-i İmran"),
    (8, 41, 59, 7, "İbn Kesir", "Ganimet - Haşr taksimi"),
    
    # Tawba
    (9, 5, 2, 191, "İbn Kesir", "Müşriklerle savaş - Bakara kuralları"),
    (9, 60, 2, 273, "Kurtubi", "Zekat dağıtımı - Bakara fakirler"),
    (9, 103, 2, 277, "Taberi", "Zekat temizler - Bakara"),
    
    # Yunus
    (10, 57, 17, 82, "İbn Kesir", "Şifa - İsra'daki Kur'an şifası"),
    (10, 62, 10, 64, "Taberi", "Allah'ın dostları - devam"),
    
    # Hud - Warnings
    (11, 1, 2, 2, "İbn Kesir", "Muhkem kitap - Bakara"),
    (11, 114, 29, 45, "Taberi", "Namaz günahları önler - Ankebut"),
    
    # Yusuf
    (12, 3, 12, 111, "İbn Kesir", "En güzel kıssa - sonuç ibret"),
    (12, 87, 39, 53, "Kurtubi", "Allah'ın rahmetinden ümit kesmeme"),
    
    # Ra'd
    (13, 28, 2, 152, "Taberi", "Zikir ile kalp huzuru - Bakara"),
    
    # Ibrahim
    (14, 24, 16, 112, "İbn Kesir", "Güzel söz örneği - Nahl"),
    (14, 35, 2, 126, "Kurtubi", "Hz. İbrahim'in duası - Bakara"),
    
    # Nahl
    (16, 90, 4, 58, "Taberi", "Adalet ve ihsan emri - Nisa"),
    (16, 97, 4, 124, "İbn Kesir", "Güzel hayat vaadi - Nisa"),
    
    # Isra
    (17, 23, 31, 14, "İbn Kesir", "Anne baba hakkı - Lokman"),
    (17, 31, 6, 151, "Taberi", "Çocuk öldürme yasağı - En'am"),
    (17, 78, 11, 114, "Kurtubi", "Namaz vakitleri - Hud"),
    
    # Kehf
    (18, 28, 6, 52, "İbn Kesir", "Sabah akşam zikir - En'am"),
    (18, 46, 3, 14, "Taberi", "Dünya malı geçici - Al-i İmran"),
    (18, 110, 41, 6, "Kurtubi", "Ben de sizin gibi insanım - Fussilet"),
    
    # Meryem
    (19, 58, 4, 69, "İbn Kesir", "Nimet verilenler - Nisa"),
    
    # Taha
    (20, 14, 29, 45, "Taberi", "Namaz için zikir - Ankebut"),
    (20, 82, 4, 110, "İbn Kesir", "Tövbe ve amel - Nisa"),
    
    # Enbiya
    (21, 87, 68, 48, "Kurtubi", "Hz. Yunus - Kalem paraleli"),
    
    # Hajj
    (22, 27, 3, 97, "İbn Kesir", "Hac çağrısı - Al-i İmran"),
    (22, 78, 2, 143, "Taberi", "Ümmet-i vasat - Bakara"),
    
    # Müminun
    (23, 1, 70, 22, "İbn Kesir", "Müminler kurtuldu - Mearic"),
    (23, 115, 75, 36, "Kurtubi", "Boşuna mı yarattık - Kıyame"),
    
    # Nur
    (24, 30, 24, 31, "İbn Kesir", "Erkek kadın bakış kurallari"),
    (24, 35, 57, 28, "Taberi", "Nur ayeti - Hadid nur"),
    
    # Furkan
    (25, 63, 31, 18, "Kurtubi", "Yürüyüş adabı - Lokman"),
    (25, 70, 4, 110, "İbn Kesir", "Tövbe edenler - Nisa"),
    
    # Şuara
    (26, 80, 10, 57, "Taberi", "Şifa ve hidayet - Yunus"),
    
    # Neml
    (27, 59, 10, 10, "İbn Kesir", "Hamd Allah'a - Yunus"),
    
    # Kasas
    (28, 77, 2, 201, "Kurtubi", "Dünya ahiret dengesi - Bakara duası"),
    
    # Ankebut
    (29, 45, 20, 14, "İbn Kesir", "Namaz kötülükten alıkoyar - Taha"),
    (29, 46, 3, 64, "Taberi", "Ehli kitapla tartışma - Al-i İmran"),
    
    # Rum
    (30, 21, 7, 189, "İbn Kesir", "Eşler arası huzur - A'raf"),
    
    # Lokman
    (31, 13, 4, 48, "Taberi", "Şirk zulümdür - Nisa"),
    (31, 14, 46, 15, "İbn Kesir", "Anne hakkı - Ahkaf"),
    (31, 18, 17, 37, "Kurtubi", "Kibirden kaçınma - İsra"),
    
    # Secde
    (32, 17, 56, 89, "İbn Kesir", "Gizli nimetler - Vakia"),
    
    # Ahzab
    (33, 21, 60, 6, "Taberi", "Rasulullah örnek - Mümtehine"),
    (33, 35, 9, 71, "İbn Kesir", "Kadın erkek eşitliği - Tövbe"),
    (33, 56, 4, 64, "Kurtubi", "Salavat getirme - Nisa"),
    
    # Fatır
    (35, 28, 39, 9, "İbn Kesir", "Alimler Allah'tan korkar - Zümer"),
    
    # Yasin
    (36, 58, 10, 10, "Taberi", "Cennette selam - Yunus"),
    
    # Sad
    (38, 26, 4, 58, "İbn Kesir", "Adaletle hükmet - Nisa"),
    
    # Zümer
    (39, 9, 58, 11, "Kurtubi", "Alimler bilenler - Mücadele"),
    (39, 53, 4, 110, "İbn Kesir", "Rahmetten ümit kesme - Nisa"),
    
    # Mümin/Gafir
    (40, 60, 2, 186, "Taberi", "Dua edene icabet - Bakara"),
    
    # Fussilet
    (41, 34, 23, 96, "İbn Kesir", "Kötülüğe iyilikle karşılık - Müminun"),
    
    # Şura
    (42, 38, 3, 159, "Kurtubi", "İstişare - Al-i İmran"),
    
    # Zuhruf
    (43, 32, 6, 165, "İbn Kesir", "Derece farkları - En'am"),
    
    # Muhammad
    (47, 15, 76, 5, "Taberi", "Cennet nehirleri - İnsan"),
    
    # Fetih
    (48, 29, 3, 110, "İbn Kesir", "Hayırlı ümmet - Al-i İmran"),
    
    # Hucurat
    (49, 10, 3, 103, "Kurtubi", "Müminler kardeştir - Al-i İmran"),
    (49, 13, 30, 22, "İbn Kesir", "Kavimler, kabileler - Rum"),
    
    # Rahman
    (55, 27, 28, 88, "Taberi", "Baki olan Allah - Kasas"),
    
    # Vakıa
    (56, 79, 33, 33, "İbn Kesir", "Temiz olanlara - Ahzab ehli beyt"),
    
    # Hadid
    (57, 4, 2, 255, "Kurtubi", "Ma'iyet - Ayetel Kursi"),
    (57, 25, 5, 8, "İbn Kesir", "Adalet - Maide"),
    
    # Mücadele
    (58, 11, 35, 10, "Taberi", "Meclis adabı - Fatır"),
    
    # Haşr
    (59, 7, 8, 41, "İbn Kesir", "Fey ve ganimet - Enfal"),
    
    # Saff
    (61, 6, 7, 157, "Kurtubi", "Ahmed müjdesi - A'raf"),
    
    # Cuma
    (62, 9, 29, 45, "İbn Kesir", "Cuma namazı çağrısı - Ankebut"),
    
    # Talak
    (65, 2, 2, 231, "Taberi", "Talak marufla - Bakara"),
    (65, 3, 2, 233, "Kurtubi", "Rızık garantisi - Bakara"),
    
    # Tahrim
    (66, 8, 25, 70, "İbn Kesir", "Nasuh tövbe - Furkan"),
    
    # Mülk
    (67, 3, 7, 54, "Taberi", "Yedi kat gök - A'raf"),
    
    # Kalem
    (68, 4, 21, 107, "İbn Kesir", "Yüce ahlak - Enbiya"),
    
    # Mearic
    (70, 19, 17, 11, "Kurtubi", "İnsan aceleci - İsra"),
    
    # Nuh
    (71, 10, 11, 3, "İbn Kesir", "İstiğfar - Hud"),
    
    # Müzzemmil
    (73, 20, 2, 238, "Taberi", "Gece namazı - Bakara"),
    
    # Müddessir
    (74, 4, 2, 222, "İbn Kesir", "Temizlik - Bakara"),
    
    # Kıyame/İnsan
    (76, 1, 33, 72, "Kurtubi", "İnsan emanet - Ahzab"),
    
    # İnfitar
    (82, 10, 50, 17, "İbn Kesir", "Kiramen katibin - Kaf"),
    
    # Mutaffifin
    (83, 26, 76, 21, "Taberi", "Tesnim - İnsan pınarı"),
    
    # İnşirah
    (94, 5, 65, 7, "İbn Kesir", "Zorlukla beraber kolaylık - Talak"),
    
    # Alak
    (96, 1, 20, 114, "Taberi", "Oku - ilim önemi"),
    
    # Beyyine
    (98, 5, 3, 19, "İbn Kesir", "Din Allah katında İslam - Al-i İmran"),
    
    # Asr
    (103, 3, 90, 17, "Kurtubi", "Sabır ve hak tavsiyesi - Beled"),
    
    # İhlas
    (112, 1, 2, 163, "İbn Kesir", "Tek ilah - Bakara"),
    (112, 4, 42, 11, "Taberi", "Hiçbir şey O'na benzemez - Şura"),
]

def import_tafsir_refs():
    """Import tafsir reference data"""
    db: Session = SessionLocal()
    
    try:
        from sqlalchemy import inspect
        inspector = inspect(engine)
        if 'tafsir_reference' in inspector.get_table_names():
            result = db.execute("SELECT COUNT(*) FROM tafsir_reference").fetchone()
            if result[0] > 0:
                print("Tafsir references already exist. Skipping.")
                db.close()
                return
    except:
        pass
    
    # Create table
    tafsir_reference.create(engine, checkfirst=True)
    
    print("Importing tafsir references...")
    total = 0
    
    for src_s, src_a, tgt_s, tgt_a, mufassir, note in TAFSIR_REFS:
        try:
            db.execute(
                tafsir_reference.insert().values(
                    source_surah=src_s,
                    source_ayat=src_a,
                    target_surah=tgt_s,
                    target_ayat=tgt_a,
                    mufassir=mufassir,
                    note_tr=note
                )
            )
            total += 1
        except:
            pass
    
    db.commit()
    print(f"Imported {total} tafsir references.")
    db.close()

if __name__ == "__main__":
    import_tafsir_refs()
