from selenium import webdriver
from selenium.webdriver.common.by import By
from tkinter import messagebox
import time,pickle,random,sqlite3,threading,sys
sys.path.append("E:/Python/instagram_automation/")
import paths

class FollowAndFollowerList:

    def __init__(self,delete_follower_list,delete_followup_list,scrap_follower_list,scrap_followup_list,scroll_min_time,scroll_max_time,last_followers,margin_of_error):
        
        self.delete_follower_list = delete_follower_list
        self.delete_followup_list = delete_followup_list
        self.scrap_follower_list = scrap_follower_list
        self.scrap_followup_list = scrap_followup_list
        self.scroll_min_time = scroll_min_time
        self.scroll_max_time = scroll_max_time
        self.last_followers = last_followers
        self.margin_of_error = margin_of_error

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

        options = webdriver.FirefoxOptions()
        # option.add_argument("-profile") # # temporary serious opening - Giriş yapılmış halde bıraktığı için iptal ettim.
        # option.add_argument(paths.firefox_proile_path) # temporary serious opening - Giriş yapılmış halde bıraktığı için iptal ettim.
        options.set_preference("network.proxy.type", 1)
        options.set_preference("network.proxy.http", PROXY_HOST)
        options.set_preference("network.proxy.http_port", PROXY_PORT)
        options.set_preference("dom.webdriver.enabled", False)
        options.set_preference('useAutomationExtension', False)
        options.set_capability("unhandledPromptBehavior", "ignore")

        browser = webdriver.Firefox(options=options)
        return browser

    def create_accounts_db(self):
        conn = sqlite3.connect(paths.login_db_path)
        cursor = conn.cursor()
        return conn,cursor
    
    def create_auto_unfollow_db(self):
        conn = sqlite3.connect(paths.auto_unfollow_db_path)
        cursor = conn.cursor()
        return conn,cursor
    
    def create_accounts_informations_db(self):
        conn = sqlite3.connect(paths.account_informations_db_path)
        cursor = conn.cursor()
        return conn,cursor

    def get_username_login_account(self):
        try:
            (conn,cursor) = self.create_accounts_db()
            cursor.execute("SELECT username FROM Accounts_Data")
            self.login_username = cursor.fetchone()[0]
        except:
            print("get_username_login_account yüklenirken hata oluştu!")

    # 1 - Başlangıçta profile girip takipçi ve takip sayılarını çekmek (Döngü için gerekli bir sayıdır.)
    def get_counts_on_profile_link(self): # Get Followers and Follow-Up Counts On Beggining 
        browser = self.create_browser()
        (conn,cursor) = self.create_accounts_informations_db()

        # region 1 - Pilot hesabın çerezlerini yükleme
        try:
            browser.get("https:/www.instagram.com/")
            cookies = pickle.load(open(paths.cookies_pilot_account_path,"rb"))
            for cookie in cookies:
                cookie['domain'] = ".instagram.com"
                try:
                    browser.add_cookie(cookie)
                except:
                    print("Cookieler yüklenemedi!")
        except:
            print("load_cookies_pilot_account yüklenirken hata oluştu!")
        # endregion

        # region 2 - Profile gidip sayıları veritabanına yazdırma
        browser.get(f"https://www.instagram.com/{self.login_username}")
        browser.implicitly_wait(10)

        account_informations = browser.find_element(By.CSS_SELECTOR,paths.accounts_informations_css_selector).text.split("\n")

        follower_count_from_profile = int(account_informations[4].split(" ")[0])
        followup_count_from_profile = int(account_informations[5].split(" ")[0])

        # Profile Counts tablosu accounts_informations.py başlangıcında accounts_informations.db veritabanında oluşturulmuştur.
        cursor.execute("DELETE FROM Profile_Counts")
        cursor.execute("INSERT INTO Profile_Counts (follower, followup) VALUES (?,?)",(follower_count_from_profile,followup_count_from_profile))
        conn.commit()

        time.sleep(3)
        browser.quit()
        # endregion
    
    # 2 - Başlangıçta Followers ve Follows tablolarını oluşturup seçeneğe göre siliyoruz.
    def clear_list(self):
        (conn,cursor) = self.create_accounts_informations_db()

        # 1 - Takipçi listesi seçime göre silinecek / silinmeyecek.
        try:
            if self.delete_follower_list == True:
                # Followers tablosu accounts_informations.py başlangıcında accounts_informations.db veritabanında oluşturulmuştur.
                cursor.execute("DELETE FROM Followers")
                print("Followers tablosu temizlendi.")
            else:
                print("Followers tablosu yaptığınız seçim sebebiyle temizlenmedi.")
            conn.commit()
        except Exception as e:
            print(e,"Followers tablosu temizlenirken sorun oluştu!")

        # 2 - Takip listesi seçime göre silinecek / silinmeyecek.
        try:
            # Follows tablosu accounts_informations.py başlangıcında accounts_informations.db veritabanında oluşturulmuştur.
            if self.delete_followup_list == True:
                cursor.execute("DELETE FROM Follows")
                print("Follows tablosu temizlendi.")
            else:
                print("Follows tablosu yaptığınız seçim sebebiyle temizlenmedi.")
            conn.commit()
        except Exception as e:
            print(e,"Follows tablosu oluşturulurup temizlenirken hata oluştu!")

    # 3 - Takipçi Listesini Oluşturmak ve Doldurmak
    def create_follower_list(self):
        browser = self.create_browser()
        (conn,cursor) = self.create_accounts_informations_db()

        def FirstScan():
          
            # region 1 - Pilot hesabın çerezlerini yükleme
            try:
                browser.get("https:/www.instagram.com/")
                cookies = pickle.load(open(paths.cookies_pilot_account_path,"rb"))
                for cookie in cookies:
                    cookie['domain'] = ".instagram.com"
                    try:
                        browser.add_cookie(cookie)
                    except:
                        print("Cookieler yüklenemedi!")
            except:
                print("load_cookies_pilot_account yüklenirken hata oluştu!")
            # endregion

            # region 2 - ScrollDown Functions
            try:
                browser.get(f"https://www.instagram.com/{self.login_username}/followers")
                browser.implicitly_wait(5)
                time.sleep(random.uniform(1,3))
                followers_dialog_window = browser.find_element(By.CSS_SELECTOR,paths.follow_and_follower_dialog_window_css_selector)
                followers_list_stop_scrolling = False
                follower_count_check_list = []

                # Eğer "Senin için Önerilenler" kısmı varsa yazandan 30 takipçi az yüklenmiş demektir. Yoksa aynı şekilde devam edilir.
                try:
                    browser.find_element(By.CSS_SELECTOR,".xw7yly9 > span:nth-child(1)")
                    real_followers = follower_count_FHTML - 30
                except:
                    real_followers = follower_count_FHTML

                while not followers_list_stop_scrolling:
                    browser.execute_script("arguments[0].scrollTop += 1000;", followers_dialog_window) 
                    follower_count_FHTML = len(browser.find_elements(By.XPATH,paths.follow_and_follower_count_from_html_xpath))

                    if len(follower_count_check_list) >= self.last_followers and len(set(follower_count_check_list[-self.last_followers:])) == 1 :
                        followers_list_stop_scrolling = True
                        print("İlk döngüde takipçi listesinin sonuna ulaşıldı. Scroll işlemi durduruldu, tablo oluşturulup veriler yazılacak.")
                    else:
                        follower_count_check_list.append(real_followers)
                        scroll_time = random.uniform(self.scroll_min_time,self.scroll_max_time)
                        print(f"{real_followers} takipçi açıldı, scroll devam ediyor. {scroll_time} saniye sonra scroll yapılacak.")
                        time.sleep(scroll_time) # Kaç saniyede bir scroll yapılsın ?

            except Exception as e:
                print(e,"Takipçi listesinin scrolldown aşamasında sıkıntı oluştu!")
            # endregion

            # region 2 - Saving all Followers Usernames
            try:
                followers_list = []

                for i in range(1,real_followers+1):
                    user = browser.find_element(By.CSS_SELECTOR,paths.create_follower_username_css(i)).text
                    user_info_list = user.split("\n") # username,isim,takip durumu şeklinde bilgi verir.
                    followers_username = user_info_list[0]
                    cursor.execute("SELECT * FROM Followers WHERE username = ?",(followers_username,))
                    result = cursor.fetchone()
                    if not result:
                        followers_list.append((followers_username,))
                        line = "-" * (50 - len(followers_username))
                        print(f"{i}. {followers_username} takipçi listende yoktu ve kaydedildi. {line}")
                    else:
                        print(f"{i}. {followers_username} zaten takipçi listesinde kayıtlı.")
                time.sleep(random.uniform(2,4))

                cursor.executemany("INSERT INTO Followers (username) VALUES (?)",followers_list) 
                conn.commit()
                print("Takipçi listesinin taraması yapıldı ve takipçiler veri tabanına kaydı yapıldı.")
            except Exception as e:
                print(e,"Takipçi listesini kaydederken sorun oluştu!")
            time.sleep(random.uniform(3,5))
            # endregion
            
        def NextScans():
            cursor.execute("SELECT follower FROM Profile_Counts")
            follower_count_FP = cursor.fetchone()[0]
            while True:
                cursor.execute("SELECT COUNT(*) FROM Followers")
                result = cursor.fetchone()
                follower_count_FDB = result[0]

                if int(follower_count_FP)-self.margin_of_error >= int(follower_count_FDB):
                    print(f"Profilden alınan takip sayısı {follower_count_FP}, veri tabanından alınan takip sayısı {follower_count_FDB}'dır. Veri tabanı henüz dolmadığı için tarama tekrar yapılacaktır.(Hata payı:{self.margin_of_error})")
                    FirstScan()
                else:
                    print(f"Profilden alınan takipçi sayısı {follower_count_FP}, veri tabanından alınan takipçi sayısı {follower_count_FDB}'dır. Veritabanı doldurulduğu için tarama durmuştur.")
                    browser.quit()
                    break
            time.sleep(random.uniform(3,5))
    
        FirstScan(),NextScans()

    # 4 - Takip Listesini Oluşturmak ve Doldurmak
    def create_followup_list(self):
        browser = self.create_browser()
        (conn,cursor) = self.create_accounts_informations_db()

        def FirstScan():

            # region 1 - Pilot hesabın çerezlerini yükleme
            try:
                browser.get("https:/www.instagram.com/")
                cookies = pickle.load(open(paths.cookies_pilot_account_path,"rb"))
                for cookie in cookies:
                    cookie['domain'] = ".instagram.com"
                    try:
                        browser.add_cookie(cookie)
                    except:
                        print("Cookieler yüklenemedi!")
            except:
                print("load_cookies_pilot_account yüklenirken hata oluştu!")
            # endregion
            
            # region 2 - ScrollDown Functions
            try:
                browser.get(f"https://www.instagram.com/{self.login_username}/following")
                # browser.get(f"https://www.instagram.com/default.py/following") # test = Düşük takip - takipçili bir hesabın üzerinden accounts_informations.py doldurulurması.
                browser.implicitly_wait(5)
                # time.sleep(300) # test - Takip listesine girip 10 dakika bekler.

                followup_dialog_window = browser.find_element(By.CSS_SELECTOR,paths.follow_and_follower_dialog_window_css_selector)
                followup_list_stop_scrolling = False
                followUp_count_check_list = []

                while not followup_list_stop_scrolling:
                    browser.execute_script("arguments[0].scrollTop += 1000;",followup_dialog_window)
                    followup_count_FHTML = len(browser.find_elements(By.XPATH,paths.follow_and_follower_count_from_html_xpath))

                    if len(followUp_count_check_list) >= self.last_followers and len(set(followUp_count_check_list[-self.last_followers:])) == 1 :
                        followup_list_stop_scrolling = True
                        print("İlk döngüde takip listesinin sonuna ulaşıldı. Scroll işlemi durduruldu, tablo oluşturulup veriler yazılacak.")
                    else:
                        followUp_count_check_list.append(followup_count_FHTML)
                        scroll_time = random.uniform(self.scroll_min_time,self.scroll_max_time)
                        print(f"{followup_count_FHTML} takip edilen açıldı, scroll devam ediyor.{scroll_time} saniye sonra scroll yapılacak.")
                        time.sleep(scroll_time) # Kaç saniyede bir scroll yapılsın ?

            except Exception as e:
                print(e,"Takip listesinin scrolldown aşamasında sıkıntı oluştu!")
            # endregion

            # region 3 - Saving All Follow-up Usernames
            try:
                followUps_list = [] 
                for i in range(1,followup_count_FHTML+1):
                    user = browser.find_element(By.CSS_SELECTOR,paths.create_follow_username_css(i)).text
                    user_info_list = user.split("\n") # username,isim,takip durumu şeklinde bilgi verir.
                    followup_username = user_info_list[0]
                    cursor.execute("SELECT * FROM Follows WHERE username = ?",(followup_username,))

                    
                    result = cursor.fetchone()
                    if not result:
                        followUps_list.append((followup_username,))
                        line = "-" * (50 - len(followup_username))
                        print(f"{i}. {followup_username} takip listende yoktu ve kaydedildi. {line}")
                    else:
                        print(f"{i}. {followup_username} zaten takip listende kayıtlı.")
                time.sleep(random.uniform(2,4))

                cursor.executemany("INSERT INTO Follows (username) VALUES (?)",followUps_list)
                conn.commit()
                print(f"Takip listesinin taraması yapıldı ve takiplerin veritabanına kaydı yapıldı.")
            except Exception as e:
                print(e,"Takip listesini kaydedişte bir sıkıntı oluştu!")
            # endregion
            
            time.sleep(random.uniform(3,5))

        def NextScans():
            cursor.execute("SELECT followup FROM Profile_Counts")
            followup_count_FP = cursor.fetchone()[0]
            while True:
                cursor.execute("SELECT COUNT(*) FROM Follows")
                followUp_count_FDB = int(cursor.fetchone()[0])

                if int(followup_count_FP)- int(self.margin_of_error)>= int(followUp_count_FDB):
                    print(f"Profilden alınan takip sayısı {followup_count_FP}, veri tabanından alınan takip sayısı {followUp_count_FDB}'dır. Veri tabanı henüz dolmadığı için tarama tekrar yapılacaktır.(Hata payı:{self.margin_of_error})")
                    FirstScan()
                else:
                    print(f"Profilden alınan takip sayısı {followup_count_FP}, veri tabanından alınan takip sayısı {followUp_count_FDB}'dır. Veritabanı doldurulduğu için tarama durmuştur.")
                    browser.quit()
                    break
            time.sleep(random.uniform(3,5))
        
        FirstScan(),NextScans()

    # 5 - Yukarıdaki 4 Fonksiyonu Çalıştırmak - İş Parçacıkları  
    def run_follower_and_following_creating(self):
        try:
            # region t1 
            t1 = threading.Thread(target=self.get_username_login_account)

            print("t1 başladı.")
            t1.start()
            t1.join()
            print("t1 bitti.")
            # endregion

            # region t2 
            t2 = threading.Thread(target=self.get_counts_on_profile_link)

            print("t2 başladı.")
            t2.start()
            t2.join()
            print("t2 bitti.")
            # endregion

            # region t3 
            t3 = threading.Thread(target=self.clear_list)

            print("t3 başladı.")
            t3.start()
            t3.join()
            print("t3 bitti.")
            # endregion

            t4 = threading.Thread(target=self.create_follower_list)
            t5 = threading.Thread(target=self.create_followup_list)

            if (self.scrap_follower_list == True) and (self.scrap_followup_list==True):
                t4.start()
                t4.join()
                t5.start()
                t5.join()
            elif (self.scrap_follower_list == True) and (self.scrap_followup_list==False):
                t4.start()
                t4.join()
            elif (self.scrap_follower_list == False) and (self.scrap_followup_list==True):
                t5.start()
                t5.join()
            elif (self.scrap_follower_list == False) and (self.scrap_followup_list==False):
                print("Takip ve takipçi listelerinden herhangi biri seçilmediği için tarama yapılamıyor.")
        
        finally:
            # self.conn_accounts_db.close()
            # self.conn_auto_unfollow_db.close()
            time.sleep(3)
            # self.browser.quit() # browser kapatma
    
    # 6 - Ana thread - Başlatıcı Fonksiyon
    def start_follower_and_following_creating(self):
        threading.Thread(target=self.run_follower_and_following_creating).start()

