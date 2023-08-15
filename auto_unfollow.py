import tkinter as tk
from tkinter import scrolledtext
from PIL import Image,ImageTk
from auto_unfollow_selenium import lists_and_counts,unfollow_bot
import paths,threading,fonts

class AutoUnfollowWindow:

    def __init__(self,parent_frame):
        self.parent_frame = parent_frame

    def create_components(self):

        # region First Label Frame 
        self.first_label_frame = tk.LabelFrame(self.parent_frame)
        self.first_label_frame.grid(row=0,column=0,rowspan=2)
        
        # region Non Mutual List
        first_label_title = tk.Label(self.first_label_frame,text="Non Mutual List",font=fonts.get_stencil_font(self.first_label_frame,20),fg="grey")
        first_label_title.grid(row=0,column=0,padx=10,pady=(5,0))

        self.non_mutual_scrolledText = scrolledtext.ScrolledText(self.first_label_frame,width = 25, height = 31)
        self.non_mutual_scrolledText.vbar.configure(width=25)

        self.non_mutual_scrolledText.grid(row=1,column=0,padx=10,pady=(0,15))
        # endregion

        # endregion 

        # region Second Label Frame
        self.second_label_frame = tk.LabelFrame(self.parent_frame)
        self.second_label_frame.grid(row=0,column=1)

        # region Blacklist Adding
        blacklist_add_label = tk.Label(self.second_label_frame,text="Add to BlackList:")
        blacklist_add_label.grid(row=0,column=0,sticky="e",pady=5)
        self.blacklist_add_entry = tk.Entry(self.second_label_frame)
        self.blacklist_add_entry.grid(row=0,column=1,pady=5)
        blacklist_add_button = tk.Button(self.second_label_frame,text="Add!",width=10,command=self.add_to_blacklist)
        blacklist_add_button.grid(row=0,column=2,pady=5)
        # endregion

        # region Blacklist Removing
        blacklist_remove_label = tk.Label(self.second_label_frame,text="Remove to BlackList:")
        blacklist_remove_label.grid(row=1,column=0,sticky="e",pady=(5,15))
        self.blacklist_remove_entry = tk.Entry(self.second_label_frame)
        self.blacklist_remove_entry.grid(row=1,column=1,pady=(5,15))
        blacklist_remove_button = tk.Button(self.second_label_frame,text="Remove!",width=10,command=self.remove_to_blacklist)
        blacklist_remove_button.grid(row=1,column=2,pady=(5,15))
        # endregion 

        # region Blacklist ScrolledText & Remove All Button
        self.blacklist_scrolledText = scrolledtext.ScrolledText(self.second_label_frame,width = 45, height = 8)
        self.blacklist_scrolledText.grid(row=2,column=0,columnspan=3,padx=10,pady=10)

        blacklist_remove_all_button = tk.Button(self.second_label_frame,text="Remove all BlackList!",command=self.remove_all_blacklist)
        blacklist_remove_all_button.grid(row=3,column=0,columnspan=3,padx=10,pady=10,sticky="nsew")
        # endregion

        # endregion

        # region Third Label Frame
        self.third_label_frame = tk.LabelFrame(self.parent_frame)
        self.third_label_frame.grid(row=1,column=1)

        # region Speed & Start Unfollow Process
        self.speed_to_unfollow_scale = tk.Scale(self.third_label_frame,orient="horizontal",from_=1,to=10,length=395,width=30)
        self.speed_to_unfollow_scale.set(value=5)
        self.speed_to_unfollow_scale.grid(row=0,column=0,padx=5,pady=5)

        start_unfollow_process_button = tk.Button(self.third_label_frame,text="Start Unfollow!",command=self.start_unfollow_process,width=55,height=10,bg="lightgrey")
        start_unfollow_process_button.grid(row=1,column=0,padx=5,pady=10)
        # endregion

        # endregion

        for widget in self.parent_frame.winfo_children():
            widget.grid_configure(padx=10,pady=10)
            widget.configure(border=False,highlightthickness=5,highlightbackground="white")

    def run_unfollow_process(self):
        unfollow_bot.UnfollowBot(self.speed_to_unfollow_scale.get()).start_unfollow_bot()
    
    def start_unfollow_process(self):
        threading.Thread(target=self.run_unfollow_process).start()
        
    def refresh_to_blacklist(self):
        self.blacklist_scrolledText.delete("1.0",tk.END)
        blacklist_from_database = lists_and_counts.ListMembers().getBlackListMembers()
        for number,username in enumerate(blacklist_from_database,start=1):
            self.blacklist_scrolledText.insert(tk.END,f"{number}. {username}\n")

    def add_to_blacklist(self):
        # Entry'den bilgiyi alıyoruz ve virgüllere göre ayırıyoruz.
        add_to_blacklist_from_entry = self.blacklist_add_entry.get().strip()
        blacklist = [username.strip() for username in add_to_blacklist_from_entry.split(",") if username.strip()]
        # Blacklist database'ye ekliyoruz.
        lists_and_counts.BlackList().addToBlackList(blacklist)
        # Blacklist scrolledText'i güncelliyoruz.
        self.refresh_to_blacklist()

    def remove_to_blacklist(self):
        # Entry'den bilgiyi alıyoruz ve virgüllere göre ayırıyoruz.
        remove_to_blacklist_from_entry = self.blacklist_remove_entry.get().strip()
        blacklist = [username.strip() for username in remove_to_blacklist_from_entry.split(",") if username.strip()]
        # Blacklist database'ye ekliyoruz.
        lists_and_counts.BlackList().removeFromBlackList(blacklist)
        # Blacklist scrolledText'i güncelliyoruz.
        self.refresh_to_blacklist()

    def remove_all_blacklist(self):
        lists_and_counts.BlackList().removeAll()
        self.refresh_to_blacklist()

    def update_from_beginning(self):

        def update_non_mutual_scrolledText():
            try:
                non_mutual_usernames = lists_and_counts.ListMembers().getNonMutualFollowerListMembers()
                if non_mutual_usernames is not None:
                    for number,username in enumerate(non_mutual_usernames,start=1):
                        self.non_mutual_scrolledText.insert(tk.END,f"{number}. {username}\n")
                self.first_label_frame.after(20000,update_non_mutual_scrolledText)
            except Exception as e:
                print("There was a problem loading the non-mutuals:",e)
        
        self.first_label_frame.after(0,update_non_mutual_scrolledText)

        def update_blacklist_scrolledText():
            # BlackList başlangıçta auto_unfollow.db içerisinde oluşturuluyor.
            lists_and_counts.BlackList().createBlackList()

            # BlackList'i başlangıçta auto_unfollow.db'den alıp scrolledText içerisine yazdırıyoruz.
            blacklist_from_database = lists_and_counts.ListMembers().getBlackListMembers()
            self.blacklist_scrolledText.delete("1.0",tk.END) # blacklist'i temizliyoruz.
            for number,username in enumerate(blacklist_from_database,start=1):
                self.blacklist_scrolledText.insert(tk.END,F"{number}. {username}\n")
            
        self.second_label_frame.after(0,update_blacklist_scrolledText)
        
    def run_auto_unfollow_window(self):
        self.create_components()
        self.update_from_beginning()
#         self.parent_frame.mainloop() # temporary - Programın bu pencereden açılmasını istiyorsan -> CTRL + K + U
# if __name__ == "__main__": # temporary - Programın bu pencereden açılmasını istiyorsan -> CTRL + K + U
#     parent_frame = tk.Tk() # temporary - Programın bu pencereden açılmasını istiyorsan -> CTRL + K + U
#     AutoUnfollowWindow(parent_frame).run_auto_unfollow_window() # temporary - Programın bu pencereden açılmasını istiyorsan -> CTRL + K + U