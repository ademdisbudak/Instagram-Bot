import tkinter as tk
from selenium import webdriver
from selenium.webdriver.common.by import By
from PIL import Image,ImageTk
from pygame import mixer
import subprocess,sqlite3,paths,threading,time,random,pickle,fonts



class LoginWindow:

    def __init__(self):
        self.login_window = tk.Tk()

    def configure_properties(self):
        
        self.login_window.update_idletasks() 
        self.login_window.title("İnstagram Bot Application")

        screen_width = self.login_window.winfo_screenwidth()
        screen_height = self.login_window.winfo_screenheight()

        window_width = self.login_window.winfo_width()
        window_height = self.login_window.winfo_height()

        x = (screen_width - window_width) // 2
        y = (screen_height - window_height*3) // 2
        self.login_window.geometry(f"+{x}+{y}") 

    def create_components(self):

        # region Main Frame
        frame = tk.Frame(self.login_window)
        frame.pack()
        # endregion

        # region Label Frame
        # label_widget = tk.Label(frame, text="Login Page",font=fonts.get_big_font(frame),fg="darkorange4") 
        self.account_login_page = tk.LabelFrame(frame,labelanchor="n",border=False)
        self.account_login_page.pack(fill="both",expand=True)
        # endregion

        # region Logo
        self.logo_img = Image.open(paths.auto_unfollow_png_path).resize((250,250))
        self.logo_img = ImageTk.PhotoImage(self.logo_img)

        logo_label = tk.Label(self.account_login_page,image=self.logo_img)
        logo_label.grid(row=0,column=0,columnspan=2,padx=20,pady=10)

        welcome_label = tk.Label(self.account_login_page,text="Welcome to my instagram automation!\n@4demph - Adem Dişbudak",font=fonts.get_middle_font(frame),fg="darkorange4") 
        welcome_label.grid(row=1,column=0,columnspan=2,padx=25,pady=10)
        # endregion

        # region Username
        self.username_String_Var = tk.StringVar()
        self.username_String_Var.trace_add("write",self.alert_for_username)
        self.username_warning_label = tk.Label(self.account_login_page,text="",fg="red")

        login_username_label = tk.Label(self.account_login_page,text="Username:",font=fonts.get_middle_font(frame),fg="darkorange3")
        login_username_label.grid(row=2,column=0,sticky="e",pady=(0,10))
        self.login_username_entry = tk.Entry(self.account_login_page,textvariable=self.username_String_Var,font=fonts.get_small_font(frame),fg="darkorange2")
        self.login_username_entry.grid(row=2,column=1,sticky="w",padx=5,pady=(0,10))
        # endregion

        # region Password
        login_password_label = tk.Label(self.account_login_page,text="Password:",font=fonts.get_middle_font(frame),fg="darkorange3")
        login_password_label.grid(row=4,column=0,sticky="e",pady=(0,10)) # row = 4 olmasının sebebi alert_for_username içerisindeki username_warning_label -> row=3 
        self.login_password_entry = tk.Entry(self.account_login_page,show="*",font=fonts.get_small_font(frame),fg="darkorange2") 
        self.login_password_entry.grid(row=4,column=1,sticky="w",padx=5,pady=(0,10)) # row = 4 olmasının sebebi alert_for_username içerisindeki username_warning_label -> row=3 
        # endregion

        # region Login Button
        login_button = tk.Button(self.account_login_page,text="Login",command=self.start_login_button,background="darkorange2",foreground="white",width=30)
        login_button.grid(row=5,column=0,padx=10,pady=(10,25),columnspan=2)
        # endregion 

    # region Username Check
    def alert_for_username(self,*args):
        username = self.login_username_entry.get()
        is_valid = self.check_username_entry_rules(username)
        if is_valid or len(username) == 0:
            self.username_warning_label.grid_forget()
        else:
            self.username_warning_label.grid(row=3,column=0,columnspan=2)
            self.username_warning_label.config(text="The user name cannot be less than 4 characters and \n cannot contain prohibited letters.")
          
    def check_username_entry_rules(self,username):
        turkish_characters = 'çÇğĞıİöÖşŞüÜ'

        has_turkish_character = any(char in username for char in turkish_characters) 
        return len(username) >= 4 and not has_turkish_character 
    # endregion

    # region Login Button Works
    def save_to_database(self):   
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
            cursor.close()
            conn.close()

    def read_to_database(self):
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

    def click_login(self):
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
            print("Loginning..")
            time.sleep(5)

        except Exception as e:
            print(e,"click_login")

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
            
    def start_login_button(self):
        self.t1 = threading.Thread(target=self.run_login_button)
        self.t1.start()
    
    def run_login_button(self):
        t1 = threading.Thread(target=self.save_to_database)
        t2 = threading.Thread(target=self.read_to_database)
        t3 = threading.Thread(target=self.click_login)

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