class MutualAndNonMutualList:

    def __init__(self):
        self.conn = sqlite3.connect(paths.account_informations_db_path)
        self.cursor = self.conn.cursor()
    
    # -------------------------------------------------
    # 1 - Mutual Takipçiler Listesini Oluşturmak
    def createMutualFollowerList(self):
        def createTable():
            with self.conn:
                # Mutual_Followers tablosu accounts_informations.py başlangıcında accounts_informations.db veritabanında oluşturulmuştur.
                self.cursor.execute("DELETE FROM Mutual_Followers")
        def findAndInsert():
            self.cursor.execute("SELECT username FROM Follows")
            follows_usernames = [row[0] for row in self.cursor.fetchall()]
            if follows_usernames:
                with self.conn:
                    for username in follows_usernames:
                        self.cursor.execute("SELECT username FROM Followers WHERE username = ?", (username,))
                        result = self.cursor.fetchone()
                        if result:
                            self.cursor.execute("INSERT INTO Mutual_Followers (username) VALUES (?)", (username,))

        createTable()
        findAndInsert()
    # -------------------------------------------------


    # -------------------------------------------------
    # 2 - Non-Mutual Takipçilerin Listesini Oluşturmak
    def createNonMutualFollowerList(self):
        def createTable():
            with self.conn:
                # Non_Mutual_Followers tablosu accounts_informations.py başlangıcında accounts_informations.db veritabanında oluşturulmuştur.
                self.cursor.execute("DELETE FROM Non_Mutual_Followers")

        def findAndInsert():
            self.cursor.execute("SELECT username FROM Follows")
            follows_usernames = [row[0] for row in self.cursor.fetchall()]
            if follows_usernames:
                with self.conn:
                    for username in follows_usernames:
                        self.cursor.execute("SELECT username FROM Mutual_Followers WHERE username = ?", (username,))
                        result = self.cursor.fetchone()
                        if not result:
                            self.cursor.execute("INSERT INTO Non_Mutual_Followers (username) VALUES (?)", (username,))

        createTable()
        findAndInsert()
    # -------------------------------------------------

