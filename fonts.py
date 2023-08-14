from tkinter import font

def get_big_font(root):
    return font.Font(root, family="Calibri",size=30, weight="bold")

def get_middle_font(root):
    return font.Font(root, family="Calibri", size=12, weight="bold")

def get_small_font(root):
    return font.Font(root, family="Calibri", size=9, weight="normal")






import tkinter as tk
def show_all_font():
    root = tk.Tk()
    font_names = tk.font.families()

    for font_name in font_names:
        print(font_name)

    root.destroy()

# show_all_font() # If you want see all font names, do it.