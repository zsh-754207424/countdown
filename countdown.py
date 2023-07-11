import tkinter as tk
import time
import threading
from pygame import mixer
from configparser import ConfigParser

ini = ConfigParser()
ini.read('conf.ini', encoding='utf8')

'''
剩余30秒开始，每隔5秒嘀一声，剩余10秒每一秒嘀一声，最后结束的时候有另一个提示音
'''

SECONDS = 60

cfg = ini['countdown']
BUTTON1 = int(cfg.get('BUTTON1'))
BUTTON2 = int(cfg.getint('BUTTON2'))
FLASH_TIME = int(cfg.getint('FLASH_TIME'))
BEEP_FREQ_TIME = int(cfg.getint('BEEP_FREQ_TIME'))
BEEP_TIME = int(cfg.getint('BEEP_TIME'))
BEEP_INTERVAL_TIME = int(cfg.getint('BEEP_INTERVAL_TIME'))
DEFAULT_CLOCK_TIME = int(cfg.getint('DEFAULT_CLOCK_TIME'))


class CountDown:

    def __init__(self):
        mixer.init()
        self.root = tk.Tk()
        self.root.wm_attributes('-topmost', 1)  # ui置顶
        self.root.title('倒计时')
        self.root.iconbitmap("gjdw.ico")

        self.root.rowconfigure(0, weight=1)
        self.root.columnconfigure(0, weight=1)
        self.root.columnconfigure(1, weight=3)

        # 创建一个frame窗体对象，用来包裹标签
        # 创建左侧框架
        self.left_frame = tk.Frame(self.root)
        self.left_frame.grid(row=0, column=0, sticky="nsew")

        # 创建右侧框架
        self.right_frame = tk.Frame(self.root)
        self.right_frame.grid(row=0, column=1, sticky="nsew")

        # init countdown
        self.countdown = None
        self.clock_time = None
        self.init_label()

        self.button1 = None
        self.button2 = None
        self.button_reset = None
        # self.button_stop = None

        self.init_button(btn=self.button1, button_conf=BUTTON1, txt='倒计时%d分' % BUTTON1)
        self.init_button(btn=self.button2, button_conf=BUTTON2, txt='倒计时%d分' % BUTTON2)
        self.init_button(btn=self.button_reset, button_conf=DEFAULT_CLOCK_TIME, txt='重置')
        self.root.protocol("WM_DELETE_WINDOW", self.no_closing)
        self.root.mainloop()

    def init_label(self, new_clock_time=DEFAULT_CLOCK_TIME, refresh=False):
        if self.countdown:
            self.countdown.destroy()
        self.clock_time = new_clock_time * SECONDS
        # self.clock_time = 13  # 该变量定义倒计时时间
        f_str = '%M:%S'
        if self.clock_time >= 3600:
            f_str = '%H:%M:%S'
        self.countdown = tk.Label(self.left_frame, text='%d' % self.clock_time, font=("Arial", 36), fg="red")
        self.countdown.config(text=str(time.strftime(f_str, time.gmtime(self.clock_time))))
        self.countdown.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        if self.clock_time > 0 and refresh:
            self.refresh_current_time()

    def reset_time(self, button_conf):
        self.stop()
        self.init_label(button_conf, button_conf!=DEFAULT_CLOCK_TIME)

    def init_button(self, btn, button_conf, txt):
        btn = tk.Button(self.right_frame, text=txt,
                        command=lambda: self.reset_time(button_conf),
                        width=8, height=1)
        btn.pack(padx=10, pady=5)

    def refresh_current_time(self):
        """刷新当前时间"""
        f_str = '%M:%S'
        if self.clock_time >= 3600:
            f_str = '%H:%M:%S'
        self.countdown.config(text=str(time.strftime(f_str, time.gmtime(self.clock_time))))
        self.clock_time -= 1
        if self.clock_time == FLASH_TIME - 1:
            self.flash()
        self.countdown.after(1000, self.refresh_current_time)
        if BEEP_FREQ_TIME < self.clock_time < BEEP_TIME and self.clock_time % BEEP_INTERVAL_TIME == BEEP_INTERVAL_TIME - 1:
            self.thread_play_sound(fn=lambda: self.play("beep-beep.wav"))
        elif self.clock_time < BEEP_FREQ_TIME:
            self.thread_play_sound(fn=lambda: self.play("beep-beep.wav"))
        if self.clock_time < 0:
            self.init_label(0)
            self.thread_play_sound(fn=lambda: self.play("ringing.wav"))

    def flash(self):
        bg = self.countdown.cget("background")
        fg = self.countdown.cget("foreground")
        self.countdown.configure(background=fg, foreground=bg)
        self.countdown.after(500, self.flash)

    def no_closing(self):  # 设置关闭方式的函数
        """
        设置点击窗口关闭按钮时要做的事
        :return:
        """
        self.root.quit()

    @staticmethod
    def play(file):
        mixer.music.set_volume(0.5)
        mixer.music.load(file)
        mixer.music.play()

    @staticmethod
    def stop():
        mixer.music.pause()

    @staticmethod
    def thread_play_sound(fn):
        thread = threading.Thread(target=fn)
        thread.daemon = True
        thread.start()


if __name__ == '__main__':
    my_countdown = CountDown()
