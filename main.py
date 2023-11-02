import os
from tkinter import *
from tkinter import filedialog, messagebox
from tkinter.ttk import Combobox

import yaml

from script import audio_tool, whisper_tool


with open('config.yaml', encoding='utf-8') as f:
    config = yaml.load(f.read(), Loader=yaml.FullLoader)


def generate_subtitle(input, lang='en', model_size='base'):

    print('input='+input)
    print('lang='+lang)

    last_dot_index = input.rfind('.')
    mp3_output = input[:last_dot_index]+'.mp3'
    srt_output = input[:last_dot_index]+'.srt'

    print('audio extract begin')
    audio_tool.audio_extract(input, mp3_output)
    print('audio extract success')

    print('whisper begin')
    whisper_tool.do_whisper(audio=mp3_output, srt_path=srt_output, language=lang,
                            model_size=model_size,
                            model_download_root=config['model_download_root'])
    print('whisper success')

    print('remove temporary file')
    os.remove(mp3_output)

    print('success')


if __name__ == '__main__':

    window = Tk()
    ws = window.winfo_screenwidth()
    hs = window.winfo_screenheight()
    w = 300
    h = 180
    x = (ws/2) - (w/2)
    y = (hs/2) - (h/2)
    window.geometry('%dx%d+%d+%d' % (w, h, x, y))
    window.resizable(False, False)
    window.title('Extract subtitle')

    model_frame = Frame(window)
    model_frame.pack(fill='both', pady=10)
    model_lbl = Label(model_frame, text='MODEL', width=10)
    model_lbl.pack(side=LEFT)
    model_combo = Combobox(model_frame, state='readonly')
    model_combo['values'] = ('tiny.en', 'tiny', 'base.en', 'base', 'small.en',
                             'small', 'medium.en', 'medium', 'large-v1', 'large-v2', 'large')
    model_combo.current(3)
    model_combo.pack(side=LEFT, ipadx=26)

    lang_frame = Frame(window)
    lang_frame.pack(fill='both', pady=10)
    lang_lbl = Label(lang_frame, text='LANGUAGE', width=10)
    lang_lbl.pack(side=LEFT)
    lang_combo = Combobox(lang_frame, state='readonly')
    lang_combo['values'] = ('en', 'ja', 'zh')
    lang_combo.current(0)
    lang_combo.pack(side=LEFT, ipadx=26)

    def choose_file():
        files = filedialog.askopenfilenames(
            filetypes=[('Video files', '*.mp4 *.flv *.avi *.mkv'), ('All files', '*.*')])
        if files is not None:
            file_txt.delete(0, END)
            file_txt.insert(0, ';'.join(files))

    file_frame = Frame(window)
    file_frame.pack(fill='both', pady=10)
    file_lbl = Label(file_frame, text='FILE PATH', width=10)
    file_lbl.pack(side=LEFT)
    file_txt = Entry(file_frame)
    file_txt.pack(side=LEFT)
    file_btn = Button(file_frame, text='CHOOSE', command=choose_file)
    file_btn.pack(side=LEFT, padx=8)

    def clicked():
        lang = lang_combo.get()
        inputs = file_txt.get()
        model_size = model_combo.get()
        if inputs is None or inputs == '':
            messagebox.showerror('Error', 'No file path')
            return
        inputs = inputs.strip(';').split(';')
        file_btn.config(state='disabled')
        btn.config(text='Extracting...please wait', state='disabled')
        try:
            for index, input in enumerate(inputs):
                btn.config(
                    text=f'Extracting {index+1}/{len(inputs)}, please wait')
                btn.update()
                generate_subtitle(input=input, lang=lang,
                                  model_size=model_size)
            messagebox.showinfo('Info', 'Extract successfully!')
        except RuntimeError as err:
            messagebox.showerror('Generate Error', err)
        finally:
            file_btn.config(state='normal')
            btn.config(text='EXTRACT', state='normal')
    btn = Button(window, text='EXTRACT', command=clicked)
    btn.pack()

    window.mainloop()
