import tkinter as tk
from tkinter import font

root = tk.Tk()
root.title("Özel Font Kullanımı")

# Font dosyasının yolunu belirtin
font_path = "fonts/Caprasimo-Regular.ttf"

# Fontu adlandırın
custom_font = tk.font.nametofont("Caprasimo")
custom_font.configure(family="Caprasimo", file=font_path, size=30)

# Yeni bir etiket (label) oluşturun ve fontu ayarlayın
label = tk.Label(root, text="Merhaba Özel Font!", font=custom_font)
label.pack(pady=20)

root.mainloop()
