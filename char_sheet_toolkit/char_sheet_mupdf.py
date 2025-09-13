import os
import pprint
import re

"""Code for pymupdf - not actively used since it can't set the display font on filled out forms.
   This code is great for rendering images, etc
"""

import pymupdf
from pathlib import Path
import yaml

from char_sheet_toolkit.mako_render import mako_render_str
from char_sheet_toolkit.pc_data import PCData


# [field dictionary]
# object 7 (stream: False)
# <<
#   /Type /Annot    [object type/subtype]
#   /Subtype /Widget
#   /AP <<        [appearance stream]
#     /N 19 0 R   [normal display ref]
#   >>
#   /DA (0.000000 0.000000 0.000000 rg /ComicSansMS 18.000000 Tf)   [default appearance - after re-filled]
#   /DV (ABC abc 123)  [default value - when reset]
#   /F 4       [annotation flags: invisible, hidden, print, nozoom, ...]
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
#   /Opt[(Yes)]   [true option for checkbox]
# >>

class CharSheetMuPdf:
    def __init__(self, pdf_filename):
        self.font_list = None
        self.doc = pymupdf.open(pdf_filename)
        self.clean()

    def get_field_button_option(self, field, value):
        """return the button option names for True/False"""
        fld_xref = field.xref
        if value:
            opt_key = self.doc.xref_get_key(fld_xref, 'Opt')
            if opt_key[0] == 'array':
                return re.sub(r"\[\((.*?)\)\]", r"\1", opt_key[1])
            return 'Yes'
        return 'Off'

    def fill_form(self, pc_data: PCData):
        """This function fills the pdf form with data from the pd
           pdf form field_value: evaluated when form is filled (override in yaml)
           pdf form field_label: normally input, but used for output for blank/button entries
        """

        for page in self.doc:
            for field in page.widgets():
                field_name = field.field_name
                field_label = self.get_field_label(field, None)

                if field.field_type_string == 'CheckBox':
                    field_value = field.field_value
                    if field_label:
                        field_value = '${' + field_label + '}'
                    if yaml_data and field_name in yaml_data['fields'] and \
                            'value' in yaml_data['fields'][field_name] and \
                            yaml_data['fields'][field_name]:
                        field_value = yaml_data['fields'][field_name]
                    field_value_eval = mako_render_str(field_value, pc_data)
                    ###field_button_state = self.get_field_button_value(field)
                    fld_xref = field.xref
                    print(self.doc.xref_object(fld_xref, compressed=False))
                    chk_ap = field._annot._getAP()
                    print(f"CHK ap:: {chk_ap}")
                    opt0 = self.get_field_button_option(field, False)
                    opt1 = self.get_field_button_option(field, True)

                    # field.reset()
                    print(
                        f"CheckBox: {field_name}/{field_label}={field_value} => {field_value_eval}  => {field_button_state} -> ? [{opt0},{opt1}]")
                    fld_xref = field.xref
                    #print(self.doc.xref_object(fld_xref, compressed=False))
                    ### field.field_value = get_button_state_name(field_value_eval, field_button_state)
                    field.update()

                elif field.field_type_string == 'Text':
                    field_value = self.get_field_value(field, yaml_data)  # maybe use DV instead?
                    if len(field_value) > 2 and field_value[0] == '[':
                        field_value_eval = self.get_text_checkbox_value(field_name, field_value, pc_data)
                    else:
                        field_value_eval = mako_render_str(field_value, pc_data)
                        if field_value == field_value_eval and field_name in pc_data:
                            field_value_eval = pc_data[field_name]

                    field_font = field.text_font
                    # if field_font.endswith('bats'):
                    #     field_font = 'ITCZapfDingbats'  # 'ZaDb'
                    print(
                        f"Text: {field_name}/{field_label}={field_value} => {field_value_eval} [font {field.text_fontsize}] {field.text_font}")
                    font_point = next(filter(lambda font_pointx: font_pointx.startswith(field_font), self.font_list),
                                      None)
                    print(f"CHK font_point: {font_point}")
                    fld_xref = field.xref
                    (da_type, fld_da) = self.doc.xref_get_key(fld_xref, 'DA')
                    #print(f"{fld_xref}:{self.doc.xref_object(fld_xref, compressed=False)}")
                    print(self.doc.xref_get_keys(fld_xref))

                    # field.reset()
                    field.field_value = field_value_eval
                    # field.text_font = field_font
                    field.update()
                    field.text_font = field_font
                    self.doc.xref_set_key(fld_xref, 'DA',
                                          f"({fld_da})")  # restore default font (during form entry only)
                    if font_point:
                        print(f"CHK {field_name} font={field.text_font} ({" ".join(font_point.split()[-3:])})")
                        (apn_type, fld_apn) = self.doc.xref_get_key(fld_xref, 'AP/N')

                        # apn = template_pdf.xref_get_key(field.xref, "AP/N")
                        apm_ref = fld_apn.split()[0]
                        self.doc.xref_set_key(int(apm_ref), "Resources/Font", "null")
                        self.doc.xref_set_key(int(apm_ref), "Resources/Font/%s" % field_font,
                                              " ".join(font_point.split()[-3:]))
                        #print(f"xobject {apm_ref}: {self.doc.xref_object(int(apm_ref), compressed=False)}")
                        apn = field._annot._getAP()
                        print(f"CHK ap:: {apn}")
                        field._annot._setAP(apn.replace(b"Helv", (field_font.encode())))
                    else:
                        print(f"CHK- weird font {field_font}")
                    chk_ap = field._annot._getAP()
                    print(f"CHK ap:: {chk_ap}")
                    #field.reset()
                    #field.field_value = field_value_eval

                    #self.doc.xref_set_key(fld_xref, 'V', f"({field_value_eval})")
                    #self.doc.xref_set_key(fld_xref, 'DV', f"({field_value_eval})")
                    #field.update()
                    #chk_ap = field._annot._getAP()
                    #print(f"CHK ap:: {chk_ap}")

                    # field._annot._setAP(chk_ap.replace(b'Helv',field_font.encode()))
                    #chk_ap = field._annot._getAP()
                    #print(f"CHK ap:: {chk_ap}")

                    # ? self.doc.xref_set_key(fld_xref, 'DA', f"({fld_da})") # default font (during form entry only)
                    # self.doc.xref_set_key(fld_xref, 'AP/N', f"{fld_apn}")


                elif field.field_type_string == 'Text':
                    print(f"Info - {field_name} Button (portrait?)")
                else:
                    print(f"Check - {field_name} has unknown type {field.field_type_string}")
                print(
                    f"CHK: {field.field_name}/{field.field_label}={field.field_value} [font {field.text_fontsize}] {field.text_font}")
                fld_xref = field.xref
                #print(self.doc.xref_object(fld_xref, compressed=False))

    def get_text_checkbox_value(self, field_name, field_value, pc_data):
        if field_name not in pc_data:
            print(f"Warning - property {field_name} not found in character (assuming False) ")
            return field_value[1]
        prop_val = pc_data[field_name]  # TODO what if missing
        if isinstance(prop_val, int) and prop_val == 2:
            field_value_eval = field_value[3]
        elif isinstance(prop_val, int) and prop_val == 1:
            field_value_eval = field_value[2]
        elif isinstance(prop_val, int) and prop_val == 0:
            field_value_eval = field_value[1]
        elif prop_val == '':
            field_value_eval = field_value[1]
        else:
            print(f"DEBUG {field_name}={prop_val} ({field_value})")
            field_value_eval = field_value[1]
        # print(f"Info - select ding: {field_name}={type(prop_val)} {prop_val}=>'{field_value_eval}' ({field_value})")
        return field_value_eval

    def check_form(self, ref_data: PCData):
        """This function is to help create pdf/yaml pairs that can be used to read and fill-out pdf files
            pdf form field_name: original (can't be changed here)
            pdf form field_label: property associated to value when importing (override in yaml)
            pdf form field_value: evaluated when form is filled (override in yaml)
                value should be in mako format (form filled with rendered data)
                "?" will be replaced by the field_name
        """
        pdf_yaml_file = Path(Path(self.doc.name).stem + ".yaml")
        yaml_data = None
        ###if os.path.isfile(pdf_yaml_file):
        ###    yaml_data = self.read_yaml_data(pdf_yaml_file)
        for page in self.doc:
            for field in page.widgets():
                field_name = field.field_name
                field_label = self.get_field_label(field, yaml_data)
                field_value = self.get_field_value(field, yaml_data)
                field_appearance = self.get_field_appearance(field)  # /AS field - displayed value/state
                field_button_state = self.get_field_button_state(field)

                field_value_eval = mako_render_str(field_value, ref_data)

                if not field_label:  # fill-in label from valid character attribute in the field_value
                    if field_value in ref_data:
                        field_label = field_value

                if field_value in ref_data:  # mako-ize
                    field_value = '${' + field_value + '}'

                if not field_label and field.field_type_string == 'CheckBox':
                    if field_value == field_button_state[1] or field_appearance == field_button_state[1]:
                        print(
                            f"Check - CheckBox: {field.field_name} {field_label} is activated ({field_value}/{field_appearance})")

                if field_value == '?':
                    field_value = field_name
                    print(f"Check - {field.field_type_string} {field_name}: unmatched ('?' value replace)")
                elif not field_label:
                    pass  # print(f"Check - {field.field_type_string} {field_name}: unmatched ")

                # update check.pdf fields
                field.reset()
                field.field_label = field_label
                if field.field_type_string == 'CheckBox':
                    if field_label:
                        # print(f"CHK - set check box {field_name}/{field_label} to {field_button_state[1]}")
                        field.field_value = field_button_state[1]
                    field_value = ""
                elif field.field_type_string == 'Text':
                    field.field_value = field_value
                else:
                    print(f"Check - Unknown type {field.field_type_string}")
                # print(f"CHK {field_name}/{field_label}={field_value} => {field_value_eval}")
                field.update()

                # update check.yaml fields
                if yaml_data is None:
                    yaml_data = {'fields': {}}
                yaml_data['fields'][field_name] = {}
                yaml_data['fields'][field_name]['label'] = field_label
                if field_value:
                    yaml_data['fields'][field_name]['value'] = field_value

        self.save(alt="check", yaml_data=yaml_data)

    @staticmethod
    def get_field_label(field, yaml_data):
        """get field label"""
        if yaml_data and 'fields' in yaml_data and field.field_name in yaml_data['fields']:
            yaml_field_info = yaml_data['fields'][field.field_name]
            if 'label' in yaml_field_info and yaml_field_info['label']:
                return yaml_field_info['label']
        return field.field_label

    @staticmethod
    def get_field_value(field, yaml_data):
        if yaml_data and 'fields' in yaml_data and field.field_name in yaml_data['fields']:
            yaml_field_info = yaml_data['fields'][field.field_name]
            if 'value' in yaml_field_info:
                return yaml_field_info['value']
        return field.field_value

    def get_field_appearance(self, field):
        if field.field_type_string == 'CheckBox':
            appearance_state = self.doc.xref_get_key(field.xref, "AS")
            if appearance_state[0] == 'name':
                return appearance_state[1][1:]
        return None

    def clean(self):
        for page in self.doc:
            page.clean_contents(sanitize=True)
            xref = page.get_contents()[0]  # get xref of resulting /Contents
            content = page.read_contents()
            pattern = rb'q/Artifact.*?Pagination.*?atermark.*? EMC'
            result = re.sub(pattern, b"", content, count=1, flags=re.DOTALL)
            if result != content:
                self.doc.update_stream(xref, result)
        cat_xref = self.doc.pdf_catalog()
        form_fonts = self.doc.xref_get_key(cat_xref, "AcroForm/DR/Font")
        self.font_list = form_fonts[1][3:-2].split("/") if form_fonts[1] else []
        print(f"Debug CharSheetPdf.clean - set fonts: {self.font_list}")

    def print_form_entries(self):
        """ debug form
              print widgets
              dump png
        """
        for page in self.doc:
            for xref in range(1, self.doc.xref_length()):  # Iterate through all xref entries (starting from 1)
                print("")
                print("object %i (stream: %s)" % (xref, self.doc.xref_is_stream(xref)))
                try:
                    print(self.doc.xref_object(xref, compressed=False))
                except:
                    print('=')

            print(f"====== widgets page {page.number} =========")
            for field in page.widgets():
                field_appearance = self.get_field_appearance(field)
                if field_appearance:
                    appearance_info = '|' + field_appearance
                else:
                    appearance_info = ''
                print(f"pg {page.number}: '{field.field_name}'/'{field.field_label}' = "
                      f"{field.field_value}{appearance_info}  ({field.field_type_string}, {field.text_font})")
                fld_xref = field.xref
                print(f"   {fld_xref}:{self.doc.xref_object(fld_xref, compressed=False)}")
                print("    " + str(self.doc.xref_get_keys(fld_xref)))
                # fld_xref = field.xref
                # print(self.doc.xref_object(fld_xref, compressed=False))
            for annot in page.annots():
                print(f'Annotation on page: {page.number} with type: {annot.type} and rect: {annot.rect}')
            for image in page.get_images():
                print(f'Image on page: {image} ')

            pix = page.get_pixmap()
            pix.save(f"{Path(self.doc.name).stem}_page-{page.number}.png")

    def save(self, pdf_file=None, alt="copy", yaml_data=None):
        if pdf_file:
            pdf_output_file = Path(pdf_file)
        else:
            pdf_output_file = Path(Path(self.doc.name).stem + '_' + alt + ".pdf")
        print(f"saving {pdf_output_file.name}")
        pdf_output_file.unlink(missing_ok=True)
        self.doc.save(pdf_output_file.name, garbage=4)  # , deflate=True)
        if yaml_data:
            yaml_output_file = Path(pdf_output_file.stem + '_' + alt + ".yaml")
            with open(yaml_output_file, "w") as yaml_output_file:
                yaml.dump(yaml_data, yaml_output_file, default_flow_style=False)

#