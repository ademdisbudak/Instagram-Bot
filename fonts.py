from tkinter import font
import random
import tkinter as tk


# ---------------------------------------------------------------------
def get_very_big_stencil_font(root):
    return font.Font(root,family="Stencil",size=40,weight="bold")
# ---------------------------------------------------------------------


# ---------------------------------------------------------------------
def get_big_calibri_font(root):
    return font.Font(root, family="Calibri",size=24, weight="bold")
def get_medium_calibri_font(root):
    return font.Font(root, family="Calibri",size=12, weight="bold")
def get_small_calibri_font(root):
    return font.Font(root, family="Calibri",size=10, weight="normal")
# ---------------------------------------------------------------------

def get_big_bahnschrift_font(root):
    return font.Font(root,family="Bahnschrift SemiBold",size=24,weight="bold")

def get_medium_bahnschrift_font(root):
    return font.Font(root,family="Bahnschrift SemiBold",size=12,weight="normal")



def get_big_random_font(root):

    # creating a list with all font families
    font_list = []
    font_names = tk.font.families()
    for font_name in font_names:
        font_list.append(font_name)
    
    # making a random choice
    random_choice = random.choice(font_list)
    print(random_choice)

    return font.Font(root,family=random_choice,size=24,weight="bold")