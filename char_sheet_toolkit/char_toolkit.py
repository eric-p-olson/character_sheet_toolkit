"""character sheet toolkit"""
import argparse
import os
import tkinter as tk

from char_sheet_toolkit.pc_data import PCData
from char_sheet_toolkit.toolkit_gui import TkTop

_location = os.path.dirname(__file__)

root = None

def start_up_gui(pc_data: PCData):
    global root
    root = tk.Tk()
    _w1 = TkTop(pc_data=pc_data, top=root, )
    root.mainloop()

def argparse_cmdline():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("xml", help="FG xml filename")
    parser.add_argument("-v", "--verbose", help="increase output verbosity", action='store_true')
    parser.add_argument("-d", "--debug", help="maximize output verbosity", action='store_true')
    parser.add_argument("-o", metavar='output_file', help="write to file (default STDOUT)")
    parser.add_argument("-pdf", metavar='pdf_file', help="read pdf form")
    parsed_args = parser.parse_args()
    return parsed_args


if __name__ == '__main__':
    # args = argparse_cmdline()
    pc_data = PCData()
    start_up_gui(pc_data)

# old code
#         args_xml = "tests/jazz_4_3_spellz.xml"
#         character = FgXmlReader(args_xml)
#         #pprint.pp(character)
#
#         pdf_template = "tests/dnd_beyond_example.pdf"
#         pdf_form = PdfFormFiller(pdf_template)
#
#         pdf_form.display_fields()
#
#         pdf_form.create_pdf(output_pdf, character)
