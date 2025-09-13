""" functions creating derived properties
      Fantasy Grounds CoreRPG 8_1 format data (D&D 5e.24 rules)
"""
from lxml import etree


def properties(pc):
    print(f"Info -   deriving properties for {pc.name}")

    etree.SubElement(pc, "species").text = pc.race

    # adding on/off values for different skill proficiency types
    for skill in pc.xpath('./skilllist/*'):
        etree.SubElement(skill, "prof_norm").text = str(int(skill.prof == "1" or skill.prof == "2"))
        etree.SubElement(skill, "prof_expr").text = str(int(skill.prof == "2"))  # expertise
        etree.SubElement(skill, "prof_half").text = str(int(skill.prof == "3"))  # half prof

    # create multi-class composite fields
    combined_class_info = {'name': [], 'specialization': [], 'level': [], 'hddie': []}
    for c in pc.xpath('./classes/*'):
        for fld in combined_class_info.keys():
            if fld == 'hddie':
                combined_class_info[fld].append(f"{c.level}_{c.hddie}".replace('_1d','d'))
            elif fld in c:
                combined_class_info[fld].append(c.find(fld).text)
    class_elem = etree.SubElement(pc, "multiclass")
    for fld in combined_class_info.keys():
        etree.SubElement(class_elem, fld).text = '/'.join(combined_class_info[fld])

    # textual list of languages
    languages = []
    for lang in pc.xpath('./languagelist/*'):
        languages.append(lang.name)
    etree.SubElement(pc, "languages").text = ", ".join(languages)

    # textual list of weapon/tool proficiencies
    proficiencies = []
    for prof in pc.xpath('./proficiencylist/*'):
        proficiencies.append(prof.name)
    etree.SubElement(pc, "proficiencies").text = ", ".join(proficiencies)

