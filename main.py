import tkinter as tk
import auto_follow,accounts_informations,threading,sqlite3,paths,auto_unfollow

class MainWindow:
    
    def __init__(self):
        self.main_window = tk.Tk()

    def configure_main_window_widget(self):
        self.main_window.title("Menü ve Pencereler")
        screen_width = self.main_window.winfo_screenwidth()
        screen_height = self.main_window.winfo_screenheight()
        self.width = 700
        self.height = 400
        self.x = (screen_width - self.width) // 2
        self.y = (screen_height - self.height) // 2
        self.main_window.geometry(f"{self.width}x{self.height}+{self.x}+{self.y}")

    def create_menu(self):
        self.menu_frame = tk.Frame(self.main_window, bg="lightgray")
        self.menu_frame.pack(side="left", fill="y")

        self.menu_label = tk.Label(self.menu_frame, text="Menü", font=("Arial", 16), bg="lightgray")
        self.menu_label.grid(row=0, column=0, pady=10)

        self.menu_items = {
            "Accounts Informations": self.open_accounts_informations_window,
            "Auto Follow": self.open_auto_follow_window,
            "Auto Unfollow": self.open_auto_unfollow_window,
            "Auto Like": self.open_auto_like_window,
        }

        row_num = 1
        for item in self.menu_items:
            button = tk.Button(self.menu_frame, text=item, command=self.menu_items[item], width=20)
            button.grid(row=row_num, column=0, padx=10, pady=5)
            row_num += 1
    
    def create_frames(self):
        self.content_frame = tk.Frame(self.main_window)
        self.content_frame.pack(side="right", fill="both", expand=True)

        self.frames = {
            "accounts_informations": tk.Frame(self.content_frame, bg="white"),
            "auto_follow": tk.Frame(self.content_frame, bg="white"),
            "auto_unfollow": tk.Frame(self.content_frame, bg="white"),
            "auto_like": tk.Frame(self.content_frame, bg="white"),
        }

        for frame in self.frames.values():
            frame.pack(fill="both", expand=True)

        self.hide_all_frames()
    
    def open_accounts_informations_window(self):
        def run():
            self.hide_all_frames()
            self.frames["accounts_informations"].pack(fill="both",expand=True)
            for widget in self.frames["accounts_informations"].winfo_children():
                widget.destroy()
            
            width_change = 300
            height_change = 370

            self.main_window.geometry(f"{self.width+width_change}x{self.height+height_change}+{self.x-width_change//2}+{self.y-height_change//2}")
            accounts_informations.AccountsInformationsWindow(self.frames["accounts_informations"]).run_accounts_informations_window()
        
        threading.Thread(target=run).start()

    def open_auto_follow_window(self):
        def run():
            self.hide_all_frames()
            self.frames["auto_follow"].pack(fill="both",expand=True)
            for widget in self.frames["auto_follow"].winfo_children():
                widget.destroy()

            width_change = -10
            height_change = 60

            self.main_window.geometry(f"{self.width+width_change}x{self.height+height_change}+{self.x-width_change//2}+{self.y-height_change//2}")
            auto_follow.AutoFollowWindow(self.frames["auto_follow"]).run_auto_follow_window()
        
        threading.Thread(target=run).start()

    def open_auto_unfollow_window(self):
        def run():
            self.hide_all_frames()
            self.frames["auto_unfollow"].pack(fill="both",expand=True)
            for widget in self.frames["auto_unfollow"].winfo_children():
                widget.destroy()
            
            width_change = 220
            height_change = 250

            self.main_window.geometry(f"{self.width+width_change}x{self.height+height_change}+{self.x-width_change//2}+{self.y-height_change//2}")
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
    
    def create_account_informations_db(self):
        conn = sqlite3.connect(paths.account_informations_db_path)
        cursor = conn.cursor()
        return conn,cursor
    
    def create_auto_follow_db(self): # Her thread ayrı bağlantı istediği için her defasında yeniden bağlantı oluşturmalıyız.
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


    def runMainWindow(self):
        self.configure_main_window_widget()
        self.create_menu()
        self.create_frames()
        self.create_database_from_beginning()
        self.main_window.mainloop()

if __name__ == "__main__":
    MainWindow().runMainWindow()