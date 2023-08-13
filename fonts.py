from tkinter import font
from ttkthemes import ThemedTk

def get_big_font(root):
    return font.Font(root, family="Oswald", size=30, weight="bold")

def get_middle_font(root):
    return font.Font(root, family="Oswald", size=12, weight="bold")

def get_small_font(root):
    return font.Font(root, family="Oswald", size=9, weight="normal")