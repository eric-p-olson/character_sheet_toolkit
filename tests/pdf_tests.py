import os
# import pprint
import unittest
# import pymupdf

# from char_sheet_toolkit.char_sheet_mupdf import CharSheetMuPdf
from char_sheet_toolkit.char_sheet_pdf import CharSheetPdf
from char_sheet_toolkit.char_toolkit_utils import template_path
from char_sheet_toolkit.pc_data import PCData
# from char_sheet_toolkit.pc_yaml import write_pc_yaml

_location = os.path.dirname(__file__)


class TestPDF(unittest.TestCase):

    def test_fill_testform_pdf(self):
        """test form filling"""
        pdf_filename = os.path.join(template_path(), "DnD_2024_simple.pdf")
        pdf = CharSheetPdf(pdf_filename)

        character = "SiRD"
        xml_filename = os.path.join(_location, f"{character}.xml")
        pc = PCData(xml_filename=xml_filename)
        pdf.fill_form(pc, pdf_filename=f"{character}.pdf")

    def test_fill_testform_wotc_pdf(self):
        """test form filling"""
        # pdf_filename = "out2.pdf"
        pdf_filename = os.path.join(template_path(), "DnD_2024_wotc_character-sheet.pdf")
        pdf = CharSheetPdf(pdf_filename)

        character = "SiRD"
        xml_filename = os.path.join(_location, f"{character}.xml")
        pc = PCData(xml_filename=xml_filename)
        pdf.fill_form(pc, pdf_filename=f"{character}_wotc.pdf")

    def test_create_fdf(self):
        """test fdf creation"""
        # pdf_filename = "out2.pdf"
        pdf_filename = os.path.join(template_path(), "DnD_2024_wotc_character-sheet.pdf")
        pdf = CharSheetPdf(pdf_filename)

        character = "SiRD"
        xml_filename = os.path.join(_location, f"{character}.xml")
        pc = PCData(xml_filename=xml_filename)
        pdf.create_fdf(pc, pdf_filename=f"{character}_fdf.pdf")

    def test_create_mapping_file(self):
        pdf_filename = os.path.join(_location, "DnD_2024_wotc_character-Sheet.pdf")
        pdf = CharSheetPdf(pdf_filename)
        pdf.create_mapping("DnD_2024_Character-Sheet.new_map.yaml")


class TestUtilsPDF(unittest.TestCase):
    def test_compact_pdf(self):
        """debug - try compression on pypdf file"""
        pdf_filename = os.path.join(_location, "DnD_2024_simple.pdf")
        from pypdf import PdfReader, PdfWriter
        reader = PdfReader(pdf_filename)
        writer = PdfWriter()
        writer.append(reader)  # pre-populate writer with FORMs
        # writer = PdfWriter(clone_from=pdf_filename)

        writer.compress_identical_objects(remove_identicals=True, remove_orphans=True)

        for page in writer.pages:
            page.compress_content_streams()

        with open("out.pdf", "wb") as f:
            writer.write(f)
