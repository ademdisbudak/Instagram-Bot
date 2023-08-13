import tkinter as tk

class CenteredWindow:

    def __init__(self):
        self.window = tk.Tk()
        self.configure_properties()

        self.create_components()
        self.center_window()

    def configure_properties(self):
        self.window.title("Centered Window")

    def create_components(self):
        label = tk.Label(self.window, text="Bu pencere ekranın tam ortasında görünecek.")
        label.pack(padx=10, pady=10)

        button = tk.Button(self.window, text="Kapat", command=self.window.quit)
        button.pack(pady=10)

    def center_window(self):
        self.window.update_idletasks()  # Pencere boyutunu almak için güncelleme yapılır
        screen_width = self.window.winfo_screenwidth()
        screen_height = self.window.winfo_screenheight()

        x = (screen_width - self.window.winfo_width()) // 2
        y = (screen_height - self.window.winfo_height()) // 2

        self.window.geometry(f"+{x}+{y}")  # Pencereyi ortalamak için konumlandırılır

    def run(self):
        self.window.mainloop()

if __name__ == "__main__":
    app = CenteredWindow()
    app.run()
