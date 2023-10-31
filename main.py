import os
from tkinter import *
from tkinter import filedialog, messagebox
from tkinter.ttk import Combobox

import yaml

from script import audio_tool, whisper_tool


def generate_subtitle(input, lang='en'):

    print('input='+input)
    print('lang='+lang)

    last_dot_index = input.rfind('.')
    mp3_output = input[:last_dot_index]+'.mp3'
    srt_output = input[:last_dot_index]+'.srt'

    with open('config.yaml', encoding='utf-8') as f:
        config = yaml.load(f.read(), Loader=yaml.FullLoader)
    print('audio extract begin')
    audio_tool.audio_extract(input, mp3_output)
    print('audio extract success')

    print('whisper begin')
    whisper_tool.do_whisper(mp3_output, srt_output, lang, config['hf_model_path'],
                            config['device'])
    print('whisper success')

    print('remove temporary file')
    os.remove(mp3_output)

    print('success')


if __name__ == '__main__':

    window = Tk()
    ws = window.winfo_screenwidth()
    hs = window.winfo_screenheight()
    w = 300
    h = 100
    x = (ws/2) - (w/2)
    y = (hs/2) - (h/2)
    window.geometry('%dx%d+%d+%d' % (w, h, x, y))
    window.resizable(False, False)
    window.title('Extract subtitle')

    lang_lbl = Label(window, text='language')
    lang_lbl.grid(column=0, row=0)
    combo = Combobox(window, state='readonly')
    combo['values'] = ('en', 'ja', 'zh')
    combo.current(0)
    combo.grid(column=1, row=0)

    def choose_file():
        files = filedialog.askopenfilenames(
            filetypes=[('Video files', '*.mp4 *.flv *.avi *.mkv'), ('All files', '*.*')])
        if files is not None:
            file_txt.delete(0, END)
            file_txt.insert(0, ';'.join(files))

    file_lbl = Label(window, text='file')
    file_lbl.grid(column=0, row=1)
    file_txt = Entry(window)
    file_txt.grid(column=1, row=1)
    file_btn = Button(window, text='CHOOSE', command=choose_file)
    file_btn.grid(column=2, row=1)

    def clicked():
        lang = combo.get()
        inputs = file_txt.get()
        if inputs is None or inputs == '':
            messagebox.showerror('Error', 'No file path')
            return
        inputs = inputs.strip(';').split(';')
        file_btn.config(state='disabled')
        btn.config(text='Extracting...please wait', state='disabled')
        for index, input in enumerate(inputs):
            btn.config(text=f'Extracting {index+1}/{len(inputs)}, please wait')
            btn.update()
            generate_subtitle(input=input, lang=lang)
        file_btn.config(state='normal')
        btn.config(text='EXTRACT', state='normal')
        messagebox.showinfo('Info', 'Extract successfully!')
    btn = Button(window, text='EXTRACT', command=clicked)
    btn.grid(column=1, row=2)

    window.mainloop()