class BlackList:

    def create_auto_unfollow_db(self):
        conn = sqlite3.connect(paths.auto_unfollow_db_path)
        cursor = conn.cursor()
        return conn,cursor

    def create_account_informations_db(self):
        conn = sqlite3.connect(paths.account_informations_db_path)
        cursor = conn.cursor()
        return conn,cursor

    def createBlackList(self):
        (conn,cursor) = self.create_auto_unfollow_db()
        cursor.execute("CREATE TABLE IF NOT EXISTS BlackList (username TEXT)") # Bu kod auto_unfollow.py pencersinde olacaktır.
        conn.commit()

    def addToBlackList(self,blacklist): # Entry'ye girilen kişileri BlackList'e ekler ve BlackList listesini döndürür.
        (conn_auto_unfollow_db,cursor_auto_unfollow_db) = self.create_auto_unfollow_db()
        (conn_account_information_db,cursor_account_information_db) = self.create_account_informations_db()
        # burada iki adet sql bağlantısı açtık, bu sıkıntı oluşturabilir. blacklist'i accounts_information.db'ye alabilirsin. yukarıdaki iki fonksiyonu silip init içine atabilirsin.
        
        if blacklist:
            cursor_auto_unfollow_db.execute("CREATE TABLE IF NOT EXISTS BlackList (username TEXT)")
            for username in blacklist:
                cursor_account_information_db.execute("SELECT * FROM Non_Mutual_Followers WHERE username=?",(username,))
                there_is_username = cursor_account_information_db.fetchone()
                if there_is_username:
                    cursor_auto_unfollow_db.execute("SELECT * FROM BlackList WHERE username=?",(username,))
                    added_username = cursor_auto_unfollow_db.fetchone()
                    if not added_username:
                        cursor_auto_unfollow_db.execute("INSERT INTO BlackList (username) VALUES (?)", (username,))
                    else:
                        messagebox.showwarning(title="Error!",message="You already add this.")
                else:
                    messagebox.showwarning(title="Error!",message="There is not this username in Non-Followers List.")
            conn_auto_unfollow_db.commit()
            conn_account_information_db.commit()

    def removeFromBlackList(self,blacklist): # Entry'e girilen kişileri BlackList'ten siler ve BlackList listesini döndürür.
        (conn_auto_unfollow_db,cursor_auto_unfollow_db) = self.create_auto_unfollow_db()
        if blacklist:
            cursor_auto_unfollow_db.execute("CREATE TABLE IF NOT EXISTS BlackList (username TEXT)")
            for username in blacklist:
                cursor_auto_unfollow_db.execute("SELECT * FROM BlackList WHERE username=?",(username,))
                there_is_username = cursor_auto_unfollow_db.fetchone()
                if there_is_username:
                    cursor_auto_unfollow_db.execute("DELETE FROM BlackList WHERE username=?",(username,))
                else:
                    messagebox.showwarning(title="Error!",message="There is not this username in BlackList!")
        conn_auto_unfollow_db.commit()

    def removeAll(self): # BlackList'in tamamını siler.
        (conn_auto_unfollow_db,cursor_auto_unfollow_db) = self.create_auto_unfollow_db()
        cursor_auto_unfollow_db.execute("DELETE FROM BlackList")
        conn_auto_unfollow_db.commit()

