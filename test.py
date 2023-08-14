import tkinter as tk
import webbrowser

def open_linkedin_profile():
    url = "https://www.linkedin.com/in/ademdisbudak/"
    webbrowser.open(url)

root = tk.Tk()
root.title("LinkedIn Profil")

button = tk.Button(root, text="LinkedIn Profilimi Aç", command=open_linkedin_profile)
button.pack(pady=20)

root.mainloop()
