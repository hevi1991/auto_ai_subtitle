import os
from tkinter import *
from tkinter import filedialog, messagebox
from tkinter.ttk import Combobox

import yaml

from script import audio_tool, whisper_tool


with open('config.yaml', encoding='utf-8') as f:
    config = yaml.load(f.read(), Loader=yaml.FullLoader)


def generate_subtitle(input, lang='en', use_custom_model=True):

    print('input='+input)
    print('lang='+lang)

    last_dot_index = input.rfind('.')
    mp3_output = input[:last_dot_index]+'.mp3'
    srt_output = input[:last_dot_index]+'.srt'

    print('audio extract begin')
    audio_tool.audio_extract(input, mp3_output)
    print('audio extract success')

    print('whisper begin')
    whisper_tool.do_whisper(mp3_output, srt_output, lang, config['hf_model_path'] if use_custom_model else "",
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
    h = 150
    x = (ws/2) - (w/2)
    y = (hs/2) - (h/2)
    window.geometry('%dx%d+%d+%d' % (w, h, x, y))
    window.resizable(False, False)
    window.title('Extract subtitle')

    lang_frame = Frame(window)
    lang_frame.pack(fill='both', pady=10)
    lang_lbl = Label(lang_frame, text='language', width=10)
    lang_lbl.pack(side=LEFT)
    combo = Combobox(lang_frame, state='readonly')
    combo['values'] = ('en', 'ja', 'zh')
    combo.current(0)
    combo.pack(side=LEFT, ipadx=26)

    def choose_file():
        files = filedialog.askopenfilenames(
            filetypes=[('Video files', '*.mp4 *.flv *.avi *.mkv'), ('All files', '*.*')])
        if files is not None:
            file_txt.delete(0, END)
            file_txt.insert(0, ';'.join(files))

    file_frame = Frame(window)
    file_frame.pack(fill='both')
    file_lbl = Label(file_frame, text='file', width=10)
    file_lbl.pack(side=LEFT)
    file_txt = Entry(file_frame)
    file_txt.pack(side=LEFT)
    file_btn = Button(file_frame, text='CHOOSE', command=choose_file)
    file_btn.pack(side=LEFT, padx=8)

    use_custom_model_var = BooleanVar()
    model_check = Checkbutton(window, text='USE CUSTOM MODEL', variable=use_custom_model_var,
                              state='disabled' if config['hf_model_path'] == '' else 'normal')
    model_check.pack(ipady=6)

    def clicked():
        lang = combo.get()
        inputs = file_txt.get()
        use_custom_model = use_custom_model_var.get()
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
                                  use_custom_model=use_custom_model)
            messagebox.showinfo('Info', 'Extract successfully!')
        except RuntimeError as err:
            messagebox.showerror('Generate Error', err)
        finally:
            file_btn.config(state='normal')
            btn.config(text='EXTRACT', state='normal')
    btn = Button(window, text='EXTRACT', command=clicked)
    btn.pack()

    window.mainloop()