class FanFollowersList:
        def __init__(self):
            self.conn = sqlite3.connect(paths.account_informations_db_path)
            self.cursor = self.conn.cursor()

        def createFanFollowerList(self):
            # Fan_Followers tablosu accounts_informations.py başlangıcında accounts_informations.db veritabanında oluşturulmuştur.
            self.cursor.execute("DELETE FROM Fan_Followers")

            self.cursor.execute("SELECT username FROM Followers")

            follow_list = [row[0] for row in self.cursor.fetchall()]
            for username in follow_list:
                self.cursor.execute("SELECT * FROM Follows WHERE username = ?",(username,))
                is_followup_fan_follower = self.cursor.fetchone()
                if is_followup_fan_follower is None: # Eğer takip listesinde yoksa:
                    fan_follower = username
                    self.cursor.execute("INSERT INTO Fan_Followers (username) VALUES (?)",(fan_follower,))
            self.conn.commit()

class ListMembers:

    def create_accounts_informations_db(self):
        conn = sqlite3.connect(paths.account_informations_db_path)
        cursor = conn.cursor()
        return conn,cursor
    
    def create_auto_unfollow_db(self):
        conn = sqlite3.connect(paths.auto_unfollow_db_path)
        cursor = conn.cursor()
        return conn,cursor


    def getFollowerListMembers(self):
        (conn,cursor) = self.create_accounts_informations_db()
        cursor.execute("SELECT username FROM Followers ORDER BY username")
        follower_list = [row[0] for row in cursor.fetchall()]
        return follower_list

    def getFollowUpListMembers(self):
        (conn,cursor) = self.create_accounts_informations_db()
        cursor.execute("SELECT username FROM Follows ORDER BY username")
        followUp_list = [row[0] for row in cursor.fetchall()]
        return followUp_list

    def getMutualFollowerListMembers(self):
        (conn,cursor) = self.create_accounts_informations_db()
        cursor.execute("SELECT username FROM Mutual_Followers ORDER BY username")
        mutual_follower_list = [row[0] for row in cursor.fetchall()]
        return mutual_follower_list

    def getNonMutualFollowerListMembers(self):
        (conn,cursor) = self.create_accounts_informations_db()
        cursor.execute("SELECT username FROM Non_Mutual_Followers ORDER BY username")
        non_mutual_follower_list = [row[0] for row in cursor.fetchall()]
        return non_mutual_follower_list
    
    def getBlackListMembers(self):
        (conn,cursor) = self.create_auto_unfollow_db()
        cursor.execute("SELECT username FROM BlackList")
        black_list = [row[0] for row in cursor.fetchall()]
        return black_list
    
    def getFanFollowerListMembers(self):
        (conn,cursor) = self.create_accounts_informations_db()
        cursor.execute("SELECT username FROM Fan_Followers")
        fan_followers = [row[0] for row in cursor.fetchall()]
        return fan_followers
        
