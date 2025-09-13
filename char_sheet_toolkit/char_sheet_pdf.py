import os
import pprint
import shutil
# import pprint

from pathlib import Path

import pypdf.generic
import yaml
from pypdf import PdfReader, PdfWriter
from pypdf.generic import NameObject, ArrayObject, DictionaryObject, NumberObject

from char_sheet_toolkit.fg_xml_reader import PcElement
from char_sheet_toolkit.mako_render import mako_render_str, mako_render
from char_sheet_toolkit.pc_data import PCData

_location = os.path.dirname(__file__)


# [field dictionary]
# object 7 (stream: False)
# <<
#   /Type /Annot    [object type/subtype]
#   /Subtype /Widget
#   /AP <<        [appearance stream]
#     /N 19 0 R   [normal display ref]
#   >>
#   /DA (0.000000 0.000000 0.000000 rg /ComicSansMS 18.000000 Tf)   [default appearance - after re-filled]
#   /DV (ABC xyz 123)  [default value - when reset]
#   /F 4       [annotation flags: invisible, hidden, print, no-zoom, ...]
#   /FT /Tx    [widget type (Tx. Btn, Ch, Sig)]
#   /Ff 0      [field flags:  (... multi-line,no_export,required,read_only) ]
#   /FontName (Comic Sans MS)    [not sure if used]
#   /MK <<     [appearance - icons, captions, border style, background color, text appearance]
#     /BC [ 0 0 0 ]
#     /BG [ 1 1 1 ]
#   >>
#   /P 4 0 R    [page object ref]
#   /Rect [ 162.324 692.983 376.149 768.143 ]
#   /T (Text_Name)    [field name]
#   /TU (Text_Label)  [field label]
#   /V (ABC abc 123)   [value]
#   ---
#   /TM  (?)      [mapping name for export]
#   /AA  <<?>>    [additional actions]
#   /Q ?          [quadding/justification - 0: left, 1: center, 2: right]
#   /DS (?)       [rich text default style]
#   /RV (?)       [rich text - xhtml]
#   /AS  /Yes     [appearance state when /AP has multiple dict]
#   /Opt[(Yes)]   [true option for checkbox (multiple  /AP dict?)]
# >>

def get_field_button_states(field):
    """figure out /_States_ for a button if not in field: probably we need to look at kid fields"""
    button_states = ['/Yes', '/Off']
    if '/Kids' in field:
        for k in field['/Kids']:
            kid = k.get_object()
            if '/Opt' in kid and isinstance(kid['/Opt'], ArrayObject):
                button_states[0] = str(kid['/Opt'][0])
            elif '/AP' in kid and '/N' in kid['/AP'] and isinstance(kid['/AP']['/N'], DictionaryObject):
                button_states[0] = next(iter(kid['/AP']['/N']))
    return button_states


def get_field_button_option(field, value):
    """return the button option names for [True,False]
        value should be str: '0' or '1', but can work as other
    """
    if '/_States_' in field:
        button_states = field.get('/_States_')
    else:
        button_states = get_field_button_states(field)
    button_option = button_states[1 - int(value)]  # value is str/int of 0/1
    return button_option


def utf16be(text):
    """fdf string must be utf16be if they are not ascii"""
    if any(ord(c) > 127 for c in text):
        utf16_be = text.encode("utf-16-be")  # Convert to UTF-16 Big-Endian bytes
        return "þÿ" + "".join(chr(b) for b in utf16_be)  # Convert bytes to %XX format
    else:
        return text


# -- legacy code looking at the full field --
# if '/Opt' in field and isinstance(field['/Opt'], ArrayObject):
#     true_opt = str(field['/Opt'][0])
# elif '/AP' in field and '/N' in field['/AP'] and isinstance(field['/AP']['/N'], DictionaryObject):
#     true_opt = next(iter(field['/AP']['/N']))


