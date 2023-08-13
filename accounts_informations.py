import threading,paths,sqlite3,random,time,pickle
import tkinter as tk
from tkinter import font,scrolledtext
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from auto_unfollow_sel import lists_and_counts
from PIL import Image,ImageTk,ImageDraw

class AccountsInformationsWindow():

    def __init__(self,parent_frame):
        self.parent_frame = parent_frame

        self.first_label_frame_background_color = "ivory"
        self.second_label_frame_background_color = "aliceblue"
        self.third_label_frame_background_color = "lightsteelblue"

        self.delete_follower_list_checkbutton_Boolean_Var = tk.BooleanVar(value=False)
        self.delete_followup_list_checkbutton_Boolean_Var = tk.BooleanVar(value=False)
        self.scrap_follower_list_checkbutton_Boolean_Var = tk.BooleanVar(value=False)
        self.scrap_followup_list_checkbutton_Boolean_Var = tk.BooleanVar(value=True)

        self.scroll_min_time = 0 # Takip ya da takipçi çekilme sürecinde en düşük scroll zamanıdır.
        self.scroll_max_time = 1 # Takip ya da takipçi çekilme sürecinde en yüksek scroll zamanıdır.
        self.scroll_max_repeat_count = 20 # Takip ya da takipçi çekilme sürecinde kaç tekrara düştüğü zaman scroll işleminin biteceğini belirler.
        self.margin_of_error = 5 # Takip ya da takipçi çekilme sürecinde eksik kaç takipçi ya da takip kabul edilebilir olsun?

    def configure_fonts(self,weight,size):
        custom_font = font.Font(weight=weight,size=size,family="Calibri")
        return custom_font
    
    def create_account_informations_db(self):
        conn = sqlite3.connect(paths.account_informations_db_path)
        cursor = conn.cursor()
        return conn,cursor
    
    def create_accounts_db(self):
        conn = sqlite3.connect(paths.login_db_path)
        cursor = conn.cursor()
        return conn,cursor

    def create_auto_unfollow_db(self):
        conn = sqlite3.connect(paths.auto_unfollow_db_path)
        cursor = conn.cursor()
        return conn,cursor

    def create_browser(self):
        # region in proxy_list içerisinden rastgele bir proxy çekme
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

        # option.add_argument("-profile") # # temporary serious opening - Giriş yapılmış halde bıraktığı için iptal ettim.
        # option.add_argument(paths.firefox_proile_path) # temporary serious opening - Giriş yapılmış halde bıraktığı için iptal ettim.
        option.set_preference("network.proxy.type", 1)
        option.set_preference("network.proxy.http", PROXY_HOST)
        option.set_preference("network.proxy.http_port", PROXY_PORT)
        option.set_preference("dom.webdriver.enabled", False)
        option.set_preference('useAutomationExtension', False)
        option.set_capability("unhandledPromptBehavior", "ignore")

        browser = webdriver.Firefox(options=option)
        return browser
    
    def create_components(self):

        # region 1 - First Label Frame - Pilot Hesap Giriş Butonu
        self.first_label_frame = tk.LabelFrame(self.parent_frame,bg=self.first_label_frame_background_color,border=False)
        self.first_label_frame.grid(row=0,column=0,padx=10,pady=10)

        pilot_account_check_label = tk.Label(self.first_label_frame,text="Eğer yedek bir hesap girişi yapmadıysanız program çalışmaz, bu yüzden aşağıdaki butona tıklayıp yedek bir hesaba giriniz!",fg="red",font=self.configure_fonts("bold",10))
        pilot_account_check_label.grid(row=0,column=0,padx=10,pady=(10,5))

        pilot_account_login_page_button = tk.Button(self.first_label_frame,text="Entry to Pilot Account Login Page",command=self.create_first_label_frame_toplevel_window,font=self.configure_fonts("bold",10))
        pilot_account_login_page_button.grid(row=1,column=0,padx=10,pady=10,sticky="we")

        for widget in self.first_label_frame.winfo_children():
            widget.configure(bg = self.first_label_frame_background_color)
        # endregion

        # region 2 - Second Label Frame - Sayılar ve Listeler
        # Not: Buradaki tüm sayılar manuel olarak güncellenmemeli. Sadece update_from_beginning fonksiyonunda ve takip - takipçi alımı sonrası yapılmalıdır.
        self.second_label_frame = tk.LabelFrame(self.parent_frame,bg=self.second_label_frame_background_color,border=False)
        self.second_label_frame.grid(row=1,column=0,padx=10,pady=10)

        # region Followers Count & List
        followers_count_and_list_button = tk.Button(self.second_label_frame,text="Followers Count & List",width=30,font=self.configure_fonts("bold",10),command=lambda: self.create_second_label_frame_toplevel_windows("Followers Count & List"))
        followers_count_and_list_button.grid(row=0,column=0)

        self.followers_count_label = tk.Label(self.second_label_frame,text="0",font=self.configure_fonts("bold",60))
        self.followers_count_label.grid(row=1,column=0)
        # endregion

        # region Follow-ups Count & List  
        followups_count_and_list_button = tk.Button(self.second_label_frame,text="Follow-ups Count & List",width=30,font=self.configure_fonts("bold",10),command=lambda: self.create_second_label_frame_toplevel_windows("Follow-ups Count & List"))
        followups_count_and_list_button.grid(row=0,column=1)

        self.followups_count_label = tk.Label(self.second_label_frame,text="0",font=self.configure_fonts("bold",60))
        self.followups_count_label.grid(row=1,column=1)
        # endregion

        # region Mutual Followers Count & List
        mutual_followers_count_and_list_button = tk.Button(self.second_label_frame,text="Mutual Followers Count & List",width=30,font=self.configure_fonts("bold",10),command=lambda: self.create_second_label_frame_toplevel_windows("Mutual Followers Count & List"))
        mutual_followers_count_and_list_button.grid(row=0,column=2)

        self.mutual_followers_count_label = tk.Label(self.second_label_frame,text="0",font=self.configure_fonts("bold",60))
        self.mutual_followers_count_label.grid(row=1,column=2)
        # endregion

        # region Non Mutual Followers Count & List
        non_mutual_followers_count_and_list_button = tk.Button(self.second_label_frame,text="Non Mutual Followers Count & List",width=30,font=self.configure_fonts("bold",10),command=lambda: self.create_second_label_frame_toplevel_windows("Non Mutual Followers Count & List"))
        non_mutual_followers_count_and_list_button.grid(row=2,column=0)

        self.non_mutual_followers_count_label = tk.Label(self.second_label_frame,text="0",font=self.configure_fonts("bold",60))
        self.non_mutual_followers_count_label.grid(row=3,column=0)
        # endregion

        # region Fan Followers Count & List
        fan_followers_count_and_list_button = tk.Button(self.second_label_frame,text="Fan Followers Count & List",width=30,font=self.configure_fonts("bold",10),command=lambda: self.create_second_label_frame_toplevel_windows("Fan Followers Count & List"))
        fan_followers_count_and_list_button.grid(row=2,column=1)

        self.fan_followers_count_label = tk.Label(self.second_label_frame,text="0",font=self.configure_fonts("bold",60))
        self.fan_followers_count_label.grid(row=3,column=1)
        # endregion
      
        for widget in self.second_label_frame.winfo_children():
            widget.grid_configure(padx=10,pady=10)
            widget.configure(bg=self.second_label_frame_background_color)
        # endregion

        # region 3 - Third Label Frame - Takip ve Takipçi Listelerini Oluşturma
        self.third_label_frame = tk.LabelFrame(self.parent_frame,bg=self.third_label_frame_background_color,border=False)
        self.third_label_frame.grid(row=2,column=0,padx=10,pady=(0,10))

        # region Check Button's
        self.delete_follower_list_checkbutton = tk.Checkbutton(self.third_label_frame,text="Delete Follower List",onvalue=True,offvalue=False,variable=self.delete_follower_list_checkbutton_Boolean_Var,font=self.configure_fonts("bold",10),bg="lightsteelblue")
        self.delete_follower_list_checkbutton.grid(row=0,column=0)

        self.delete_followup_list_checkbutton = tk.Checkbutton(self.third_label_frame,text="Delete Follow-up List",onvalue=True,offvalue=False,variable=self.delete_followup_list_checkbutton_Boolean_Var,font=self.configure_fonts("bold",10),bg="lightsteelblue")
        self.delete_followup_list_checkbutton.grid(row=0,column=1)

        self.follower_list_scrap = tk.Checkbutton(self.third_label_frame,text="Follower List Scrap",onvalue=True,offvalue=False,variable=self.scrap_follower_list_checkbutton_Boolean_Var,font=self.configure_fonts("bold",10),bg="lightsteelblue")
        self.follower_list_scrap.grid(row=0,column=2)

        self.followup_list_scrap = tk.Checkbutton(self.third_label_frame,text="Follow-up List Scrap",onvalue=True,offvalue=False,variable=self.scrap_followup_list_checkbutton_Boolean_Var,font=self.configure_fonts("bold",10),bg="lightsteelblue")
        self.followup_list_scrap.grid(row=0,column=3)
        # endregion

        # region Profile Photo
        self.profile_photo = tk.Label(self.third_label_frame,text="Profile Photo",font=self.configure_fonts("bold",13),bg="white")
        self.profile_photo.grid(row=1,column=0,rowspan=4)
        # endregion 

        # region Follower and Follow-up Count Table's
        follower_count_title_from_profile_link = tk.Label(self.third_label_frame,text="Top Follower Count",font=self.configure_fonts("bold",12))
        follower_count_title_from_profile_link.grid(row=1,column=1)
        self.follower_count_label_from_profile_link = tk.Label(self.third_label_frame,text="0",font=self.configure_fonts("bold",30))
        self.follower_count_label_from_profile_link.grid(row=2,column=1)

        followup_count_title_from_profile_link = tk.Label(self.third_label_frame,text="Top Follow-up Count",font=self.configure_fonts("bold",12))
        followup_count_title_from_profile_link.grid(row=1,column=2)
        self.followup_count_label_from_profile_link = tk.Label(self.third_label_frame,text="0",font=self.configure_fonts("bold",30))
        self.followup_count_label_from_profile_link.grid(row=2,column=2)

        follower_count_title_from_database = tk.Label(self.third_label_frame,text="Follower Count From Database",font=self.configure_fonts("bold",12))
        follower_count_title_from_database.grid(row=3,column=1)
        self.follower_count_label_from_database = tk.Label(self.third_label_frame,text="0",font=self.configure_fonts("bold",30))
        self.follower_count_label_from_database.grid(row=4,column=1)

        followup_count_title_from_database = tk.Label(self.third_label_frame,text="Follow-up Count From Database",font=self.configure_fonts("bold",12))
        followup_count_title_from_database.grid(row=3,column=2)
        self.followup_count_label_from_database = tk.Label(self.third_label_frame,text="0",font=self.configure_fonts("bold",30))
        self.followup_count_label_from_database.grid(row=4,column=2)
        # endregion

        # region Start Button
        follow_and_followup_list_creating_button = tk.Button(self.third_label_frame,text="Start",font=self.configure_fonts("bold",12),command=self.start_scraping)
        follow_and_followup_list_creating_button.grid(row=1,column=3,rowspan=4)
        # endregion

        for widget in self.third_label_frame.winfo_children():
            widget.grid_configure(padx=10,pady=10,sticky="nsew")
            widget.configure(background=self.third_label_frame_background_color)
        # endregion

    def get_login_account_username(self): # Login hesabının kullanıcı adının alınması
        try:
            (conn,cursor) = self.create_accounts_db()
            cursor.execute("SELECT username FROM Accounts_Data")
            self.username_login_account = cursor.fetchone()[0]
        except Exception as e:
            print("accounts.db'ye başlanırken sorun oluştu: ",e)

    def get_profile_photo(self): # Profilden fotoğrafın alınması
        browser = self.create_browser()

        try: # Pilot hesabın çerezlerini yükleme
            browser.get("https://www.instagram.com")
            cookies = pickle.load(open(paths.cookies_pilot_account_path,"rb"))
            for cookie in cookies:
                cookie['domain'] = ".instagram.com"
                try:
                    browser.add_cookie(cookie)
                except:
                    print("Cookieler yüklenemedi!")
        except Exception as e:
            print(e,"LoadLoginAccountCookies")
        
        try: # Profil fotoğrafını dosyaya yükleme
            browser.get(f"https://www.instagram.com/{self.username_login_account}")
            # browser.get(f"https://www.instagram.com/ogretmenler.sayfasi") # test - Buradan profil fotoğrafı çekme işlemi her profilde çalışıyor mu diye bak.
            element = WebDriverWait(browser, 10).until(EC.visibility_of_element_located((By.CSS_SELECTOR,paths.profile_photo_css_selector)))
            time.sleep(3) # 3 saniye beklemeli yoksa fotoğraf doğru yüklenmiyor.
            element.screenshot(paths.profile_photo_png_path)
            browser.quit()
        except Exception as e:
            print("Ekran fotoğrafı çekilirken bir sorun oluştu: ",e)
            
    def show_profile_photo(self): # Profil fotoğrafının programa yansıtılması
        image = Image.open(paths.profile_photo_png_path).resize((100,100))
        mask = Image.new("L",image.size,0)
        draw = ImageDraw.Draw(mask)
        draw.ellipse((0,0,image.size[0],image.size[1]),fill=255)
        image = Image.composite(image,Image.new("RGBA",image.size,(255,255,255,0)),mask)

        photo = ImageTk.PhotoImage(image)
        self.profile_photo.config(image=photo)
        self.profile_photo.image = photo

        image.close()
        mask.close()

    def scrap_process(self): # Takip ve takipçi listesinin çekilme süreci
        delete_follower_list_or_not = self.delete_follower_list_checkbutton_Boolean_Var.get()
        delete_followup_list_or_not = self.delete_followup_list_checkbutton_Boolean_Var.get()
        scrap_follower_list_or_not = self.scrap_follower_list_checkbutton_Boolean_Var.get()
        scrap_followup_list_or_not = self.scrap_followup_list_checkbutton_Boolean_Var.get()

        lists_and_counts.FollowAndFollowerList(
            delete_follower_list_or_not, 
            delete_followup_list_or_not,
            scrap_follower_list_or_not,
            scrap_followup_list_or_not,
            self.scroll_min_time, # scroll min time
            self.scroll_max_time, # scroll max time
            self.scroll_max_repeat_count, # scroll last repeat count
            self.margin_of_error, # margin of error
            ).start_follower_and_following_creating()
        
    def start_scraping(self):
        threading.Thread(target=self.run_scraping).start()

    def run_scraping(self):

        # region t1
        t1 = threading.Thread(target=self.get_login_account_username)

        print("Login hesabının kullanıcı adı veri tabanından alıyor.")
        t1.start()
        t1.join()
        print("Login hesabının kullanıcı adı veritabanından başarıyla alındı.")
        # endregion

        # region t2
        t2 = threading.Thread(target=self.get_profile_photo)

        print("Profil fotoğrafı alınacak.")
        t2.start()
        t2.join()
        print("Profil fotoğrafı alındı.")
        # endregion
        
        # region t3
        t3 = threading.Thread(target=self.show_profile_photo)

        print("Profil fotoğrafı pencereye alınıyor.")
        t3.start()
        t3.join()
        print("Profil fotoğrafı pencerede gösterildi.")
        # endregion

        # region t4
        t4 = threading.Thread(target=self.scrap_process)

        print("Takip ve takipçi sayıları alınacak.")
        t4.start()
        t4.join()
        print("Takip ve takipçi sayıları alındı.")
        # endregion

    def create_second_label_frame_toplevel_windows(self,window_title):
        window = tk.Toplevel()
        window.title(window_title)

        window_text_area = scrolledtext.ScrolledText(window,width = 30,height=30)
        window_text_area.pack(fill="both",expand=True)

        try:
            list_titles = {
                "Followers Count & List": "getFollowerListMembers",
                "Follow-ups Count & List": "getFollowUpListMembers",
                "Mutual Followers Count & List": "getMutualFollowerListMembers",
                "Non Mutual Followers Count & List": "getNonMutualFollowerListMembers",
                "Fan Followers Count & List": "getFanFollowerListMembers"
            }

            if window_title in list_titles:
                usernames = getattr(lists_and_counts.ListMembers(), list_titles[window_title])()

            if usernames:
                for number,username in enumerate(usernames,start=1):
                    window_text_area.insert(tk.END,f"{number}. {username}\n")
        except Exception as e:
            print("create_second_label_frame_toplevel_windows")
        
        window.mainloop()

    def create_first_label_frame_toplevel_window(self):

        def entry_to_database(): # Entry'den alınan bilgileri veritabanına yazdırma
            (conn,cursor) = self.create_account_informations_db()
            username_from_entry = self.username_entry.get()
            password_from_entry = self.password_entry.get()

            cursor.execute("DELETE FROM Pilot_Account")
            cursor.execute("INSERT INTO Pilot_Account (username,password) VALUES (?,?)",(username_from_entry,password_from_entry))
            conn.commit()
        
        def save_pilot_account_cookies(): # Yedek hesaba giriş yapıp çerezlerini yükleme
            try: # Entry bilgileriyle giriş yapma

                username_from_entry = self.username_entry.get()
                password_from_entry = self.password_entry.get()

                # Browser oluşturma
                browser = self.create_browser()
                
                # Sayfa yüklenene kadar bekleme
                browser.get("https://www.instagram.com/")
                browser.implicitly_wait(10)

                username = browser.find_element("name","username")
                password = browser.find_element("name","password")
                username.send_keys(f"{username_from_entry}")
                password.send_keys(f"{password_from_entry}")

                time.sleep(random.uniform(1,2))

                login = browser.find_element(By.XPATH,"//button[@type='submit']")
                login.click()
                # Login butonuna basıldıktan sonra 5-10 saniye arası bekleme (giriş süresi)
                time.sleep(random.uniform(5,10)) # düzeltilmeli - sayfa 5-10 saniyede yüklenmezse sorun olur o yüzden sayfanın yüklenme anına kadar bekletmen lazım.
            except Exception as e:
                print("Giriş yapılırken bir sorun oluştu:",e)

            try: # Cookie'leri yükleme

                cookies = browser.get_cookies()
                pickle.dump(cookies,open(paths.cookies_pilot_account_path,"wb"))

                # Browser'dan ve login sayfasından çıkış yapma
                browser.quit()
                self.pilot_account_login_page.destroy()
                # düzeltilmeli - Giriş yapmadığı zaman uyarı vermiyor, ayarlamadım zaman yok.
            except Exception as e:
                print("Çerezler kaydedilirken bir sorun oluştu:",e)

        def start_login(): # Ana thread
            threading.Thread(target=run_login).start()

        def run_login(): # İş parçacıklarını teker teker çalıştırma
            t1 = threading.Thread(target=entry_to_database)

            print("Bilgiler entry'den alınıp veritabanına yazılıyor.")
            t1.start()
            t1.join()
            print("Bilgiler veritabanına yazdırıldı.")

            t2 = threading.Thread(target=save_pilot_account_cookies)

            print("Çerezler kaydedilecek.")
            t2.start()
            t2.join()
            print("Çerezler kaydedildi.")

        def update_from_beginning_for_login_page(): # pilot_account_login_page için update fonksiyonu

            def create_table_from_beginning(): # Pilot_Account Table Creating
                (conn,cursor) = self.create_account_informations_db()
                cursor.execute("CREATE TABLE IF NOT EXISTS Pilot_Account (username TEXT, password TEXT)")
                conn.commit()
            
            self.pilot_account_login_page_first_label_frame.after(0,create_table_from_beginning) # Login sayfasına tıkladığı zaman Pilot_Account tablosu oluşturulur.
            
            def fill_username_and_password():
                try:
                    (conn,cursor) = self.create_account_informations_db()

                    cursor.execute("SELECT username,password FROM Pilot_Account")
                    username_and_password = cursor.fetchone()
                    if username_and_password is not None:
                        username_from_database = username_and_password[0]
                        password_from_database = username_and_password[1]

                        self.username_entry.insert(0,username_from_database)
                        self.password_entry.insert(0,password_from_database)
                except Exception as e:
                    print("Önceki username ve password alınırken sorun yaşandı:",e)
            
            self.pilot_account_login_page_first_label_frame.after(0,fill_username_and_password)

        # region Components
        self.pilot_account_login_page = tk.Toplevel(self.parent_frame)

        self.pilot_account_login_page_first_label_frame = tk.LabelFrame(self.pilot_account_login_page,border=False)
        self.pilot_account_login_page_first_label_frame.pack()

        # region Username
        username_label = tk.Label(self.pilot_account_login_page_first_label_frame,text="Username:")
        username_label.grid(row=0,column=0,padx=(50,10),pady=(20,5))

        self.username_entry = tk.Entry(self.pilot_account_login_page_first_label_frame)
        self.username_entry.grid(row=0,column=1,padx=(10,50),pady=(20,5))
        # endregion

        # region Password
        password_label = tk.Label(self.pilot_account_login_page_first_label_frame,text="Password:")
        password_label.grid(row=1,column=0,padx=(50,10),pady=(5,20))

        self.password_entry = tk.Entry(self.pilot_account_login_page_first_label_frame)
        self.password_entry.grid(row=1,column=1,padx=(10,50),pady=(5,10))
        # endregion

        # region Login
        login_button = tk.Button(self.pilot_account_login_page_first_label_frame,text="Login",command=start_login)
        login_button.grid(row=2,column=0,columnspan=2,pady=(0,10))
        # endregion

        for widget in self.pilot_account_login_page_first_label_frame.winfo_children():
            widget.configure(font=self.configure_fonts("bold",10))
        # endregion

        update_from_beginning_for_login_page()
        self.pilot_account_login_page.mainloop()
    
    def update_from_beginning(self):

        def update_second_label_frame_counts(): # just beginnig update
            # Mutual, non mutual ve fan followers listeleri follower ve followup listelerine göre tekrar oluşturuluyor.
            lists_and_counts.MutualAndNonMutualList().createMutualFollowerList()
            lists_and_counts.MutualAndNonMutualList().createNonMutualFollowerList()
            lists_and_counts.FanFollowersList().createFanFollowerList()

            follower_count_from_beginning = lists_and_counts.Counts().getFollowerCount()
            self.followers_count_label.config(text=follower_count_from_beginning)

            followup_count_from_beginning = lists_and_counts.Counts().getFollowUpCount()
            self.followups_count_label.config(text=followup_count_from_beginning)

            mutual_count_from_beginning = lists_and_counts.Counts().getMutualFollowerCount()
            self.mutual_followers_count_label.config(text=mutual_count_from_beginning)

            non_mutual_count_from_beginning = lists_and_counts.Counts().getNonMutualFollowerCount()
            self.non_mutual_followers_count_label.config(text=non_mutual_count_from_beginning)

            fan_count_from_beginning = lists_and_counts.Counts().getFanFollowerCount()
            self.fan_followers_count_label.config(text=fan_count_from_beginning)
            self.second_label_frame.after(10000,update_second_label_frame_counts) # test - Ekranı kasarsa kapatılabilir.
        
        self.second_label_frame.after(0,update_second_label_frame_counts)

        def update_third_label_frame_counts(): # repeater update
            follower_count_from_profile_link = lists_and_counts.Counts().getFollowerCountfromProfileLink()
            if follower_count_from_profile_link is not None:
                self.follower_count_label_from_profile_link.config(text=follower_count_from_profile_link)

            followup_count_from_profile_link = lists_and_counts.Counts().getFollowUpCountfromProfileLink()
            self.followup_count_label_from_profile_link.config(text=followup_count_from_profile_link)

            follower_count_from_database = lists_and_counts.Counts().getFollowerCount()
            self.follower_count_label_from_database.config(text=follower_count_from_database)

            followup_count_from_database = lists_and_counts.Counts().getFollowUpCount()
            self.followup_count_label_from_database.config(text=followup_count_from_database)

            self.third_label_frame.after(3000,update_third_label_frame_counts)

        self.third_label_frame.after(0,update_third_label_frame_counts)

        # Fonksiyounsuz - Program başladığı zaman ekranda bilgileri olan profilin fotoğrafı gelmeliydi.
        self.third_label_frame.after(0,self.show_profile_photo)
    
    def run_accounts_informations_window(self):
        self.create_components()
        self.update_from_beginning()
#         self.parent_frame.mainloop() # temporary - Programın bu pencereden açılmasını istiyorsan -> CTRL + K + U
# parent_frame = tk.Tk() # temporary - Programın bu pencereden açılmasını istiyorsan -> CTRL + K + U
# AccountsInformationsWindow(parent_frame).run_accounts_informations_window() # temporary - Programın bu pencereden açılmasını istiyorsan -> CTRL + K + U


# region Notlar:
# düzeltilmeli = Sonradan düzeltilecek bir durumdur.
# test = Bu kısımlardaki ifadelerle test yapılabilir.
# lists_and_count içerisindeki database yolu düzeltilmeli.
# just beginnig update = sadece başta update olanlar
# repeater update = belli aralıklarla sürekli update olanlar
# temporary serious opening

# Pilot_Account Table Creating = Pilot Account tablosunun oluşturulma yeridir.
# endregion