class Counts:
    
    def __init__(self):
        self.conn = sqlite3.connect(paths.account_informations_db_path)
        self.cursor = self.conn.cursor()

    # -------------------------------------------------
    # 1 - Takipçi sayılarını veritabanından çeker (auto_unfolllow.db/Followers)
    def getFollowerCount(self):
        self.cursor.execute("SELECT COUNT(*) FROM Followers")
        result = self.cursor.fetchone()
        if result is not None:
            count = result[0]
            return count
    # -------------------------------------------------

    # -------------------------------------------------
    # 2 - Takip sayılarını veritabanından çeker (auto_unfollow.db/Follows)
    def getFollowUpCount(self):
        self.cursor.execute("SELECT COUNT(*) FROM Follows")
        result = self.cursor.fetchone()
        if result is not None:
            count = result[0]
            return count

    # -------------------------------------------------
    # 3 - Mutual takipçi sayısını verir.
    def getMutualFollowerCount(self):
        self.cursor.execute("SELECT COUNT(*) FROM Mutual_Followers")
        result = self.cursor.fetchone()
        if result is not None:
            count = result[0]
            return count
    # -------------------------------------------------

    # -------------------------------------------------
    # 4 - Non Mutual takipçi sayısını verir.
    def getNonMutualFollowerCount(self):
        self.cursor.execute("SELECT COUNT(*) FROM Non_Mutual_Followers")
        result = self.cursor.fetchone()
        if result is not None:
            count = result[0]
            return count
    # -------------------------------------------------

    def getFollowerCountfromProfileLink(self):
        self.cursor.execute("SELECT follower FROM Profile_Counts")
        result = self.cursor.fetchone()
        if result is not None:
            follower_count_FPL = result[0] 
            return follower_count_FPL
    
    def getFollowUpCountfromProfileLink(self):
        self.cursor.execute("SELECT followup FROM Profile_Counts")
        result = self.cursor.fetchone()
        if result is not None:
            followUp_count_FPL = result[0]
            return followUp_count_FPL
    
    def getFanFollowerCount(self):
        self.cursor.execute("SELECT COUNT(*) FROM Fan_Followers")
        result = self.cursor.fetchone()
        if result is not None:
            count = result[0]
            return count


# temporary serious opening 
# test = Bu kısımlardaki ifadelerle test yapılabilir.
# test = Düşük takip - takipçili bir hesabın üzerinden accounts_informations.py doldurulurması.
# browser kapatma