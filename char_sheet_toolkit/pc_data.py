"""
Dictionary for Character Data
"""
import importlib
import os
import sys
from collections import defaultdict
from pathlib import Path

from char_sheet_toolkit.fg_xml_reader import get_fg_xml_schema, pc_xml_fromfile

_location = os.path.dirname(__file__)


def etree_to_dict(t):
    """debug?"""
    d = {t.tag: {} if t.attrib else None}
    children = list(t)
    if children:
        dd = defaultdict(list)
        for dc in map(etree_to_dict, children):
            for k, v in dc.items():
                dd[k].append(v)
        d = {t.tag: {k: v[0] if len(v) == 1 else v
                     for k, v in dd.items()}}
    if t.attrib:
        d[t.tag].update(('@' + k, v)
                        for k, v in t.attrib.items())
    if t.text:
        text = t.text.strip()
        if children or t.attrib:
            if text:
                d[t.tag]['#text'] = text
        else:
            d[t.tag] = text
    return d


def convert_to_int(string):
    """convert bool/int string to int"""
    if string == 'True': return 1
    if string == 'False': return 0
    try:
        return int(string)
    except ValueError:
        return string


class PCData:
    format = None
    format_dir = None
    xml_filename = None
    xml_tree = None

    def __init__(self, xml_filename=None):
        if xml_filename:
            self.read_xml(xml_filename)

    def read_xml(self, xml_filename):
        self.xml_filename = xml_filename
        self.xml_tree = pc_xml_fromfile(xml_filename)
        base_type, sub_type = get_fg_xml_schema(self.xml_tree)
        self.format = f"{base_type}_{sub_type}"
        self.format_dir = os.path.join(_location, base_type)
        self.run_character_data_plugin(f"{self.format}-patch", directory=self.format_dir)
        self.run_character_data_plugin(f"{self.format}-properties", directory=self.format_dir)

    def character_data(self):
        return self.xml_tree.getroot().find('character')

    def run_character_data_plugin(self, plugin_name, directory=_location):
        """execute the plugin -
             check directory/plugin-type.py
             load module 'plugin-type' in sys.path
             execute function 'type'
        """
        if Path(os.path.join(directory, f"{plugin_name}.py")).is_file():
            print(f"Info - applying plugin: {plugin_name}")
            if directory not in sys.path:
                sys.path.insert(0, str(directory))
            module = importlib.import_module(plugin_name)
            plugin_func_name = plugin_name.split('-')[-1].lower()
            plugin_func = getattr(module, plugin_func_name)
            plugin_func(self.character_data())
