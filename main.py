import tkinter as tk
from PIL import Image,ImageTk
import auto_follow,accounts_informations,threading,sqlite3,paths,auto_unfollow,fonts,webbrowser

class MainWindow:
    
    def __init__(self):
        self.main_window = tk.Tk()

        self.linkedin_profile_link = "https://www.linkedin.com/in/ademdisbudak/"
        self.instagram_profile_link = "https://www.instagram.com/4demph"
        self.github_profile_link = "https://github.com/ademdisbudak"
        self.web_address = "https://www.ademdisbudak.com"

    def configure_main_window_widget(self):
        self.main_window.update_idletasks()
        self.main_window.title("4demph - Instagram Automation")
        screen_width = self.main_window.winfo_screenwidth()
        screen_height = self.main_window.winfo_screenheight()
        
        window_width = self.main_window.winfo_width()
        window_height = self.main_window.winfo_height()

        x = (screen_width - window_width*3) // 2
        y = (screen_height - window_height*3) // 2
        self.main_window.geometry(f"+{x}+{y}") 

    def create_menu(self):
        self.menu_frame = tk.Frame(self.main_window)
        self.menu_frame.pack(side="left",fill="y")

        self.menu_label = tk.Label(self.menu_frame, text="Menu",font=fonts.get_big_bahnschrift_font(self.main_window))
        self.menu_label.grid(row=0, column=0, pady=10)

        self.menu_items = {
            "Main": self.open_welcome_window,
            "Counts & Lists": self.open_accounts_informations_window,
            "Auto Follow": self.open_auto_follow_window,
            "Auto Unfollow": self.open_auto_unfollow_window,
            "Auto Like": self.open_auto_like_window,
        }

        row_num = 1
        for item in self.menu_items:
            button = tk.Button(self.menu_frame, text=item, command=self.menu_items[item], width=20,font=fonts.get_medium_bahnschrift_font(self.main_window))
            button.grid(row=row_num, column=0, padx=10, pady=5)
            row_num += 1
    
    def create_frames(self):
        self.content_frame = tk.Frame(self.main_window)
        self.content_frame.pack(side="right",expand=True)

        self.frames = {
            "welcome": tk.Frame(self.content_frame),
            "accounts_informations": tk.Frame(self.content_frame),
            "auto_follow": tk.Frame(self.content_frame),
            "auto_unfollow": tk.Frame(self.content_frame),
            "auto_like": tk.Frame(self.content_frame),
        }

        for frame in self.frames.values():
            frame.pack()
        
        self.hide_all_frames()      

    def open_welcome_window(self):
        def run():
            self.hide_all_frames()
            self.welcome_frame = self.frames["welcome"]
            self.welcome_frame.pack()
            for widget in self.welcome_frame.winfo_children():
                widget.destroy()

            # region 1 - Title and Logo Label Frame
            title_and_logo_label_frame = tk.LabelFrame(self.welcome_frame,highlightthickness=10,highlightbackground="chocolate4",border=False)
            title_and_logo_label_frame.grid(row=0,column=0,padx=7,pady=7)

            # region Title
            title = tk.Label(title_and_logo_label_frame,text="Welcome!",font=fonts.get_stencil_font(title_and_logo_label_frame,40),fg="chocolate4")
            title.grid(row=0,column=0)
            # endregion

            # region Image
            self.logo_img = Image.open(paths.auto_unfollow_png_path).resize((400,400))
            self.logo_img = ImageTk.PhotoImage(self.logo_img)

            logo_location_label = tk.Label(title_and_logo_label_frame,image=self.logo_img)
            logo_location_label.grid(row=1,column=0)
            # endregion

            # endregion

            # region 2 - Concact Label Frame
            contact_label_frame = tk.LabelFrame(self.welcome_frame,border=False)
            contact_label_frame.grid(row=1,column=0)
            
            # region Linkedin Button
            def open_linkedin_profile():
                webbrowser.open(self.linkedin_profile_link)
            self.linkedin_img = Image.open(paths.linkedin_png_path).resize((50,50))
            self.linkedin_img = ImageTk.PhotoImage(self.linkedin_img)

            linkedin_button = tk.Button(contact_label_frame,image=self.linkedin_img,border=False,command=open_linkedin_profile)
            linkedin_button.grid(row=2,column=0)
            # endregion

            # region İnstagram Button
            def open_instagram_profile():
                webbrowser.open(self.instagram_profile_link)
            self.instagram_img = Image.open(paths.instagram_png_path).resize((50,50))
            self.instagram_img = ImageTk.PhotoImage(self.instagram_img)

            instagram_button = tk.Button(contact_label_frame,image=self.instagram_img,border=False,command=open_instagram_profile)
            instagram_button.grid(row=2,column=1)
            # endregion

            # region GitHub Button
            def open_github_profile():
                webbrowser.open(self.github_profile_link)
            self.github_img = Image.open(paths.github_png_path).resize((50,50))
            self.github_img = ImageTk.PhotoImage(self.github_img)

            github_button = tk.Button(contact_label_frame,image=self.github_img,border=False,command=open_github_profile)
            github_button.grid(row=2,column=2)
            # endregion

            # region Web Adress
            def open_web_address():
                webbrowser.open(self.web_address)
            self.web_address_img = Image.open(paths.logo_png_path).resize((50,50))
            self.web_address_img = ImageTk.PhotoImage(self.web_address_img)

            web_address_button = tk.Button(contact_label_frame,image=self.web_address_img,border=False,command=open_web_address)
            web_address_button.grid(row=2,column=3)

            # endregion

            for widget in contact_label_frame.winfo_children():
                widget.grid_configure(padx=5,pady=5)

            # endregion

        threading.Thread(target=run).start()
    
    def open_accounts_informations_window(self):
        def run():
            self.hide_all_frames()
            self.frames["accounts_informations"].pack(fill="both",expand=True)
            for widget in self.frames["accounts_informations"].winfo_children():
                widget.destroy()

            accounts_informations.AccountsInformationsWindow(self.frames["accounts_informations"]).run_accounts_informations_window()
        
        threading.Thread(target=run).start()

    def open_auto_follow_window(self):
        def run():
            self.hide_all_frames()
            self.frames["auto_follow"].pack(fill="both",expand=True)
            for widget in self.frames["auto_follow"].winfo_children():
                widget.destroy()

            auto_follow.AutoFollowWindow(self.frames["auto_follow"]).run_auto_follow_window()
        
        threading.Thread(target=run).start()

    def open_auto_unfollow_window(self):
        def run():
            self.hide_all_frames()
            self.frames["auto_unfollow"].pack(fill="both",expand=True)
            for widget in self.frames["auto_unfollow"].winfo_children():
                widget.destroy()

            auto_unfollow.AutoUnfollowWindow(self.frames["auto_unfollow"]).run_auto_unfollow_window()
            
        threading.Thread(target=run).start()
        
    def open_auto_like_window(self):
        self.hide_all_frames()
        self.frames["auto_like"].pack()
        for widget in self.frames["auto_like"].winfo_children():
            widget.destroy()

    def hide_all_frames(self):
        for frame in self.frames.values():
            frame.pack_forget()

    def run_main_window(self):
        self.configure_main_window_widget()
        self.create_menu()
        self.create_frames()
        self.open_welcome_window()
        self.create_database_from_beginning()
        self.main_window.mainloop()
    
    # region Creating Database
    def create_account_informations_db(self):
        conn = sqlite3.connect(paths.account_informations_db_path)
        cursor = conn.cursor()
        return conn,cursor
    
    def create_auto_follow_db(self):
        conn = sqlite3.connect(paths.auto_follow_db_path)
        cursor = conn.cursor()
        return conn,cursor
    
    def create_database_from_beginning(self):

        def create_account_information_tables():
            (conn,cursor) = self.create_account_informations_db()
            cursor.execute("CREATE TABLE IF NOT EXISTS Profile_Counts (follower TEXT , followup TEXT)")
            cursor.execute("CREATE TABLE IF NOT EXISTS Followers (username TEXT)")
            cursor.execute("CREATE TABLE IF NOT EXISTS Follows (username TEXT)")
            cursor.execute("CREATE TABLE IF NOT EXISTS Mutual_Followers (username TEXT)")
            cursor.execute("CREATE TABLE IF NOT EXISTS Non_Mutual_Followers (username TEXT)")
            cursor.execute("CREATE TABLE IF NOT EXISTS Fan_Followers (username TEXT)")
            conn.commit()

        self.main_window.after(0,create_account_information_tables)

        def create_auto_follow_db():
            (conn,cursor) = self.create_auto_follow_db()
            cursor.execute("CREATE TABLE IF NOT EXISTS Permanent_Follow_Count (count TEXT)")
            
            cursor.execute("CREATE TABLE IF NOT EXISTS Temporary_Follow_Count (count TEXT)")
            cursor.execute("DELETE FROM Temporary_Follow_Count")

            cursor.execute("CREATE TABLE IF NOT EXISTS Username_To_Follow (username TEXT)")
            cursor.execute("DELETE FROM Username_To_Follow")
            conn.commit()

        self.main_window.after(0,create_auto_follow_db)
    # endregion

if __name__ == "__main__":
    MainWindow().run_main_window()