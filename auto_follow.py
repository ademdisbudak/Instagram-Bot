import tkinter as tk,threading,sqlite3,queue,requests,random,pickle,paths,time
from selenium import webdriver
from selenium.webdriver.common.by import By
from tkinter import ttk
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys
from tkinter import font

class AutoFollowWindow:

    def __init__(self,parent_frame):
        self.parent_frame = parent_frame # main.py'deki self.frames["auto_follow"]'i alabilmek için.
        self.rearranging_proxy_list_checkbutton_Boolean_Var = tk.BooleanVar(value=False) # Proxy List Rearranging default değeridir.
        self.delete_permanent_follow_list_checkbutton_Boolean_Var = tk.BooleanVar(value=False) # Permanent Follow List delete default değeridir.

        self.detected_available_post_count = 0 # Available post count başta hiçbir hesap takip edilmediği için sıfır olur.
        self.detected_permanent_follow_count = 0 # Repeater updater için.
        self.detected_temporary_follow_count = 0 # Repeater updater için.

        self.follow_random_time_min = 0 # temporary serious opening- Program ciddi olarak açıldığı zaman 45 olmalı.
        self.follow_random_time_max = 1 # temporary serious opening - Program ciddi olarak açıldığı zaman 60 olmalı.
        # Yukarıdaki değerler kaç saniyeler aralığında takip yapılacağını gösterir.
    
    def configure_fonts(self,weight):
        custom_font = font.Font(weight=weight,size=10,family="Calibri") # slant,italic,underline,overstrike eklenebilir. (False,True)
        # Genel olarak tüm fontlar buradan yönetilir. Eğer eklenmesi gereken bir şey varsa yukarı ekleyip tüm self.configure_fonts değerlerini buna göre değiştirmelisin.
        return custom_font
        
    def create_components(self):

        # region 1 - First Label Frame - Pencerenin üst kısmındaki componentleri içerir.
        self.first_label_frame = tk.LabelFrame(self.parent_frame,bg="lightsteelblue",border=False)
        self.first_label_frame.grid(row=0,column=0,padx=10,pady=10)

        # region Username to Follow Account
        username_to_follow_label = tk.Label(self.first_label_frame,text="Target account username: ",font=self.configure_fonts("bold"))
        username_to_follow_label.grid(row=0,column=0,padx=(100,3),pady=(20,0),sticky="ew")

        self.username_to_follow_entry = tk.Entry(self.first_label_frame,justify="center",font=self.configure_fonts("bold"),fg="navy")
        self.username_to_follow_entry.grid(row=0,column=1,padx=(5,100),pady=(20,0),sticky="ew")
        # endregion
        
        # region Check Buttons
        rearranging_proxy_list_checkbutton = tk.Checkbutton(self.first_label_frame,text="Rearranging Proxy List",onvalue=True,offvalue=False,variable=self.rearranging_proxy_list_checkbutton_Boolean_Var,font=self.configure_fonts("normal"))
        rearranging_proxy_list_checkbutton.grid(row=1,column=0,padx=5,pady=10)

        delete_permanent_follow_list_checkbutton = tk.Checkbutton(self.first_label_frame,text="Delete Permanent Follow List",onvalue=True,offvalue=False,variable=self.delete_permanent_follow_list_checkbutton_Boolean_Var,font=self.configure_fonts("normal"))
        delete_permanent_follow_list_checkbutton.grid(row=1,column=1,padx=5,pady=10)
        # endregion

        # region Start Follow Button
        self.start_follow_button = tk.Button(self.first_label_frame,text="Start Following",command=self.start_follow,font=self.configure_fonts("bold"))
        self.start_follow_button.grid(row=2,column=0,columnspan=2,sticky="nsew",padx=20,pady=(0,20))
        # endregion

        for widget in self.first_label_frame.winfo_children():
            widget.configure(bg = "lightsteelblue") # Tüm elementlerin arka plan rengini first_label_frame arka planıyla aynı yaptık.
        # endregion

        # region 2 - Second Label Frame - Pencerenin alt kısmındaki componentleri içerir.
        self.second_label_frame = tk.LabelFrame(self.parent_frame,bg="ghostwhite",border=False)
        self.second_label_frame.grid(row=1,column=0,padx=10,pady=10)

        # region Available Post Count
        available_post_count_label = tk.Label(self.second_label_frame,text="Available Post Count",font=self.configure_fonts("bold"))
        available_post_count_label.grid(row=0,column=0,padx=40,pady=(10,5),sticky="nsew")

        self.available_post_count = tk.Label(self.second_label_frame,font="size 72")
        self.available_post_count.grid(row=1,column=0)
        # endregion

        # region Proxy Count & Rearranging Proxy List CheckBox
        proxy_list_member_count_label = tk.Label(self.second_label_frame,text="Proxy List Member Count",font=self.configure_fonts("bold"))
        proxy_list_member_count_label.grid(row=0,column=1,padx=40,pady=(10,5),sticky="nsew")

        self.proxy_list_member_count = tk.Label(self.second_label_frame,font="size 72")
        self.proxy_list_member_count.grid(row=1,column=1)
        # endregion

        # region Temporary Follow Count = program açıldıktan sonraki takip sayısı
        temporary_follow_count_label = tk.Label(self.second_label_frame,text="Temporary Follow Count",font=self.configure_fonts("bold"))
        temporary_follow_count_label.grid(row=2,column=0,pady=(0,5),sticky="nsew")

        self.temporary_follow_count = tk.Label(self.second_label_frame,font="size 72")
        self.temporary_follow_count.grid(row=3,column=0)
        # endregion

        # region Permanent Follow Count = şuana kadarki tüm takip sayısı
        permanent_follow_count_label = tk.Label(self.second_label_frame,text="From Beginning Follow Count",font=self.configure_fonts("bold"))
        permanent_follow_count_label.grid(row=2,column=1,pady=(0,5),sticky="nsew")

        self.permanent_follow_count = tk.Label(self.second_label_frame,font="size 72")
        self.permanent_follow_count.grid(row=3,column=1)
        # endregion

        for widget in self.second_label_frame.winfo_children():
            widget.configure(bg="ghostwhite") # Tüm elementlerin arka plan rengini second_label_frame arka planıyla aynı yaptık.
        # endregion

    def create_auto_follow_db(self): # Her thread ayrı bağlantı istediği için her defasında yeniden bağlantı oluşturmalıyız.
        conn = sqlite3.connect(paths.auto_follow_db_path)
        cursor = conn.cursor()
        return conn,cursor

    def create_browser(self): # Oluşturduğumuz proxy listelerini ve firefox profilini browser'ımıza yüklüyoruz.

        # region in proxy_list Random Proxy Choice
        with open(paths.proxy_list_txt_path,"r") as file: # proxy_list.txt'den dictionary halinde çektiğimiz proxyler
            proxies = file.read().split("\n")
            dict = {}
            for proxy in proxies:
                ip_and_port_list = proxy.split(":")
                ip = ip_and_port_list[0]
                port = ip_and_port_list[1]
                dict[ip] = port

        random_ip = random.choice(list(dict.keys())) # dictionary içerisinden rastgele bir key
        random_port = dict[random_ip] # yukarıdaki key'e ait olan value
        # endregion

        PROXY_HOST = random_ip
        PROXY_PORT = random_port
        print(f"PROXY: ({PROXY_HOST},{PROXY_PORT}) ")

        option = webdriver.FirefoxOptions()

        # option.add_argument("-profile")
        # option.add_argument(paths.firefox_proile_path) 
        option.set_preference("network.proxy.type", 1)
        option.set_preference("network.proxy.http", PROXY_HOST)
        option.set_preference("network.proxy.http_port", PROXY_PORT)
        option.set_preference("dom.webdriver.enabled", False)
        option.set_preference('useAutomationExtension', False)
        option.set_capability("unhandledPromptBehavior", "ignore")

        browser = webdriver.Firefox(options=option)
        return browser
    
    def delete_permanent_follow_list(self): # delete_permanent_follow_list_checkbutton True olursa Permanent_Follow_Count liste elemanları sıfırlanacaktır.
        (conn,cursor) = self.create_auto_follow_db()

        cursor.execute("DELETE FROM Permanent_Follow_Count")
        conn.commit()

    def rearrange_proxies(self): # proxy_list.txt içerisindeki çalışmayan - yavaş proxy'ler silinecektir.
        # Bir sıra (queue) objesi oluşturduk.
        self.q = queue.Queue() 

        # Çalışan proxy'leri ve diğer değişkenleri saklayacağımız listeler ve sayıcılar.
        self.valid_proxies = [] 
        self.count = 0
        self.count_lock = threading.Lock()

        # proxy_list.txt dosyasını okur ve proxy'leri sıraya ekler.
        with open(paths.proxy_list_txt_path,"r") as file:
            proxies = file.read().split("\n")
            for p in proxies:
                self.q.put(p)
        
        # Proxy'leri kontrol edecek fonksiyon.
        def check_proxies():
            while not self.q.empty():
                proxy = self.q.get()
                try:
                    # Belirtilen URL'ye proxy üzerinden istek gönderir.
                    res = requests.get("https://www.instagram.com",proxies={"http":proxy,"https":proxy},timeout=10)
                except:
                    continue
                if res.status_code == 200:
                    with self.count_lock:
                        self.count += 1
                        self.valid_proxies.append(proxy)
                        print(f"{self.count}. {proxy}")
                self.q.task_done()
        
        threads = []
        # 10 adet iş parçacığı oluşturulur ve başlatılır.
        for _ in range(10):
            t = threading.Thread(target=check_proxies)
            threads.append(t)
            t.start()

        # Tüm iş parçacıklarının tamamlanmasını bekler.
        for t in threads:
            t.join()
        
        try:
            # Çalışan proxy'leri proxy_list.txt dosyasına yazar.
            with open(paths.proxy_list_txt_path, "w") as file:
                for index, proxy in enumerate(set(self.valid_proxies)):
                    if index != len(self.valid_proxies) - 1:  # Son satır değilse
                        file.write(proxy + "\n")
                    else:  # Son satırsa
                        file.write(proxy)
        except Exception as e:
            print("proxy_list.txt yazılırken bir hata oldu:",e)  
        print("proxy_list başarıyla düzenlendi.")
    
    def save_entry_to_database(self): # Kullanıcı tarafından girilen entry veritabanına kaydedilir.
        # Kullanıcı tarafından girilen kullanıcı adını alır.
        username_to_follow = self.username_to_follow_entry.get()

         # Veritabanı bağlantısı ve imleci oluşturulur.
        (conn,cursor) = self.create_auto_follow_db()

        # Yeni kullanıcı adını tabloya ekler.
        cursor.execute("INSERT INTO Username_To_Follow (username) VALUES (?)",(username_to_follow,))

         # Değişiklikleri veritabanına kaydeder.
        conn.commit()
    
    def check_account_statu(self): # Hedef hesap durumu kontrol edilir ve post seçimi yapılır.
        # Tarayıcı oluşturulur ve veritabanı bağlantısı ve imleci oluşturulur.
        browser = self.create_browser()
        (conn,cursor) = self.create_auto_follow_db()

        # region Kayıtlı Çerezleri Yükleme Bölgesi
        try:
            browser.get("https://www.instagram.com")
            cookies = pickle.load(open(paths.cookies_pkl_path,"rb"))
            for cookie in cookies:
                cookie["domain"] = ".instagram.com"
                try:
                    browser.add_cookie(cookie)
                except Exception as e:
                    print("Cookieler yüklenemedi: ",e)
        except Exception as e:
            print("load_cookies yüklenirken sorun oluştu: ",e)
        # endregion

        # region Hedef Hesap Durumunu Kontrol Etme Bölgesi
        cursor.execute("SELECT username FROM Username_To_Follow")        
        username = cursor.fetchone()[0]
        
        browser.get(f"https://www.instagram.com/{username}")
        try:
            secret_or_open_account = WebDriverWait(browser,10).until(EC.presence_of_element_located((By.XPATH,paths.secret_or_open_account_xPath)))
            print("Hesap gizli hesap olduğu için takip edilmeye uygun değildir.")
            self.account_is_available = False
        except:
            print("Hesap takip edilmeye uygundur.")
            self.account_is_available = True
        # endregion

        # region Gönderi Seçme Bölgesi
        if self.account_is_available == True:
                self.detected_available_post_count = 0

                for a in range(1,5):
                    for b in range(1,4):

                        # region Post'a tıklama
                        try:
                            browser.find_element(By.TAG_NAME,"article").find_element(By.XPATH,f"div[1]/div/div[{a}]/div[{b}]").click() # Can be Wrong xPath
                        except Exception as e:
                            print("Posta tıklanırken bir hata oluştu:",e)
                        # endregion

                        # region Beğenenlere Tıklama
                        try:
                            like_button = WebDriverWait(browser,10).until(EC.presence_of_element_located((By.XPATH,paths.like_button_xPath)))
                            like_button.click()
                            self.detected_available_post_count += 1
                        except:
                            print("Post sorunlu çıktı.")
                            continue
                        # endregion

                        # region Gönderiyi Kapatma 
                        close_dialog_window = WebDriverWait(browser,10).until(EC.presence_of_element_located((By.XPATH,paths.close_dialog_window_xPath)))
                        close_dialog_window.click()

                        close_post_window = WebDriverWait(browser,10).until(EC.presence_of_element_located((By.XPATH,paths.close_post_window_xPath)))
                        close_post_window.click()
                        # endregion

                browser.quit()
        # endregion

    def following_process(self): # Tüm takip sürecini oluşturur.
        # Tarayıcı ve veri bağlantısı oluşturma
        browser = self.create_browser()
        (conn,cursor) = self.create_auto_follow_db()
        
        # Takip işlemini gerçekleştiren fonksiyon
        def follow_funct(i):
            # Takip butonunu bulma (üzerindeki yazı için)
            follow_control = browser.find_element(By.XPATH,f"/html/body/div[2]/div/div/div[3]/div/div/div[2]/div/div/div[1]/div/div[2]/div/div/div/div/div[2]/div/div[2]/div/div/div[{i}]/div/div/div/div[3]/div/button/div/div") 

            # Kullanıcı adını bulma (kullanıcı adını terminale yazdırmak için)
            user_nick_control = browser.find_element(By.XPATH,f"/html/body/div[2]/div/div/div[3]/div/div/div[2]/div/div/div[1]/div/div[2]/div/div/div/div/div[2]/div/div[2]/div/div/div[{i}]/div/div/div/div[2]/div/div/div/div/div/a/div/div/span")

            # Rastgele bir takip süresi belirleme (init fonksiyonunda değerler değiştirilebilir)
            follow_random_time = random.uniform(self.follow_random_time_min,self.follow_random_time_max)

            if follow_control.text == "Takip Et":
                # follow_control.click() # temporary serious opening

                # Veritabanına takip sayılarını ekleme ve kaydetme
                cursor.execute("INSERT INTO Temporary_Follow_Count VALUES ('1')")
                cursor.execute("INSERT INTO Permanent_Follow_Count VALUES ('1')")
                conn.commit()

                # Print için - daha sonra farklı amaçlarla kullanılabilir - veritabanından bilgileri çekme
                cursor.execute("SELECT COUNT(*) FROM Permanent_Follow_Count")
                self.detected_permanent_follow_count = cursor.fetchone()[0]
                
                cursor.execute("SELECT COUNT(*) FROM Temporary_Follow_Count")
                self.detected_temporary_follow_count = cursor.fetchone()[0]

                print(f"{user_nick_control.text} kullanıcısı takip edildi. Toplam takip sayısı: {self.detected_temporary_follow_count}, başlangıçtan beri:{self.detected_permanent_follow_count}")
                
                # Yukarıda belirlenen rastgele süre kadar beklemek
                time.sleep(follow_random_time)
            else:
                print(f"{user_nick_control.text} kullanıcı zaten takip edilmiş.")
        
        # Tab tuşuna bastıran fonksiyon
        def tab_funct(i):
            for i in range(i):
                action = ActionChains(browser)
                action.key_down(Keys.TAB)
                action.perform()
                
        # region Kayıtlı Çerezleri Yükleme Bölgesi
        try:
            browser.get("https://www.instagram.com")
            cookies = pickle.load(open(paths.cookies_pkl_path,"rb"))
            for cookie in cookies:
                cookie["domain"] = ".instagram.com"
                try:
                    browser.add_cookie(cookie)
                except Exception as e:
                    print("Cookieler yüklenemedi: ",e)
        except Exception as e:
            print("load_cookies yüklenirken sorun oluştu: ",e)
        # endregion
        
        # region Girilen Entry Bilgisini Veritabanından Çekme Bölgesi
        cursor.execute("SELECT username FROM Username_To_Follow")        
        username = cursor.fetchone()[0]
        browser.get(f"https://www.instagram.com/{username}")
        time.sleep(5)
        # endregion
        
        # region Temporary ve Permanent Follow Count Güncelleme Bölgesi
        def update_follow_count():
            self.temporary_follow_count.config(text=self.detected_temporary_follow_count) 
            self.permanent_follow_count.config(text=self.detected_permanent_follow_count)
            self.parent_frame.after(2500,update_follow_count)
        self.parent_frame.after(0,update_follow_count)
        # endregion

        # region Takip Etme Sürecinin Tamamı Bölgesi
        for a in range(1,5):
            for b in range(1,4):

                # region Post'a Tıklama
                try:
                    browser.find_element(By.TAG_NAME,"article").find_element(By.XPATH,f"div[1]/div/div[{a}]/div[{b}]").click() # Can be Wrong xPath
                except Exception as e:
                    print("Posta tıklanırken bir hata oluştu:",e)
                    continue
                # endregion

                # region Beğenenlere Tıklama
                try:
                    like_button = WebDriverWait(browser,10).until(EC.presence_of_element_located((By.XPATH,paths.like_button_xPath)))
                    like_button.click()
                    time.sleep(3)
                except:
                    print("Post sorunlu çıktı ve atlandı.")
                    continue
                # endregion

                # region Takip Süreci
                try:
                    # İlk 6 kişiyi takip etme
                    for i in range(1,7):
                        follow_funct(i)
                    
                    tab_funct(20)

                    # Sonraki 5 kişiyi takip etme
                    for i in range(7,12):
                        follow_funct(i)
                        tab_funct(3)
                    
                    # Sonraki 80 kişiyi takip etme (Her listede en fazla 105 kişi çıkıyor bu yüzden yukarıdakilerle beraber 91 olması makul bir değerdir.)
                    for i in range(80):
                        follow_funct(12)
                        tab_funct(3)
                
                except Exception as e:
                    print("Takip işlemleri sırasında bir sorun oluştu:",e)
                # endregion

                # region Close Post
                close_dialog_window = WebDriverWait(browser,10).until(EC.presence_of_element_located((By.XPATH,paths.close_dialog_window_xPath)))
                close_dialog_window.click()

                close_post_window = WebDriverWait(browser,10).until(EC.presence_of_element_located((By.XPATH,paths.close_post_window_xPath)))
                close_post_window.click()
                # endregion
        # endregion

    def start_follow(self): # Ana thread'ı oluşturur.
        threading.Thread(target=self.run_follow).start()

    def run_follow(self): # Tüm thread'lar burada sırayla gerçekleşir.
        t1 = threading.Thread(target=self.rearrange_proxies)
        t2 = threading.Thread(target=self.delete_permanent_follow_list)
        t3 = threading.Thread(target=self.save_entry_to_database)
        t4 = threading.Thread(target=self.check_account_statu)


        if self.rearranging_proxy_list_checkbutton_Boolean_Var.get() == True:
            print("Proxy listesi olan proxy_list.txt açılıp teker teker deneniyor.(t1)")
            t1.start()
            t1.join()
            print("Yeni proxy'ler yazdırılmıştır.(t1)")

        if self.delete_permanent_follow_list_checkbutton_Boolean_Var.get() == True:
            print("Permanent_Follow_Count tablosu temizleniyor.")
            t2.start()
            t2.join()
            print("Permanent_Follow_Count tablosu temizlendi.")

        print("Username bilgisi entry alanından alınıp veritabanına yazılıyor.(t2)")
        t3.start()
        t3.join()
        print("Username bilgisi veritabanına yazdırıldı.(t2)")

        print("Cookie'ler yüklenip hesap durumu kontrol ediliyor. Eğer hesap uygunsa postlar seçilecek.(t3)")
        t4.start()
        t4.join()
        print("Hesap durumu kontrolü ve post seçim işlemi bitmiştir.(t3)")

        t5 = threading.Thread(target=self.following_process)
        
        print("Takip etme işlemi başlamıştır.")
        t5.start()
        t5.join()
        print("Takip etme işlemi sonlanmıştır.")

    def update_from_beginning(self): # Sadece başta ve sürekli tekrarlanan update'ler gerçekleşir.

        def update_entry(): # Entry alanındaki username'i en son girilen username olarak yazar. # Just Beginnig
            conn = sqlite3.connect(paths.auto_follow_db_path)
            cursor = conn.cursor()

            cursor.execute("SELECT username FROM Username_To_Follow")
            result = cursor.fetchone()
            if result is not None:
                username = result[0]
                self.username_to_follow_entry.insert(0,username)

        self.first_label_frame.after(0,update_entry) 

        def update_available_post_count(): # Available Post Count sayısını her 3 saniyede bir yeniler. # Repeater
            try:
                self.available_post_count.config(text=self.detected_available_post_count)
            except Exception as e:
                print("Available Post Count label'i güncellenirken bir hata oluştu:",e)
            self.second_label_frame.after(3000,update_available_post_count)
        
        self.second_label_frame.after(0,update_available_post_count)

        def update_proxy_list_member_count(): # Proxy List sayısını her 2 saniyede bir yeniler. # Repeater
            try:
                with open(paths.proxy_list_txt_path,"r") as file:
                    proxy_count = sum(1 for line in file)
                    self.proxy_list_member_count.config(text=proxy_count)
            except Exception as e:
                print("Proxy sayısı alınırken hata oluştu:",e)
            self.second_label_frame.after(2000,update_proxy_list_member_count)
                
        self.second_label_frame.after(0,update_proxy_list_member_count)

        def update_follow_count(): # Temporary ve Permanent Follow Count listelerini oluşturup Temporary Follow Count'u sıfırlar. # Just Beginning
            (conn,cursor) = self.create_auto_follow_db()

            # region Permanent Follow Count
            cursor.execute("SELECT COUNT(*) FROM Permanent_Follow_Count")
            result = cursor.fetchone()
            if result is not None:
                permanent_follow_count_from_database = result[0]
                self.permanent_follow_count.config(text=permanent_follow_count_from_database)
            # endregion

            # region Temporary Follow Count
            self.temporary_follow_count.config(text="0") # Temporary Count her zaman başta sıfır olmalıdır. Veritabanından çekmeye gerek yoktur.
            # endregion 
            
        self.second_label_frame.after(0,update_follow_count)
        
    def run_auto_follow_window(self):
        self.create_components()
        self.update_from_beginning()
#         self.parent_frame.mainloop() # temporary - Programın bu pencereden açılmasını istiyorsan -> CTRL + K + U
# parent_frame = tk.Tk() # temporary - Programın bu pencereden açılmasını istiyorsan -> CTRL + K + U
# AutoFollowWindow(parent_frame).run_auto_follow_window() # temporary - Programın bu pencereden açılmasını istiyorsan -> CTRL + K + U



# region Notlar:
# temporary serious opening = Gerçekçi program açılımında değiştirilmesi gerekilen yerlerdir.
# Can be Wrong xPath = xPath'i parçalı olduğu için paths.py'ye almadığımdan herhangi bir hata durumunda bu kısımlara bakabilirsin.
# endregion