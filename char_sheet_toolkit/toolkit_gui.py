import sys
import os.path
import tkinter as tk
import tkinter.ttk as ttk
from tkinter.constants import *
# from ttkthemes import ThemedTk

from tkinter import filedialog
from tkinter import scrolledtext

from char_sheet_toolkit.mako_render import mako_render
from char_sheet_toolkit.pc_data import PCData
from char_sheet_toolkit.pc_yaml import write_pc_yaml

theme_location = r'C:\Users\ericolso\AppData\Local\Programs\Python\Python312\Lib\site-packages\ttkthemes\themes'


class TkTop:
    def __init__(self, pc_data: PCData, top=None, ):
        """This class configures and populates the toplevel window.
           top is the toplevel containing window."""
        self.top = top
        self.pc_data = pc_data
        top.title("Character Sheet Toolkit")
        top.geometry("600x450")
        top.minsize(120, 1)
        top.maxsize(4612, 1421)
        top.resizable(1, 1)
        self.default_bg = '#FFFFFF'
        self.default_fg = '#000000'
        self.style = self.style_code('clearlooks')
        top.configure(bg=self.default_bg)

        self.top.protocol('WM_DELETE_WINDOW', self.top.destroy)  # click on the 'X'

        self.input_frame = ttk.Frame(self.top, width=100, height=200)
        self.input_frame.pack(side="left", fill="both", expand=False)

        self.character_frame = ttk.LabelFrame(self.top, width=100, height=200)
        self.character_frame.configure(relief='groove'),
        self.character_frame.configure(text='''Selected Character''')
        self.character_frame.pack(side="left", fill="both", expand=False)

        self.output_frame = ttk.Frame(self.top, width=100, height=200)
        self.output_frame.pack(side="left", fill="both", expand=False)

        self.character_text_box = tk.Text(self.character_frame)
        self.character_text_box.configure(wrap="word", width=45)
        self.character_text_box.configure(background=self.default_bg, foreground=self.default_fg)
        self.character_text_box.pack(pady=10, padx=5)

        self.char_xml_button = ttk.Button(self.input_frame)
        self.char_xml_button.configure(text='import xml', compound='left', width=11,
                                       takefocus=False, command=self.open_char_xml)
        self.char_xml_button.pack(pady=(30, 5), padx=5)
        self.char_pdf_button = ttk.Button(self.input_frame)
        self.char_pdf_button.configure(text='import pdf', compound='left', width=11,
                                       takefocus=False, command=self.unknown_button)
        self.char_pdf_button.pack(pady=5, padx=5)

        self.o1_button = ttk.Button(self.output_frame)
        self.o1_button.configure(text='export pdf', compound='left', width=11,
                                 takefocus=False, command=self.unknown_button)
        self.o1_button.pack(pady=(30, 5), padx=5)
        self.o2_button = ttk.Button(self.output_frame)
        self.o2_button.configure(text='export mako', compound='left', width=11,
                                 takefocus=False, command=self.output_mako)
        self.o2_button.pack(pady=5, padx=5)
        self.o3_button = ttk.Button(self.output_frame)
        self.o3_button.configure(text='export yaml', compound='left', width=11,
                                 takefocus=False, command=self.output_yaml)
        self.o3_button.pack(pady=5, padx=5)

    def style_code(self, theme_name):
        style = ttk.Style()
        if theme_name not in style.theme_names():
            self.top.tk.call('source', os.path.join(theme_location, theme_name, f"{theme_name}.tcl"))
        style.theme_use(theme_name)
        self.default_bg = style.lookup(theme_name, 'background')
        self.default_fg = style.lookup(theme_name, 'foreground')
        return style

    def update_character_text(self):
        self.character_text_box.delete("1.0", tk.END)  # Clear existing text
        if self.pc_data.format is not None:
            mako_template = os.path.join(self.pc_data.format_dir, f"{self.pc_data.format}-character.mako")
            char_data = self.pc_data.character_data()
            self.character_text_box.insert(tk.END, mako_render(mako_template, char_data))

    def open_char_xml(self):
        file_path = filedialog.askopenfilename(title="Select an xml File",
                                               filetypes=[("FG xml files", "*.xml")])
        if file_path:
            self.pc_data.read_xml(file_path)
            char_data = self.pc_data.character_data()
            print(f"Loaded {self.pc_data.format} xml: {char_data.name}")
        self.update_character_text()

    def output_mako(self):
        file_path = filedialog.askopenfilename(title="Select mako template to render",
                                               filetypes=[("mako template file", "*.mako")])
        if file_path:
            char_data = self.pc_data.character_data()
            output = mako_render(file_path, char_data)
            print(output)
    def output_yaml(self):
        file_path = filedialog.asksaveasfilename(title="Select output yaml File",
                                                 initialfile=f"{self.pc_data['name']}.yaml",
                                                 filetypes=[("character yaml file", "*.yaml")])
        if file_path:
            write_pc_yaml(file_path, self.pc_data)

    def unknown_button(self):
        print("unknown button")
