# xPath - CSS Selector Creating Functions
def create_follower_username_css(i):                                                                                                                                                    # list_and_counts.py - pilot_account_test.py
    result = f"._aano > div:nth-child(1) > div:nth-child(1) > div:nth-child({i})"
    return result

def create_follow_username_css(i):                                                                                                                                                      # list_and_counts.py - pilot_account_test.py
    result = f"div.x1dm5mii:nth-child({i})"
    return result

def create_unfollow_button_first_stage_css(i):
    result = f"div.x1dm5mii:nth-child({i}) > div:nth-child(1) > div:nth-child(1) > div:nth-child(1) > div:nth-child(3) > div:nth-child(1) > button:nth-child(1)"
    return result



# xPath's
profile_photo_css_selector = "span.xnz67gz:nth-child(2) > img:nth-child(1)"                                                                                                             # accounts_informations.py

secret_or_open_account_xPath = "/html/body/div[2]/div/div/div[2]/div/div/div/div[1]/div[2]/section/main/div/div/article/div/div/h2"                                                     # auto_unfollow.py
follow_count_from_html_xPath = "//div[contains(@class, '_aano')]//div[@class='x1dm5mii x16mil14 xiojian x1yutycm x1lliihq x193iq5w xh8yej3']"                                           # auto_unfollow.py

like_button_xPath = "/html/body/div[2]/div/div/div[3]/div/div/div[1]/div/div[3]/div/div/div/div/div[2]/div/article/div/div[2]/div/div/div[2]/section[2]/div/div/span/a"                 # auto_follow.py
close_dialog_window_xPath = "/html/body/div[2]/div/div/div[3]/div/div/div[2]/div/div/div[1]/div/div[2]/div/div/div/div/div[2]/div/div[1]/div/div[3]/div/button"                         # auto_follow.py
close_post_window_xPath = "/html/body/div[2]/div/div/div[3]/div/div/div[1]/div/div[2]/div"                                                                                              # auto_follow.py

follow_and_follower_dialog_window_css_selector = "._aano"                                                                                                                               # list_and_counts.py
follow_and_follower_count_from_html_xpath = '//div[contains(@class, "_aano")]//div[1]//div[1]//div[@class="x1dm5mii x16mil14 xiojian x1yutycm x1lliihq x193iq5w xh8yej3"]'              # list_and_counts.py
accounts_informations_css_selector = "section.x1qjc9v5"                                                                                                                                 # list_and_counts.py

unfollow_button_second_stage_css_selector = "button._a9--:nth-child(2)"                                                                                                                 # unfollow_bot.py

# Txt's
proxy_list_txt_path = "E:/Python/instagram_automation/proxy/proxy_list.txt"

# File's
main_py_path = "E:/Python/instagram_automation/main.py" 

# Database
login_db_path = "E:/Python/instagram_automation/database/login.db" 
account_informations_db_path = "E:/Python/instagram_automation/database/account_informations.db"
auto_follow_db_path = "E:/Python/instagram_automation/database/auto_follow.db" 
auto_unfollow_db_path = "E:/Python/instagram_automation/database/auto_unfollow.db"

# Photo
logo_png_path = "E:/Python/instagram_automation/assets/photo/logo.png" 
profile_photo_png_path = "E:/Python/instagram_automation/assets/photo/profile_photo.png"
play_png_path = "E:/Python/instagram_automation/assets/photo/play.png"
pause_png_path = "E:/Python/instagram_automation/assets/photo/pause.png"
auto_unfollow_png_path = "E:/Python/instagram_automation/assets/photo/auto_unfollow.png"

# Music's
background_music_mp3_path = "E:/Python/instagram_automation/assets/music/background_music.mp3" 

# Firefox Profile
firefox_proile_path = r"C:/Users/adems/AppData/Roaming/Mozilla/Firefox/Profiles/aom2axov.default-release"

# Cookies
cookies_pkl_path = "E:/Python/instagram_automation/cookies/cookies.pkl" 
cookies_pilot_account_path =  "E:/Python/instagram_automation/cookies/cookies_pilot_account.pkl"



# İçerdikleri:
# region login.py:
# 1 - background_music_mp3_path
# 2 - logo_png_path
# 3 - accounts_db_path
# 4 - cookies_pkl_path
# 5 - main_py_path
# endregion

# region main.py:
# nothing #
# endregion

# region accounts_informations.py:
# 1 - account_informations_db_path
# 2 - accounts_db_path
# 3 - auto_unfollow_db_path
# 4 - auto_follow_db_path
# 5 - proxy_list_txt_path
# 6 - profile_photo_png_path
# endregion

# region auto_follow.py
# 1 - auto_follow_db_path 
# 2 - proxy_list_txt_path
# 3 - firefox_proxy_path
# 4 - cookies_pkl_path
# 5 - paths.secret_or_open_account_xPath
# 6 - secret_or_open_account_xPath
# 7 - like_button_xPath
# 8 - close_dialog_window_xPath
# 9 - close_post_window_xPath
# endregion



# Kütüphane:
# region Python Dosyaları:
# 1 - login.py = Giriş sayfasıdır.
# 2 - main.py = Menü sayfasıdır.
# 3 - accounts_informations.py = Hesap bilgileri sayfasıdır.
# 4 - auto_follow.py = Otomatik takip sayfasıdır.
# 5 - paths.py = Tüm pathlerin sayfasıdır.
# endregion

# region Veritabanları:
# 1 - auto_follow.db =  Username_To_Follow, Temporary_Follow_Count, Permanent_Follow_Count
# 2 - accounts_informations.db = Pilot_Account, Followers, Follows, Profile_Count, Mutual_Followers, Non_Mutual_Followers, Fan_Followers
# 3 - login.db = Accounts_Data
# 4 - proxy_list.txt
# endregion

# region Çerez Dosyaları:
# 1 - cookies.pkl
# 2 - cookies_pilot_account.pkl
# endregion

# region Asset'ler
# 1 - play.png
# 2 - pause.png
# 3 - logo.png
# 4 - background_music.mp3
# endregion