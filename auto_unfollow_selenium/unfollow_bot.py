from selenium import webdriver
from selenium.webdriver.common.by import By

import pickle,sqlite3,time,random,threading,sys
sys.path.append("E:/Python/instagram_automation/")
import paths

class UnfollowBot():

    def __init__(self,speed):
        self.speed = speed

        self.scroll_repeat_count = int(2 * speed) 
        self.unfollow_min_time = int(225 / speed) # Ciddi: 225 - 45 sn - 5. Kademe
        self.unfollow_max_time = int(300 / speed) # Ciddi: 300 - 60 sn - 5. Kademe
        self.scroll_min_time = 0 
        scroll_max_time_list = [4,4,4,4,3,3,3,2,2,1,1] 
        self.scroll_max_time = scroll_max_time_list[speed-1] 
    

    def create_login_db(self):
        conn = sqlite3.connect(paths.login_db_path)
        cursor = conn.cursor()
        return conn,cursor
    
    def create_auto_unfollow_db(self):
        conn = sqlite3.connect(paths.auto_unfollow_db_path)
        cursor = conn.cursor()
        return conn,cursor

    def create_account_informations_db(self):
        conn = sqlite3.connect(paths.account_informations_db_path)
        cursor = conn.cursor()
        return conn,cursor
    


    def create_browser(self):
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

        self.browser = webdriver.Firefox(options=option)
        
    def load_cookies(self):
        try:
            self.browser.get("https://www.instagram.com")
            cookies = pickle.load(open(paths.cookies_pkl_path,"rb"))
            for cookie in cookies:
                cookie['domain'] = ".instagram.com"
                try:
                    self.browser.add_cookie(cookie)
                except:
                    print("add cookie load_cookies")
        except Exception as e:
            print("cookies load_cookies")

    def get_username_from_database(self):
        (conn,cursor) = self.create_login_db()
        cursor.execute("SELECT (username) FROM Accounts_Data")
        self.username = cursor.fetchone()[0]

    def first_unfollow_process(self):

        # region 1 - Veritabanlarını oluşturma
        (conn_auto_unfollow_db,cursor_auto_unfollow_db) = self.create_auto_unfollow_db()
        (conn_account_informations_db,cursor_account_informations) = self.create_account_informations_db()
        # endregion

        # region 2 - Login hesabının takip listesine girme
        self.browser.get(f"https://www.instagram.com/{self.username}/following")
        self.browser.implicitly_wait(10)
        # endregion

        # region 3 - Takip listesinin sonuna kadar ilerleme
        try:
            follow_dialog_window = self.browser.find_element(By.CSS_SELECTOR,paths.follow_and_follower_dialog_window_css_selector)
            stop_scrolling = False
            follow_count_check_list = []
            while not stop_scrolling:
                self.browser.execute_script("arguments[0].scrollTop += 1000",follow_dialog_window)
                follow_count = len(self.browser.find_elements(By.XPATH, paths.follow_count_from_html_xPath))
                if len(follow_count_check_list) >= self.scroll_repeat_count and len(set(follow_count_check_list[-self.scroll_repeat_count:])) == 1: # GK
                    stop_scrolling = True
                    print("Following list has reached the end. Scroll operation is finished.")
                else:
                    follow_count_check_list.append(follow_count)
                    print(f"You are on {follow_count}. followings. Scroll process is resume.")
                time.sleep(random.uniform(self.scroll_min_time,self.scroll_max_time))
        except Exception as e:
            print("An error occurred during the scroll operation:",e)
        # endregion

        # region 4 - Takip'ten çıkma işlemini gerçekleştirme
        for i in range(1,follow_count+1):
            try:
                follow_username_find = self.browser.find_element(By.CSS_SELECTOR,paths.create_follow_username_css(i)).text
                follow_username_list = follow_username_find.split("\n") # kullanıcı adı, isim, takip durumu liste olarak verir.
                follow_username = follow_username_list[0] # kullanıcı adını verir.

                cursor_auto_unfollow_db.execute("SELECT * FROM BlackList WHERE username = ?", (follow_username,))
                is_in_blacklist = cursor_auto_unfollow_db.fetchone()

                if not is_in_blacklist:
                    cursor_account_informations.execute("SELECT * FROM Non_Mutual_Followers WHERE username=?",(follow_username,))
                    is_non_mutual = cursor_account_informations.fetchone()
                    if is_non_mutual:                   
                        self.browser.find_element(By.CSS_SELECTOR,paths.create_unfollow_button_first_stage_css(i)).click() # Takipten çıkma butonuna basıldı.
                        # Takipten çıkma butonu ikinci basamak
                        self.browser.find_element(By.CSS_SELECTOR,paths.unfollow_button_second_stage_css_selector).click() 

                        # Takipten çıkılan kişiyi terminale yazdırma
                        line = "-" * (50-len(follow_username))
                        random_time = random.uniform(self.unfollow_min_time,self.unfollow_max_time)
                        print(f"{i}. {follow_username} has been unfollowed. The next operation is {random_time} seconds later..{line}")
                        time.sleep(random_time)

                        try:
                            cursor_account_informations.execute("DELETE FROM Follows WHERE username = ?",(follow_username,))
                            cursor_account_informations.execute("DELETE FROM Non_Mutual_Followers WHERE username = ?",(follow_username,))
                            conn_account_informations_db.commit()
                        except Exception as e:
                            print("Could not be deleted from the database:",e)
                    else:
                        print(f"{i}. {follow_username} user is a mutual user.")
                else:
                    print(f"{i}. {follow_username}'s on the blacklist, so no unfollowed.")
            except Exception as e:
                print("unfollow process:",e)
        # endregion

    def next_unfollow_process(self):

        # region 1 - Veritabanlarını oluşturma 
        (conn_auto_unfollow_db,cursor_auto_unfollow_db) = self.create_auto_unfollow_db()
        (conn_account_informations_db,cursor_account_informations) = self.create_account_informations_db()
        # endregion

        # region 2 - Veritabanından sayıları alıyoruz.
        cursor_account_informations.execute("SELECT COUNT(*) FROM Non_Mutual_Followers")
        rest_of_nmutual_count = cursor_account_informations.fetchone()[0]

        cursor_auto_unfollow_db.execute("SELECT COUNT(*) FROM BlackList")
        black_list_count = cursor_auto_unfollow_db.fetchone()[0]
        # endregion
        
        # region 3 - Döngü oluşturuyoruz.
        stop_processing = False
        while not stop_processing:
            if int(rest_of_nmutual_count) - int(black_list_count) != 0: # Eğer kalan non-mutual listesi elemanı 0 değilse first_unfollow_process işleminin tekrar yapılmasını sağlar.
                print(f"Since the number of remaining non-mutuals is {rest_of_nmutual_count}, the process will be repeated.")
                self.first_unfollow_process()
            else:
                print("The transaction was terminated as there were no more non-reciprocal followers.")
                stop_processing = True
        # endregion


    def start_unfollow_bot(self):
        threading.Thread(target=self.run_unfollow_bot).start()

    def run_unfollow_bot(self):
        t1 = threading.Thread(target=self.create_browser)
        t1.start()
        t1.join()

        t2 = threading.Thread(target=self.load_cookies)
        t2.start()
        t2.join()

        t3 = threading.Thread(target=self.get_username_from_database)
        t3.start()
        t3.join()

        t4 = threading.Thread(target=self.first_unfollow_process)
        t4.start()
        t4.join()

        t5 = threading.Thread(target=self.next_unfollow_process)
        t5.start()
        t5.join()
