import tkinter as tk
import subprocess,sqlite3,paths,threading,time,random,pickle
from selenium import webdriver
from selenium.webdriver.common.by import By
from PIL import Image,ImageTk
from pygame import mixer

class LoginWindow:

    def __init__(self):
        self.login_window = tk.Tk()
        self.account_database_username = ""
        self.account_database_password = ""
        self.browser = None
        self.login_success_statu = False
        self.t1 = None
        self.logo_img = None
        self.playing = False

    def configure_properties(self):
        self.login_window.title("İnstagram Bot Application")

        screen_width = self.login_window.winfo_screenwidth()
        screen_height = self.login_window.winfo_screenheight()
        width = 290
        height = 460

        x = (screen_width - width) // 2
        y = (screen_height - height) // 2
        self.login_window.geometry(f"{width}x{height}+{x}+{y}")

    def create_components(self):

        # region Label Frame
        label_widget = tk.Label(self.login_window, text="Login Page",bg="white")
        self.account_login_page = tk.LabelFrame(self.login_window,text="Login Page",labelanchor="n",labelwidget=label_widget,bg="white")
        self.account_login_page.grid(row=0,column=0,padx=15,pady=15)
        # endregion
        
        # region Welcome Part
        self.logo_img = Image.open(paths.logo_png_path)
        self.logo_img = ImageTk.PhotoImage(self.logo_img)

        logo_label = tk.Label(self.account_login_page,image=self.logo_img)
        logo_label.grid(row=0,column=0,columnspan=2)

        welcome_label = tk.Label(self.account_login_page,text="Welcome to my instagram automation!") 
        welcome_label.grid(row=1,column=0,columnspan=2)
        # endregion

        # region Username
        self.username_String_Var = tk.StringVar()
        self.username_String_Var.trace_add("write",self.alert_for_username)
        self.username_warning_label = tk.Label(self.account_login_page,text="",fg="red")

        login_username_label = tk.Label(self.account_login_page,text="Username:")
        login_username_label.grid(row=2,column=0,padx=(50,0),pady=(10,0))
        self.login_username_entry = tk.Entry(self.account_login_page,textvariable=self.username_String_Var)
        self.login_username_entry.grid(row=2,column=1,padx=10,pady=(10,0))
        # endregion

        # region Password
        login_password_label = tk.Label(self.account_login_page,text="Password:")
        login_password_label.grid(row=4,column=0,padx=(50,0),pady=(0,10)) # row = 4 olmasının sebebi alert_for_username içerisindeki username_warning_label -> row=3 
        self.login_password_entry = tk.Entry(self.account_login_page,show="*") 
        self.login_password_entry.grid(row=4,column=1,padx=10,pady=(0,10)) # row = 4 olmasının sebebi alert_for_username içerisindeki username_warning_label -> row=3 
        # endregion

        # region Login Button
        login_button = tk.Button(self.account_login_page,text="Login",command=self.startLoginButton)
        login_button.grid(row=5,column=0,padx=10,pady=10,columnspan=2,sticky="nsew")
        # endregion 

        # region Music Button
        mixer.init()
        mixer.music.load(paths.background_music_mp3_path)
        self.create_music_button("play",6,0,10,10,paths.play_png_path) 
        self.create_music_button("pause",6,1,10,10,paths.pause_png_path)
        # endregion

        for widget in self.account_login_page.winfo_children():
            widget.configure(bg="white")
  
    # region Username Check
    def alert_for_username(self,*args):
        self.username_warning_label.grid(row=3,column=0,columnspan=2)
        username = self.login_username_entry.get()
        is_valid = self.check_username_entry_rules(username)
        if is_valid or len(username) == 0:
            self.username_warning_label.config(text="")
        else:
            self.username_warning_label.config(text="The user name cannot be less than 4 characters and \n cannot contain prohibited letters.")
          
    def check_username_entry_rules(self,username):
        turkish_characters = 'çÇğĞıİöÖşŞüÜ'

        has_turkish_character = any(char in username for char in turkish_characters) # turkish_characters içerisindeki harflerden herhangi biri içi True değer döndürür.
        return len(username) >= 4 and not has_turkish_character 
    # endregion

    # region Login Button Works
    def saveToDatabase(self):   
        username = self.login_username_entry.get() 
        password = self.login_password_entry.get() 
        conn = sqlite3.connect(paths.login_db_path)
        cursor = conn.cursor() 
        try:
            conn.execute("CREATE TABLE IF NOT EXISTS Accounts_Data (username TEXT, password TEXT)")
            conn.execute("DELETE FROM Accounts_Data")
            cursor.execute("INSERT INTO Accounts_Data (username,password) VALUES (?,?)",(username,password))
            conn.commit()
        except:
            print("Bir hata oldu!!")
        finally:
            cursor.close() # cursor conn'dan önce kapatılmalıdır.
            conn.close()

    def readToDatabase(self):
        conn = sqlite3.connect(paths.login_db_path)
        cursor = conn.cursor() 
        try:
            cursor.execute("SELECT * FROM Accounts_Data")
            data = cursor.fetchone()
            account_database_username = data[0]
            account_database_password = data[1]
            self.account_database_username = account_database_username
            self.account_database_password = account_database_password
        except Exception as e:
            print(e,"Login hesabının bilgileri Accounts_Data'dan alınırken sorun oluştu!")
        finally:
            cursor.close()
            conn.close()

    def clickLogin(self):
        try:
            self.browser = webdriver.Firefox()
            self.browser.get("https://www.instagram.com/")
            self.browser.implicitly_wait(10)
            username = self.browser.find_element("name","username")
            password = self.browser.find_element("name","password")

            username.send_keys(f"{self.account_database_username}")
            password.send_keys(f"{self.account_database_password}")
            time.sleep(random.uniform(1,2))

            login = self.browser.find_element(By.XPATH,"//button[@type='submit']")
            login.click()
            print("Login tuşuna basıldı, 5 saniye bekleniyor.")
            time.sleep(5)

        except Exception as e:
            print(e,"Accounts_Data'dan verileri alıp işlerken bir sorun oluştu!")

    def determineCookieStatu(self):
        try:
            self.browser.find_element(By.XPATH, "//*[@id='slfErrorAlert']")
            print("Can not be logged in.")
            self.login_success_statu = False
        except:
            print("Logged in!")
            cookies = self.browser.get_cookies()
            pickle.dump(cookies,open(paths.cookies_pkl_path,"wb"))
            print("Cookies have been installed.")
            self.login_success_statu = True
        finally:
            self.browser.quit()
            print("Browser has been closed.")
            
    def startLoginButton(self):
        self.t1 = threading.Thread(target=self.runLoginButton)
        self.t1.start()
    
    def runLoginButton(self):
        t1 = threading.Thread(target=self.saveToDatabase)
        t2 = threading.Thread(target=self.readToDatabase)
        t3 = threading.Thread(target=self.clickLogin)

        t1.start()
        t1.join()
        t2.start()
        t2.join()
        t3.start()
        t3.join()

        def check_threads():
            if t1.is_alive() or t2.is_alive() or t3.is_alive():
                self.login_window.after(100, check_threads)
            else:
                self.determineCookieStatu()
                if self.login_success_statu == True:
                    self.login_window.destroy()
                    subprocess.run(["python",paths.main_py_path])

        self.login_window.after(100, check_threads)
    # endregion

    def create_music_button(self,play_or_pause,row,column,padx,pady,img):
        if play_or_pause == "play":
            def play_or_pause_music():
                if not self.playing:
                    mixer.music.play()
                    self.playing = True
        else:
            def play_or_pause_music():
                if self.playing:
                    mixer.music.stop()
                    self.playing = False
                
        button_canvas = tk.Canvas(self.account_login_page,width=50,height=50,bg="white",highlightthickness=0)
        button_canvas.grid(row=row,column=column,padx=padx,pady=pady)

        button_img = Image.open(img).resize((40,40))
        button_img = ImageTk.PhotoImage(button_img)

        button = tk.Button(button_canvas,image=button_img,command=play_or_pause_music,bd=0,highlightthickness=0,relief="flat",bg="white",highlightbackground="white")
        button.image = button_img
        button.grid(row=row,column=column,padx=padx,pady=pady)
          
    def update_from_beginning(self):
        def fill_username_and_password():
            conn = sqlite3.connect(paths.login_db_path)
            cursor = conn.cursor() 

            result = cursor.fetchone()
            if result is not None:
                cursor.execute("SELECT username, password FROM Accounts_Data")
                row = cursor.fetchone()
                username = row[0]
                password = row[1]
                self.login_username_entry.insert(0,username)
                self.login_password_entry.insert(0,password)
        self.account_login_page.after(100,fill_username_and_password)

    def run_login_window(self):
        self.configure_properties()
        self.create_components()
        self.update_from_beginning()
        self.login_window.mainloop()

if __name__ == "__main__":
    LoginWindow().run_login_window()