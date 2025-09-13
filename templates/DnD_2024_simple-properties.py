# additional properties needed for: dnd_5e24_simple.pdf
# TODO: 'senses',
from lxml import etree
from char_sheet_toolkit.CoreRPG.CoreRPG_dnd_2024_utils import weapon_info, use_boxes, generate_abbreviation


def properties(pc):
    print(f"Info -   deriving properties for template")

    # move armor proficiencies from list to checkboxes
    prof_list = [p.strip() for p in pc.proficiencies.split(",")]
    checkboxed_proficiencies = {
        'Armor: Light': 'light_armor',
        'Armor: Medium': 'medium_armor',
        'Armor: Heavy': 'heavy_armor',
        'Armor: Shields': 'shields',
    }
    proficiency_element = pc.find('proficiency')
    if proficiency_element is None:
        proficiency_element = etree.SubElement(pc, "proficiency")
    for armor_type in checkboxed_proficiencies:
        if armor_type in prof_list:
            prof_list.remove(armor_type)
            etree.SubElement(proficiency_element, checkboxed_proficiencies[armor_type]).text = "1"
        else:
            etree.SubElement(proficiency_element, checkboxed_proficiencies[armor_type]).text = "0"
    proficiencies_element = pc.find('proficiencies')
    proficiencies_element.text = ", ".join(prof_list)  # exclude ones with boxes

    # create a single string inventory list
    inventory_list = []
    for item in pc.xpath('inventorylist/*'):
        item_info = item.name
        if int(item.count) > 1:
            item_info += f" ({item.count})"
        if 'rarity' in item and 'Requires Attunement' in item.rarity:
            item_info += ' @'
        inventory_list.append(item_info)
    etree.SubElement(pc, 'inventory').text = "\n".join(inventory_list)
    etree.SubElement(pc, 'inventory_overflow').text = ""  # user should manually move text here for now

    # create a list of attacks based on the weapon list (and possibly cantrip, etc)
    attack_list = []
    for weapon in pc.xpath('weaponlist/*'):
        w = weapon_info(pc, weapon)
        attack_list.append(f"{w['name']}{w['usage']} {w['atk_bonus']} hit, {w['damage']}{w['notes']}")
    etree.SubElement(pc, 'attacks').text = "\n".join(attack_list)

    # populate three sets of "power tracking" entries
    tracking_list = [["", ""], ["", ""], ["", ""]] # default blanks
    for power in pc.xpath('powers/*'):
        tracking_list.append([generate_abbreviation(power.name), use_boxes(power, 'prepared', "◊")])
    tracking_list = sorted(tracking_list, key=lambda x: len(x[1]), reverse=True)
    track_elem = etree.SubElement(pc, 'tracking')
    for n in range(3):
        track_elem_n = etree.SubElement(track_elem, "b"+str(n+1))
        etree.SubElement(track_elem_n, 'name').text = tracking_list[n][0]
        etree.SubElement(track_elem_n, 'boxes').text = tracking_list[n][1]

    # blanks for unused form entries
    etree.SubElement(pc, 'shield').text = " "  # this is a lost box on the form ??
