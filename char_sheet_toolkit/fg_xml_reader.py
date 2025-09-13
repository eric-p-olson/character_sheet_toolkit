import importlib
import os
import pprint
import sys
from lxml import etree
from pathlib import Path

from markdownify import markdownify

from char_sheet_toolkit.mako_render import mako_render

_location = os.path.dirname(__file__)


class PcElement(etree.ElementBase):
    """lxml derived element class to support xml children as class attributes
        https://lxml.de/2.0/element_classes.html
    """

    def __getattr__(self, name):
        """called when __getattributre__ fails
           access xml children as attributes
              <a><b><c>XYZ</c></b></a>                         => a.b.c == XYZ
              <a><id-01><name>Z</name><val>X</val></id-01></a> => a.Z.val == X
        """
        for child in self:
            if child.tag == name or child.tag == name.replace('_', ' '):
                if len(child) == 0:
                    return child.text  # leaf gives text value
                else:
                    return child  # recursively resolve xml tree as attributes
        for child in self:
            if child.tag.startswith('id-'):  # 'id-list' gets searched for 'name'
                id_name = child.find('name')
                if id_name is not None and id_name.text == name:
                    return child
                if id_name is not None and id_name.text == name.replace('_', ' '):
                    return child

        raise AttributeError(f"Attribute '{name}' not found")

    def __contains__(self, key):
        """find child tag"""
        key_child = self.find(key)
        return key_child is not None

    def get_text(self, key):
        """find child tag and return child's text field"""
        key_child = self.find(key)
        if key_child is not None:
            return key_child.text
        return None

    def get_kwargs(self):
        """get a kwargs style hash to pass children as independent variables"""
        kwargs = {}
        for child in self:
            key = child.tag
            if not list(child):  # No children, use text
                kwargs[key] = child.text.strip() if child.text else None
            else:  # Child has sub-elements
                kwargs[key] = child  # element_to_kwargs(child)
        return kwargs

    def tostring(self, xpath=None, method="text", encoding="unicode"):
        """get text version supporting formattedtext - (as xml, text, or markdown)"""
        pretty_print = True
        element = self
        if xpath is not None:
            element = element.find(xpath)
        data_type = element.get('type', None)
        if data_type is None:
            return etree.tostring(element, method='xml', pretty_print=True, encoding=encoding)
        elif data_type == 'formattedtext':  # html
            if method == 'markdown':
                html = etree.tostring(element, method='html', encoding='unicode')
                markdown = markdownify(html)
                return markdown
            else:
                return etree.tostring(element, method=method, pretty_print=pretty_print, encoding=encoding)
        else:
            return element.text

    # def to_dict(self):
    #     return etree_to_dict(self)


def pc_xml_fromstring(text):
    parser_lookup = etree.ElementDefaultClassLookup(element=PcElement)
    parser = etree.XMLParser(remove_blank_text=True, remove_comments=True)
    parser.set_element_class_lookup(parser_lookup)
    return etree.XML(text, parser=parser)


def pc_xml_fromfile(filename):
    tree = etree.ElementTree()
    parser_lookup = etree.ElementDefaultClassLookup(element=PcElement)
    parser = etree.XMLParser(remove_blank_text=True, remove_comments=True)
    parser.set_element_class_lookup(parser_lookup)
    tree.parse(source=filename, parser=parser)
    return tree


def get_fg_xml_schema(xml_tree):
    """from <root version="4.5" dataversion="20230911" release="8.1|CoreRPG:6">
         ==> CoreRPG_8_1
       Is there a better way to get the character format? Is this really a schema?
    """
    root_release = xml_tree.getroot().get('release', "?")
    sub_type, core_type = root_release.split('|')
    sub_type = sub_type.replace('.', '_')
    core_type = core_type.split(':')[0]
    return core_type, sub_type
