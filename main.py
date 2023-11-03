import os
import queue
import sys
import threading
from tkinter import *
from tkinter import filedialog, messagebox
from tkinter.ttk import Combobox

import yaml

from script import audio_tool, whisper_tool


class Text_Queue(queue.Queue):
    def __init__(self, maxsize: int = 0) -> None:
        super().__init__(maxsize)

    def write(self, content):
        self.put(content)

    def flush(self):
        pass


class App():

    def __init__(self) -> None:

        self._running_thread: None | threading.Thread = None

        self.window = Tk()
        ws = self.window.winfo_screenwidth()
        hs = self.window.winfo_screenheight()
        w = 300
        h = 500
        x = (ws/2) - (w/2)
        y = (hs/2) - (h/2)
        self.window.geometry('%dx%d+%d+%d' % (w, h, x, y))
        self.window.resizable(False, False)
        self.window.title('Extract subtitle')

        model_frame = Frame(self.window)
        model_frame.pack(fill='both', pady=10)
        model_lbl = Label(model_frame, text='MODEL', width=10)
        model_lbl.pack(side=LEFT)
        self.model_combo = Combobox(model_frame, state='readonly')
        self.model_combo['values'] = ('tiny.en', 'tiny', 'base.en', 'base', 'small.en',
                                      'small', 'medium.en', 'medium', 'large-v1', 'large-v2', 'large')
        self.model_combo.current(3)
        self.model_combo.pack(side=LEFT, ipadx=26)

        lang_frame = Frame(self.window)
        lang_frame.pack(fill='both', pady=10)
        lang_lbl = Label(lang_frame, text='LANGUAGE', width=10)
        lang_lbl.pack(side=LEFT)
        self.lang_combo = Combobox(lang_frame, state='readonly')
        self.lang_combo['values'] = ('en', 'ja', 'zh')
        self.lang_combo.current(0)
        self.lang_combo.pack(side=LEFT, ipadx=26)

        def choose_file():
            files = filedialog.askopenfilenames(
                filetypes=[('Media files', '*.mp4 *.flv *.avi *.mkv *.mp3'), ('All files', '*.*')])
            if files is not None:
                self.file_txt.delete(0, END)
                self.file_txt.insert(0, ';'.join(files))

        file_frame = Frame(self.window)
        file_frame.pack(fill='both', pady=10)
        file_lbl = Label(file_frame, text='FILE PATH', width=10)
        file_lbl.pack(side=LEFT)
        self.file_txt = Entry(file_frame)
        self.file_txt.pack(side=LEFT)
        self.file_btn = Button(file_frame, text='CHOOSE', command=choose_file)
        self.file_btn.pack(side=LEFT, padx=8)

        def extract():
            self._update_status_text()
            self._running_thread = threading.Thread(
                target=self._extract, daemon=True)
            self._running_thread.start()

        self.btn = Button(self.window, text='EXTRACT', command=extract)
        self.btn.pack()

        self.status_txt = Text(self.window, height=180)
        self.status_txt.pack(pady=10, padx=10)
        self.status_txt.insert(INSERT, 'Click EXTRACT button to start')

        self.msg_queue = Text_Queue()
        sys.stdout = self.msg_queue

        self._update_status_text()

        # 关闭时，中止线程池
        self.window.protocol("WM_DELETE_WINDOW", self.on_closing)

    def on_closing(self):
        print('Closing app...')
        sys.exit(0)

    def run(self) -> None:
        """
        启动GUI循环
        """

        self.window.mainloop()

    def _update_status_text(self):
        """
        更新状态文本
        """

        while not self.msg_queue.empty():
            content = self.msg_queue.get()
            self.status_txt.insert(END, content)
            self.status_txt.see(END)
            self.status_txt.update()

        self.window.after(100, self._update_status_text)

    def _extract(self) -> None:
        """
        处理提取
        """

        lang = self.lang_combo.get()
        inputs = self.file_txt.get()
        model_size = self.model_combo.get()
        if inputs is None or inputs == '':
            messagebox.showerror('Error', 'No file path')
            return
        inputs = inputs.strip(';').split(';')
        self.file_btn.config(state='disabled')
        self.btn.config(text='Extracting...please wait', state='disabled')
        try:
            for index, input in enumerate(inputs):
                print('Extracting '+input)
                self.btn.config(
                    text=f'Extracting {index+1}/{len(inputs)}, please wait')
                self.btn.update()
                self._generate_subtitle(input=input, lang=lang,
                                        model_size=model_size)
            messagebox.showinfo('Info', 'Extract successfully!')
        except RuntimeError as err:
            messagebox.showerror('Generate Error', err)
        finally:
            self.file_btn.config(state='normal')
            self.btn.config(text='EXTRACT', state='normal')

    def _generate_subtitle(self, input, lang='en', model_size='base'):
        """
        生成字幕
        """

        with open('config.yaml', encoding='utf-8') as f:
            config = yaml.load(f.read(), Loader=yaml.FullLoader)

        print('input='+input)
        print('lang='+lang)

        last_dot_index = input.rfind('.')
        input_is_not_mp3 = input[last_dot_index:].lower() != '.mp3'
        mp3_output = input[:last_dot_index] + '.mp3' if input_is_not_mp3 else input
        srt_output = input[:last_dot_index]+'.srt'

        if input_is_not_mp3:
            print('audio extract begin')
            audio_tool.audio_extract(input, mp3_output)
            print('audio extract success')

        print('whisper begin')
        whisper_tool.do_whisper(audio=mp3_output, srt_path=srt_output, language=lang,
                                model_size=model_size,
                                model_download_root=config['model_download_root'])
        print('whisper success')

        print('remove temporary file')
        if input_is_not_mp3:
            os.remove(mp3_output)

        print('success')


if __name__ == '__main__':
    app = App()
    app.run()
