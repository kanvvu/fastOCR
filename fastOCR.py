import tkinter as tk
from tkinter import messagebox
from PIL import ImageGrab, Image
import pytesseract
import pyperclip
import keyboard
from threading import Thread
import pystray
from json_config import check_and_return_config
import os

def copy_to_clipboard(text):
    pyperclip.copy(text)

class ScreenCaptureApp:
    def __init__(self, screen_scale, alpha_value, languages):
        self.screen_scale = screen_scale
        self.languages = languages
        self.alpha_val = alpha_value 

        master = tk.Tk()
        self.master = master
        master.title("fastOCR")
        self.master.attributes('-fullscreen', True)
        self.master.attributes('-topmost',True)
        self.app_quited = tk.BooleanVar(value=False)

        self.rect_id = 0
        master.attributes("-alpha", self.alpha_val)

        self.canvas = tk.Canvas(master, cursor="cross")
        self.canvas.pack(fill=tk.BOTH, expand=True)

        self.start_x = None
        self.start_y = None
        self.hidden = False 

        last_state = 0
        last_state_file = open("save.bin", "r")
        try:
            last_state = int(last_state_file.readline())
        except:
            messagebox.showerror("fastOCR ERROR", f"Couldn't read last selected languague from save.bin file")
        last_state_file.close()

        self.state = last_state 
        if self.state > len(languages):
            self.state = 0

        self.bind_events()
        print(f"{master.winfo_screenwidth()}, {master.winfo_screenheight()}")
        
        self.hide_app()
    

    def set_state(self, v):
        def inner(icon, item):
            self.state = v
        return inner

    def get_state(self, v):
        def inner(item):
            return self.state == v
        return inner

    def check_key(self):
        if self.hidden:
            self.show_app()
        else:
            self.hide_app()

    
    def show_app(self):
        self.master.deiconify()
        self.hidden = False

    def hide_app(self):
        self.master.withdraw()
        self.hidden = True

    
    def quit_app(self):
        self.icon.stop()
        self.app_quited.set(True)
    
    def check_destroy_window(self):
        if self.app_quited.get():
            self.master.destroy() 
            with open("save.bin", "w") as last_state_file:
                last_state_file.write(f"{self.state}")
        else:
            self.master.after(100, self.check_destroy_window)

    def start(self):
        self.master.after(100, self.check_destroy_window)
        language_item = pystray.MenuItem('Select language', pystray.Menu(lambda: (
            pystray.MenuItem(
                f'{lang}',
                self.set_state(i),
                checked=self.get_state(i),
                radio=True)
            for i, lang in enumerate(self.languages))))
        
        self.menu = pystray.Menu(language_item, pystray.MenuItem('Capture', self.show_app), pystray.MenuItem('Quit', self.quit_app))
        self.icon = pystray.Icon("Screen Capture app", icon=Image.open("icon.png"), menu=self.menu)
        Thread(target=self.icon.run).start()
        self.master.mainloop()

    def bind_events(self):
        self.canvas.bind("<ButtonPress-1>", self.on_press)
        self.canvas.bind("<B1-Motion>", self.on_drag)
        self.canvas.bind("<ButtonRelease-1>", self.on_release)
    
    def on_press(self, event):
        self.start_x = self.master.winfo_pointerx() 
        self.start_y = self.master.winfo_pointery()
        x, y = self.canvas.canvasx(event.x), self.canvas.canvasy(event.y)
        self.x_rect = x
        self.y_rect = y

    def on_drag(self, event):
        cur_x = self.master.winfo_pointerx()
        cur_y = self.master.winfo_pointery()
        
        self.canvas.delete(self.rect_id)
        x, y = self.canvas.canvasx(event.x), self.canvas.canvasy(event.y)
        self.rect_id = self.canvas.create_rectangle(self.x_rect,self.y_rect,x,y, outline="red")
        self.canvas.coords("selection", self.start_x, self.start_y, cur_x, cur_y)

    def on_release(self, event):
        cur_x = self.master.winfo_pointerx()
        cur_y = self.master.winfo_pointery()
        self.master.attributes("-alpha", 0.0)
        self.capture_screen(self.start_x, self.start_y, cur_x, cur_y)
        self.master.attributes("-alpha", self.alpha_val)

        # Clear the selection rectangle
        self.canvas.delete("selection")
        self.canvas.delete(self.rect_id)

        self.hide_app()

    def capture_screen(self, x1, y1, x2, y2):
        
        if x1 <= x2:
            if y1 > y2:
                temp_y1 = y1
                y1 = y2
                y2 = temp_y1 
        else:
            if y1 > y2:
                temp_x1 = x1
                temp_y1 = y1
                x1 = x2
                y1 = y2
                x2 = temp_x1
                y2 = temp_y1
            else:
                temp_x1 = x1
                x1 = x2
                x2 = temp_x1 

        
        try:
            screenshot = ImageGrab.grab(bbox=(x1*self.screen_scale, y1*self.screen_scale, x2*self.screen_scale, y2*self.screen_scale))
            screenshot.save("screenshot.png")
            print(f"Screenshot saved")
            ocr_text = pytesseract.image_to_string(screenshot, lang=self.languages[self.state])
            print(ocr_text)
            copy_to_clipboard(ocr_text)
        except Exception as e:
            messagebox.showerror("fastOCR ERROR", f"ERROR: {e}")


if __name__ == "__main__":
    try:
        config = check_and_return_config("config.json")
        app = ScreenCaptureApp(config['screen-scale'], config['alpha-value'], config['languages'])
        keyboard.add_hotkey(config['shortcut'], app.check_key)
        app.start()
    except Exception as e:
        messagebox.showerror("fastOCR ERROR", f"ERROR: {e}")