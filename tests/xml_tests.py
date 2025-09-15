import os
import sys
import unittest
from pathlib import Path
from lxml import etree

# import xml.etree.ElementTree as ET
# import yaml

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
# flake8: noqa: E402
from char_sheet_toolkit.mako_render import mako_render, mako_render_str
from char_sheet_toolkit.pc_data import PCData, etree_to_dict
from char_sheet_toolkit.fg_xml_reader import (
    pc_xml_fromstring,
    pc_xml_fromfile,
    PcElement,
)
from char_sheet_toolkit.pc_yaml import write_pc_yaml, read_pc_yaml

_location = os.path.dirname(__file__)


class TestXML(unittest.TestCase):

    def test_pc_data(self):
        parser_lookup = etree.ElementDefaultClassLookup(element=PcElement)
        parser = etree.XMLParser()
        parser.set_element_class_lookup(parser_lookup)

        char_data = parser.makeelement("character")
        etree.SubElement(char_data, "name").text = "Jazz"
        # etree.dump(char_data)
        self.assertTrue(isinstance(char_data, PcElement))
        self.assertEqual(
            "<character><name>Jazz</name></character>",
            etree.tostring(char_data, encoding="unicode"),
        )

        char_xml = """
        <character>
            <name>Jazz</name>
            <defenses><ac><total type="number">16</total></ac></defenses>
            <coins>
                <id-00001><amount type="number">1</amount><name type="string">PP</name></id-00001>
                <id-00002><amount type="number">24</amount><name type="string">GP</name></id-00002>
                <id-00003><amount type="number">2</amount><name type="string">EP</name></id-00003>
                <id-00004><amount type="number">3</amount><name type="string">SP</name></id-00004>
                <id-00005><amount type="number">4</amount><name type="string">CP</name></id-00005>
            </coins>
        </character>
        """
        char_data = pc_xml_fromstring(char_xml)

        # print(f" => {etree.tostring(char_data, encoding="unicode")}")
        self.assertEqual("Jazz", char_data.name)
        self.assertEqual("16", char_data.defenses.ac.total)
        self.assertEqual("24", char_data.coins.GP.amount)

    def test_read_xml(self):
        args_xml = os.path.join(_location, "SiRD.xml")
        pc = PCData(args_xml)
        char_data = pc.character_data()
        self.assertEqual("Sir D", char_data.name)
        print(f"Read: {args_xml}: {pc.format}")
        # etree.dump(char_data)
        self.assertEqual("20", char_data.abilities.charisma.score)
        char_dict = etree_to_dict(char_data)
        # pprint.pp(char_dict)
        self.assertEqual(
            "20", char_dict["character"]["abilities"]["charisma"]["score"]["#text"]
        )

        # print(yaml.dump(char_dict, default_flow_style=False))

    def test_mako_eval(self):
        args_xml = os.path.join(_location, "SiRD.xml")
        pc = PCData(args_xml)
        char_data = pc.character_data()
        # print(etree.tostring(char_data, pretty_print=True, method='XML', encoding="utf-8").decode())

        mako_rendered = mako_render_str("!! ${PC.name} !!", char_data)
        self.assertEqual("!! Sir D !!", mako_rendered)

        mako_data = (
            "${name}, Str: ${abilities.strength.score} (${abilities.strength.bonus|signed}) "
            "Cha: ${abilities.charisma.score} (${abilities.charisma.bonus|signed})"
        )
        mako_rendered = mako_render_str(mako_data, char_data)
        self.assertEqual("Sir D, Str: 12 (+1) Cha: 20 (+5)", mako_rendered)

        mako_data = "${featlist.Hacker.tostring(xpath='text')}"
        mako_rendered = mako_render_str(mako_data, char_data)
        self.assertEqual("You gain the following benefit.", mako_rendered[:31])

    def test_mako_markdown_eval(self):
        args_xml = os.path.join(_location, "SiRD.xml")
        pc = PCData(args_xml)
        char_data = pc.character_data()

        feature = char_data.featurelist.Spellcasting
        chk_markdown = feature.tostring(xpath="text", method="markdown")
        self.assertEqual(
            "***Cantrips.*** You know four Sorcerer cantrips", chk_markdown[251:298]
        )

        mako_data = (
            "${featurelist.Spellcasting.tostring(xpath='text', method='markdown')}"
        )
        mako_rendered = mako_render_str(mako_data, char_data)
        self.assertEqual(chk_markdown, mako_rendered)

        mako_data = (
            "${featurelist.Spellcasting.tostring('text', method='html') | markdown}"
        )
        mako_rendered = mako_render_str(mako_data, char_data)
        self.assertEqual(chk_markdown.strip(), mako_rendered.strip())

    # def test_yaml_read_write(self):
    #     args_xml = "jazz_4_3_spellz.xml"
    #     char_data = PCData()
    #     xml_data = FgXmlReader(args_xml)
    #     xml_data.extract_character_data(char_data)
    #     write_pc_yaml('jazz_4_3_spellz.yaml', char_data)
    #     char_data2 = PCData()
    #     read_pc_yaml('jazz_4_3_spellz.yaml', char_data2)
    #     self.assertEqual(char_data, char_data2)

    def test_extra_prop(self):
        args_xml = os.path.join(_location, "SiRD.xml")
        pc = PCData(args_xml)
        char_data = pc.character_data()
        # etree.dump(char_data)
        self.assertEqual("3", char_data.powers.Hacker.prepared)
        self.assertEqual("5", char_data.powers.Sorcery_Points.prepared)

        args_xml = os.path.join(_location, "SiRD.xml")
        pc = PCData(args_xml)
        char_data = pc.character_data()
        # etree.dump(char_data)
        self.assertEqual("1d8/5d6", char_data.multiclass.hddie)

    def test_mako_render(self):
        args_xml = os.path.join(_location, "SiRD.xml")
        mako_template = os.path.join(_location, "abilities.mako")

        args_xml = os.path.join(_location, "SiRD.xml")
        pc = PCData(args_xml)
        char_data = pc.character_data()
        output = mako_render(mako_template, char_data)
        output = "\n".join(output.splitlines())
        print(output)

        outfile = f"{Path(args_xml).stem}_{Path(mako_template).stem}.md"
        with open(outfile,'w') as f: f.write(output) ## rewrite output check file after changing template
        with open(outfile) as f:
            output_check = f.read()
        self.maxDiff = None
        self.assertEqual(output, output_check)

    def test_mako_render_character_info(self):
        args_xml = os.path.join(_location, "SiRD.xml")
        pc = PCData(args_xml)
        char_data = pc.character_data()
        mako_template = os.path.join(pc.format_dir, f"{pc.format}-character.mako")
        output = mako_render(mako_template, char_data)
        output = "\n".join(output.splitlines())
        print(output)

        outfile = f"{Path(args_xml).stem}_{Path(mako_template).stem}.md"
        with open(outfile, "w") as f:
            f.write(output)  ## rewrite output check file after changing template
        with open(outfile) as f:
            output_check = f.read()
        self.maxDiff = None
        self.assertEqual(output, output_check)


if __name__ == "__main__":
    unittest.main()
