import os
import pprint

import yaml
from pypdf import PdfReader, PdfWriter
from pypdf.constants import AnnotationDictionaryAttributes
"""
OLD CODE :( 
 """


def dict_diff(dict1, dict2):
    # Find keys that are only in dict1
    only_in_dict1 = {key: dict1[key] for key in dict1 if key not in dict2}

    # Find keys that are only in dict2
    only_in_dict2 = {key: dict2[key] for key in dict2 if key not in dict1}

    # Find keys that are in both but have different values
    different_values = {key: (dict1[key], dict2[key]) for key in dict1 if key in dict2 and dict1[key] != dict2[key]}

    # Display the differences
    print("Keys only in the first dictionary:")
    print(only_in_dict1)

    print("\nKeys only in the second dictionary:")
    print(only_in_dict2)

    print("\nKeys in both dictionaries with different values:")
    print(different_values)


class PdfFormFiller:
    def __init__(self, pdf_form_file):
        self.reader = PdfReader(pdf_form_file)
        # self.display_fields(self.reader)
        self.field_map = self.extract_form_fields(self.reader)
        self.type_map = {'text': {}}
        self.read_yaml_overrides(pdf_form_file)

    def read_yaml_overrides(self, pdf_form_file):
        pdf_form_file_yaml = f"{os.path.splitext(pdf_form_file)[0]}.yaml"
        if os.path.isfile(pdf_form_file_yaml):
            yaml_data = self.read_yaml_data(pdf_form_file_yaml)
            for field_type in yaml_data:
                self.type_map[field_type] = yaml_data[field_type]['values']
                for field, value in yaml_data[field_type]['fields'].items():
                    self.field_map[field] = (value, field_type)

    def create_pdf(self, pdf_output_file: str, character: dict):
        form_values = {}

        for field, field_trait in self.field_map.items():
            trait = field_trait[0]
            trait_type = field_trait[1]
            if trait in character:
                value = character[trait]
                if value in self.type_map[trait_type]:
                    value = self.type_map[trait_type][value]
                form_values[field] = value
            else:
                if trait:
                    print(f"field: {field}: {trait} has no character data")
                elif trait != ' ':
                    print(f"field: {field} unmapped ({trait})")

        writer = PdfWriter(clone_from=self.reader)
        for page_no, page in enumerate(writer.pages):
            writer.update_page_form_field_values(
                page, form_values
            )
        writer.write(pdf_output_file)

    def extract_form_fields(self, reader) -> dict:
        form_map = {}
        form_fields = reader.get_fields()
        if form_fields:
            for field, field_info in form_fields.items():
                if '/V' in field_info:
                    value = field_info['/V']
                    form_map[field] = (value, 'text')
        else:
            print("Error - no forms found")
        return form_map

    def read_yaml_data(self, yaml_filename):
        with open(yaml_filename, 'r') as file:
            try:
                data = yaml.safe_load(file)
                return data
            except yaml.YAMLError as exc:
                print(f"Error reading YAML file: {exc}")

    def display_fields(self):
        field_data1 = {}
        if self.reader.get_fields():
            for field, field_info in self.reader.get_fields().items():
                if '/V' in field_info:
                    val = field_info['/V']
                    field_data1[field] = val
                    print(f"{field}: '{val}'")
                else:
                    field_data1[field] = '?'
                    print(f"{field}:")

        field_data2 = {}
        fields = []
        for page in self.reader.pages:
            for annot in page.annotations:
                annot = annot.get_object()
                if annot[AnnotationDictionaryAttributes.Subtype] == "/Widget":
                    fields.append(annot)
        for f in fields:
            field = f.get('/T','?')
            value = f.get('/V','?')
            field_data2[field] = value

        dict_diff(field_data1,field_data2)