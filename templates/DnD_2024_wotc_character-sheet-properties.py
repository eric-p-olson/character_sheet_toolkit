# additional properties needed for: DnD_2024_Character_Sheet.pdf
#
import pprint

from lxml import etree
from char_sheet_toolkit.CoreRPG.CoreRPG_dnd_2024_utils import weapon_info, use_boxes, generate_abbreviation, \
    power_use_boxes, \
    cantrip_info


def properties(pc):
    print(f"Info -   deriving properties for DnD_2024_Character_Sheet.pdf")

    size_element = pc.find('size')
    size_element.text = pc.size[0]

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

    # split off weapon & tool prof lists
    prof_weapon_list = []
    prof_tool_list = []
    for prof in prof_list:
        if prof.startswith('Weapon: '):
            prof_weapon_list.append(prof.replace('Weapon: ', ''))
        if prof.startswith('Tool:'):
            prof_tool_list.append(prof.replace('Tool: ', ''))
    etree.SubElement(pc, "proficiencies_weapons").text = ", ".join(prof_weapon_list)
    etree.SubElement(pc, "proficiencies_tools").text = ", ".join(prof_tool_list)

    # create a single string inventory list (pull out attune)
    inventory_list = []
    attune_list = [' ', ' ', ' ']
    for item in pc.xpath('inventorylist/*'):
        item_info = item.name
        if int(item.count) > 1:
            item_info += f" ({item.count})"
        if 'rarity' in item and 'Requires Attunement' in item.rarity:
            if int(item.attune):
                attune_list.append(item_info)
                continue
            item_info += ' @'
        inventory_list.append(item_info)
    attune_list.sort(reverse=True)
    etree.SubElement(pc, 'inventory').text = "\n".join(inventory_list)
    etree.SubElement(pc, 'inventory_attuned_1').text = attune_list[0]
    etree.SubElement(pc, 'inventory_attuned_2').text = attune_list[1]
    etree.SubElement(pc, 'inventory_attuned_3').text = attune_list[2]
    etree.SubElement(pc, 'att1').text = '0'
    etree.SubElement(pc, 'att2').text = '0'
    etree.SubElement(pc, 'att3').text = '0'

    # spellcasting box - find class's 'Spells' stat
    spellcasting = {}
    for c in pc.xpath('./classes/*'):
        for power_grp in pc.xpath('powergroup/*'):
            if power_grp.name == f"Spells ({c.name})":
                stat_name = power_grp.stat
                if stat_name not in spellcasting:
                    spellcasting[stat_name] = {}
                    spellcasting[stat_name]['class'] = power_grp.name  # just info
                    modifier = int(pc.abilities.find(stat_name).bonus)
                    spellcasting[stat_name]['stat'] = stat_name
                    spellcasting[stat_name]['modifier'] = f"{modifier:+}"
                    spellcasting[stat_name]['savedc'] = f"{(8 + modifier + int(pc.profbonus))}"
                    spellcasting[stat_name]['atk_bonus'] = f"{(modifier + int(pc.profbonus)):+}"
    for fld in ['stat', 'modifier', 'savedc', 'atk_bonus']:
        fld_entry = '/'.join( [subdict[fld] for subdict in spellcasting.values()])
        etree.SubElement(pc, f'spellcasting_{fld}').text = fld_entry

    # create a list of attacks based on the weapon list (and possibly cantrip, etc)
    attacks_list = [{'name': " ", 'atk_bonus': " ", 'damage': " ", 'notes': " "}] * 6
    for weapon in pc.xpath('weaponlist/*'):
        w = weapon_info(pc, weapon)
        attacks_list.append({'name': f"{w['name']}{w['usage']}",
                             'atk_bonus': w['atk_bonus'],
                             'damage': w['damage'],
                             'notes': w['notes']})
    for power in pc.xpath('powers/*'):  # cantrips
        s = cantrip_info(pc, power)
        if s is not None:
            attacks_list.append({'name': f"{s['name']}{s['usage']}",
                                 'atk_bonus': s['atk_bonus'],
                                 'damage': s['damage'],
                                 'notes': s['notes']})
    attacks_list.sort(key=lambda x: x["atk_bonus"], reverse=True)
    #pprint.pp(attacks_list)
    attack_element = etree.SubElement(pc, 'attack')
    for spell_index in range(0, 6):
        #print(f"{weapon_index}: {attacks_list[weapon_index]}")
        i = etree.SubElement(attack_element, f"id_{(spell_index + 1):02}")
        etree.SubElement(i, 'name').text = attacks_list[spell_index]['name']
        etree.SubElement(i, 'atk_bonus').text = attacks_list[spell_index]['atk_bonus'].replace('_', ' ')
        etree.SubElement(i, 'damage').text = attacks_list[spell_index]['damage']
        etree.SubElement(i, 'notes').text = attacks_list[spell_index]['notes']

    # gather feats, species traits, class features (with tracking)
    powers = {'feats': [], 'species_traits': [], 'class_features': [], 'other_features': []}
    for trait in pc.xpath('traitlist/*'):
        powers['species_traits'].append(f"{trait.name}")
    for feat in pc.xpath('featlist/*'):
        powers['feats'].append(f"{feat.name}")
    for power in pc.xpath('powers/*'):
        if power.group.startswith('Class '):
            powers['class_features'].append(f"{power.name}")
    for feature in pc.xpath('featurelist/*'):
        if feature.name not in powers['class_features']:
            powers['other_features'].append(f"{feature.name}")
    for power_type in powers:
        power_list = [p + ' ' + power_use_boxes(pc, p, "♢") for p in powers[power_type]]
        power_entry = '\n'.join(power_list) if len(power_list) else " "
        etree.SubElement(pc, power_type).text = power_entry

    # populate spell/pact slot numbers
    ss_num = {1: [], 2: [], 3: [], 4: [], 5: [], 6: [], 7: [], 8: [], 9: []}
    for level in range(1, 10):
        n = int(pc.find(f"powermeta/pactmagicslots{level}/max").text)
        if n:
            ss_num[level].append(str(n))
        n = int(pc.find(f"powermeta/spellslots{level}/max").text)
        if n:
            ss_num[level].append(str(n))
        slots = '/'.join(ss_num[level]) if len(ss_num[level]) else " "
        etree.SubElement(pc, f'spellslots_{level}').text = slots

    # elaborate out spells
    spell_table = []
    for spell in pc.xpath("powers/*"):  # [group='Spells']
        if 'Spells' in spell.group:
            spell_table.append({'level': spell.level, 'name': spell.name,
                                'casting_time': spell.castingtime[:3], 'range': spell.range,
                                'C': f"{int('Concentration' in spell.duration)}",
                                'R': spell.ritual,
                                'M': f"{int('M' in spell.components)}",
                                'notes': " "})
    spell_table += [{'level': " ", 'name': " ", 'casting_time': " ", 'range': " ",
                     'C': '0', 'R': '0', 'M': '0', 'notes': " "}] * 30
    spell_element = etree.SubElement(pc, 'spell')
    for spell_index in range(0, 30):
        # print(f"{weapon_index}: {attacks_list[weapon_index]}")
        i = etree.SubElement(spell_element, f"r{(spell_index + 1):02}")
        etree.SubElement(i, 'name').text = spell_table[spell_index]['name']
        etree.SubElement(i, 'level').text = spell_table[spell_index]['level']
        etree.SubElement(i, 'castingtime').text = spell_table[spell_index]['casting_time']
        etree.SubElement(i, 'range').text = spell_table[spell_index]['range'].replace(' feet', "'")
        etree.SubElement(i, 'c').text = spell_table[spell_index]['C']
        etree.SubElement(i, 'r').text = spell_table[spell_index]['R']
        etree.SubElement(i, 'm').text = spell_table[spell_index]['M']
        etree.SubElement(i, 'notes').text = spell_table[spell_index]['notes']

    # pull backstory from adventurelist
    etree.SubElement(pc, 'backstory').text = " "
    backstory_element = pc.find(f"adventurelist/*[name='backstory']")
    if backstory_element is not None:
        etree.SubElement(pc, 'backstory').text = backstory_element.tostring('text')

    # blanks for known properties that can be missing
    if 'appearance' not in pc:
        etree.SubElement(pc, 'appearance').text = " "
    if 'alignment' not in pc:
        etree.SubElement(pc, 'alignment').text = " "
    if 'personalitytraits' not in pc:
        etree.SubElement(pc, 'personalitytraits').text = " "

    # blanks for unused form entries
    etree.SubElement(pc, 'heroic_inspiration').text = "0"
    etree.SubElement(pc, 'dss1').text = "0"  # death save success
    etree.SubElement(pc, 'dss2').text = "0"
    etree.SubElement(pc, 'dss3').text = "0"
    etree.SubElement(pc, 'dsf1').text = "0"  # death save failure
    etree.SubElement(pc, 'dsf2').text = "0"
    etree.SubElement(pc, 'dsf3').text = "0"
    for l in range(1, 10):
        for i in range(1, 5):
            etree.SubElement(pc, f'ss{l}_{i}').text = "0"  # spell slot checks