class CharSheetPdf:
    """Populate PDF with data
          <form>.pdf - pdf form
               '/T' (name) - reference
               '/TU' (label) - xml data association (import, checkbox values, etc)
               '/DV' (default text): mako string used to populate field
               '/V' (value):
                   text: overwritten by eval value (ENHANCEMENT - 'revision mode': only blank /V is overwritten)
                   checkbox: populate with (boolean) pc data matching '${field_name}'
          <form>-properties.mako - prepare data specific to this form
          <form>-map.yaml - map pdf field names to xml data names (overwrite pdf field element values)
    """

    def __init__(self, pdf_filename):
        self.doc_name = pdf_filename
        self.reader = PdfReader(self.doc_name)
        self.writer = PdfWriter()
        self.writer.append(self.reader)  # pre-populate writer with FORMs
        self.mapping = self.read_map_yaml()

    def fill_form(self, pc_data: PCData, pdf_filename=None):
        """
        Populate a PDF form with data from a field_assignment dictionary.
          apply form specific properties from <name>-properties.py
          fill in field_assignments for fields from pc_data xml
          save as pdf_filename (if defined)
        """

        self.apply_form_properties(pc_data)
        field_assignments = self.assign_fields(pc_data.character_data())
        # pprint.pp(field_assignments)
        self.writer.update_page_form_field_values(
            None, field_assignments,
            auto_regenerate=True,
        )
        if pdf_filename is not None:
            self.save(pdf_filename)

    def apply_form_properties(self, pc_data: PCData):
        """ read form's associated properties (<name>-properties.py) and apply them to the pc_data xml """
        form_path = Path(self.doc_name).parent
        form_properties_file = Path(self.doc_name).stem + "-properties"
        if os.path.isfile(os.path.join(form_path, form_properties_file + ".py")):
            pc_data.run_character_data_plugin(form_properties_file, directory=form_path)
        else:
            print("Debug - no form properties file: {os.path.join(form_path, form_properties_file)}")

    def assign_fields(self, character_data: PcElement):
        """Go through the fields in pdf and find the corresponding pc_data"""
        field_assignments = {}
        fields = self.reader.get_fields()
        for f in fields:
            field = fields[f]
            field_name = str(f)  # '/T', but with hierarchy
            # if field_name != field.get('/T'): # hierarchical check
            #     print(f" {field_name} =>  '{str(field.get('/T'))}'")
            #     print(field)
            field_label = self.get_field_value('/TU', field, field_name=field_name)
            if field_label == '':  # deliberately mapped empty
                continue
            if field_label is None:
                if '/FT' in field:  # real form field, not hierarchical parent field
                    print(f"Error - field label (/TU) missing for {field_name} (use pdf mapping generation)")
                continue
            if field.get("/FT") == "/Btn":  # checkbox
                if field.get("/Ff", 0) == 65536:  # upload flag: not checkbox
                    continue
                property_value = mako_render_str(f"${{{field_label}}}", character_data,
                                                 debug_info=f" in btn field '{field_name}'")
                if property_value is not None and property_value != "":
                    field_assignments[field_name] = get_field_button_option(field, property_value)
                    # print(f"FOUND - {field_name} '{field_label}': {property_value} ({field_assignments[field_name]})")
            elif field.get("/FT") == "/Tx":  # text
                field_default = self.get_field_value('/DV', field, field_name=field_name)
                if field_default is not None and field_default != "":
                    field_value_eval = mako_render_str(field_default, character_data,
                                                       debug_info=f" in Tx field '{field_name}'")
                    field_assignments[field_name] = str(field_value_eval)
                    # print(f"FOUND TXT {field_name} {field_default}=>{field_value_eval}")
            else:
                pass  # non-text, non-checkbox
                # print(f"CHK - {field_name} ({field.get("/FT")}/{field.get("/Ff")}): skipped")
                # print(field)
        return field_assignments

    def get_field_value(self, fld_entry, field, field_name=None, default=None):
        """get pdf field value from entry. Override with mapping file data"""
        if field_name is None:
            field_name = field['/T']
        field_value = field.get(fld_entry, default)
        if field_name in self.mapping:
            field_value = self.mapping[field_name].get(fld_entry, field_value)
        return field_value

    def create_fdf(self, pc_data: PCData, pdf_filename):
        """
        Populate a PDF fdf with data from a field_assignment dictionary.
          apply form specific properties from <name>-properties.py
          fill in field_assignments for fields from pc_data xml
          create copy of pdf for fdf to overwrite
          populate fdf with form fields (based on mako template of a fdf)
        """
        self.apply_form_properties(pc_data)
        field_assignments = self.assign_fields(pc_data.character_data())

        pdf_output_file = Path(pdf_filename)
        pdf_output_file.unlink(missing_ok=True)
        shutil.copy(self.doc_name, pdf_output_file)  # create copy of master for fdd to overwrite

        fdf_template = os.path.join(_location, 'fdf.mako')
        fdf_txt = mako_render(fdf_template, pc_data.character_data(),
                              {'field_assignments': field_assignments, 'base_pdf_file': pdf_output_file})
        fdf_output_file = Path(pdf_output_file.stem + ".fdf")
        with open(fdf_output_file, "w") as file:
            file.write(fdf_txt)

    def save(self, pdf_filename):
        """save pdf data as pdf_filename"""
        pdf_output_file = Path(pdf_filename)
        print(f"Info - saving {pdf_output_file.name}")
        pdf_output_file.unlink(missing_ok=True)  # delete old
        with open(pdf_output_file, "wb") as output_file:
            self.writer.write(output_file)

    def read_map_yaml(self):
        """Used to map new 'T' and 'DV' fields to field entry
            get associated yaml file data (foo.pdf -> foo.map.yaml)
               {field_name}:
                 T: {field_label}
                 DV: {field_default_value}
        """
        pdf_file = Path(self.doc_name)
        pdf_yaml_file = pdf_file.with_stem(pdf_file.stem + "-map").with_suffix('.yaml')
        data = {}
        if os.path.isfile(pdf_yaml_file):
            with open(pdf_yaml_file, 'r') as file:
                try:
                    data = yaml.safe_load(file)
                    print(f"Reading YAML map file: {pdf_yaml_file}")
                    return data
                except yaml.YAMLError as exc:
                    print(f"Error reading YAML file: {exc}")
        else:
            print(f"Info - YAML map file not found: {pdf_yaml_file}")
        return data

    def create_mapping(self, output_mapping_file):
        """ Create .map.yaml file for a pdf - this allows any field property to be overwritten

        """
        new_mapping = {}
        fields = self.reader.get_fields()
        for f in fields:
            field = fields[f]
            field_name = str(f)  # '/T', but with hierarchy
            # if field_name != field.get('/T'): # hierarchical check
            #     print(f" {field_name} =>  '{str(field.get('/T'))}'")
            #     print(field)
            field_label = self.get_field_value('/TU', field, field_name=field_name)
            if field_label == '':  # deliberately mapped empty
                continue
            if field_label is None:
                if '/FT' in field:  # real form field, not hierarchical parent field
                    print(f"Error - field label (/TU) missing for {field_name} (use pdf mapping generation)")
                continue

            # for field_name in fields:
            #     field = fields[field_name]
            #     # field_label = field.get("/TU", field_name)
            #     if str(field_name) in self.mapping:
            #         mapped_field_name = self.mapping[field_name]['T']
            #     else:
            #         mapped_field_name = ''

            #     if field.get("/FT") == "/Btn":  # checkbox
            #         if field.get("/Ff", 0) == 65536:  # upload flag: not checkbox
            #             continue
            #         property_value = mako_render_str(f"${{{field_label}}}", character_data,
            #                                          debug_info=f" in btn field '{field_name}'")
            #         if property_value is not None and property_value != "":
            #             field_assignments[field_name] = get_field_button_option(field, property_value)
            #             # print(f"FOUND - {field_name} '{field_label}': {property_value} ({field_assignments[field_name]})")
            #     elif field.get("/FT") == "/Tx":  # text
            #         field_default = self.get_field_value('/DV', field, field_name=field_name)
            #         if field_default is not None and field_default != "":
            #             field_value_eval = mako_render_str(field_default, character_data,
            #                                                debug_info=f" in Tx field '{field_name}'")
            #             field_assignments[field_name] = str(field_value_eval)
            #             # print(f"FOUND TXT {field_name} {field_default}=>{field_value_eval}")
            #     else:
            #         pass  # non-text, non-checkbox
            #         # print(f"CHK - {field_name} ({field.get("/FT")}/{field.get("/Ff")}): skipped")
            #         # print(field)
            # return field_assignments

            if field.get("/FT") == "/Btn":  # checkbox
                if mapped_field_name and mapped_field_name != '?':
                    field_map[str(field_name)] = {'T': mapped_field_name}
                else:
                    field_map[str(field_name)] = {'T': ''}
                    print(f"Checkbox {field_name} not mapped")
            elif field.get("/FT") == "/Tx":  # text
                if '/V' in field:
                    field_value = str(field.get("/V"))
                else:
                    field_value = ''
                if mapped_field_name and mapped_field_name != '?':
                    if field_value != mapped_field_name:
                        print(f"Text {field_name} updated '{mapped_field_name}' -> '{field_value}'")
                    field_map[str(field_name)] = {'T': field_value, 'DV': '${' + field_value + '}'}
                elif field_value:
                    field_map[str(field_name)] = {'T': field_value, 'DV': '${' + field_value + '}'}
                else:
                    field_map[str(field_name)] = {'T': '', 'DV': ''}

        with open(output_mapping_file, 'w') as file:
            yaml.dump(field_map, file, default_flow_style=False)

        print(f"Updated PDF saved as: {output_mapping_file}")

    def debug_field(self):
        """debug the button fields: try to see why they might lose their background or border properties
            ** this is likely because the button itself uses a reference in the MK (not clean, just make new button)
        """
        page = self.writer.pages[0]
        print(page)
        for writer_annot in page.get('/Annots', []):
            if writer_annot.get('/FT') == '/Btn':
                button_obj = writer_annot.get_object()
                print(f"BUTTON: {button_obj['/T']} {button_obj}")
                if '/MK' in button_obj and '/BG' not in button_obj['/MK']:
                    mk = button_obj['/MK'].get_object()
                    print(f"   Button MK: {type(mk)}:{mk}")
                    mk[NameObject("/BG")] = ArrayObject([])  # transparent background
                    print(f"    afterBUTTON: {button_obj['/T']} {button_obj}")
