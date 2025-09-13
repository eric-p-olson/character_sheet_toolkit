""" Patching function for Fantasy Grounds CoreRPG 8_1 format data (dnd 2024 rules).
      prepared powers - not currently updated in FG level-up wizard
      Ideally, Fantasy Grounds should take care of these by fixing their level-up wizard!
"""
import hashlib
from char_sheet_toolkit.mako_render import mako_render_str


def patch(pc):
    adjust_power_prepared(pc)


def hash10hex(string):
    return hashlib.md5(string.encode()).hexdigest()[:10]


# Tables detailing how some powers scale by level/ability/profbonus
#   Data is from the free-rules, expected to be in the SRD
#   Other data is unofficial, but it seems to work. You are fortunate if your power matches the hash
#      you should privately update this table if you have purchased non-SRD data and want it adjusted

power_prepared_adjustment = {
    'Rage': [
        {'class': 'Barbarian', 'class_table': [0, 2, 2, 3, 3, 3, 4, 4, 4, 4, 4, 4, 5, 5, 5, 5, 5, 6, 6, 6, 6]}],
    'Channel Divinity': [
        {'class': 'Cleric', 'class_table': [0, 0, 2, 2, 2, 2, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 4, 4, 4]},
        {'class': 'Paladin',
         'class_table': [0, 0, 2, 2, 2, 2, 2, 2, 2, 2, 2, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3]}],
    'Wild Shape': [{'class': 'Druid', 'class_table': [0, 0, 2, 2, 2, 2, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 4, 4, 4, 4]}],
    'Second Wind': [
        {'class': 'Fighter', 'class_table': [0, 2, 2, 2, 3, 3, 3, 3, 3, 3, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4]}],
    'Action Surge': [
        {'class': 'Fighter', 'class_table': [0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 2, 2, 2, 2]}],
    'ae6c51644b': [
        {'class': 'Fighter', 'class_table': [0, 0, 0, 4, 4, 4, 4, 5, 5, 5, 5, 5, 5, 5, 5, 6, 6, 6, 6, 6, 6]}],
    '00dddcbc9c': [
        {'class': 'Fighter', 'class_table': [0, 0, 0, 4, 4, 6, 6, 6, 6, 8, 8, 8, 8, 10, 10, 10, 10, 12, 12, 12, 12]},
        {'class': 'Rogue', 'class_table': [0, 0, 0, 4, 4, 6, 6, 6, 6, 8, 8, 8, 8, 10, 10, 10, 10, 12, 12, 12, 12]}],
    'Focus': [
        {'class': 'Monk', 'class_table': [0, 0, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20]}],
    'Favored Enemy': [
        {'class': 'Ranger', 'class_table': [0, 2, 2, 2, 2, 3, 3, 3, 3, 4, 4, 4, 4, 5, 5, 5, 5, 6, 6, 6, 6]}],
    'Sorcery Points': [{'class': 'Sorcerer',
                        'class_table': [0, 0, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20]}],
    'Hacker': [{'value': 'profbonus'}],
    'fcfa955d2f': [{'value': 'profbonus'}],
    '33ec5f50c2': [{'value': 'profbonus'}],
    '475617e4c1': [{'value': 'profbonus'}],
    '713beb5355': [{'value': 'profbonus'}],
    '6d60e1114b': [{'value': 'profbonus'}],
    '7094a0168b': [{'value': 'profbonus'}],
    'd2bb785fb8': [{'value': 'profbonus'}],
    'd55a1cb28a': [{'value': 'profbonus'}],
    'd42c2f5088': [{'value': 'profbonus'}],
    '6000a42afd': [{'value': 'profbonus'}],
    'a4d4f3d4ff': [{'value': 'profbonus'}],
    'e6424d6aa7': [{'value': 'profbonus'}],
    '8c7f5880b7': [{'value': 'profbonus'}],
    '17a0ebdf81': [{'value': 'profbonus'}],
    'f360621fc0': [{'value': 'profbonus'}],
    '7b0ba56aa6': [{'value': 'profbonus'}],
    '057a7cedf5': [{'value': 'profbonus'}],
    '271d233c12': [{'value': 'profbonus'}],
    '7398d4c606': [{'value': 'profbonus'}],
    '46f5e03e9b': [{'value': 'abilities.charisma.bonus'}],
    'db9572e3ab': [{'value': 'abilities.wisdom.bonus'}],
    'd736bf7a24': [{'value': 'abilities.wisdom.bonus'}],
    '90a7910f40': [{'value': 'abilities.wisdom.bonus'}],
    '480eeb022e': [{'value': 'abilities.wisdom.bonus'}],
    '55a575b73a': [{'value': 'abilities.wisdom.bonus'}],
    '821f43726f': [{'value': 'abilities.wisdom.bonus'}],
    '72d201d7ed': [{'value': 'abilities.wisdom.bonus'}],
    '8c7ba72554': [{'value': 'abilities.charisma.bonus'}],
    'c071a33705': [{'value': 'abilities.wisdom.bonus'}],
    '8e7ec537a7': [{'value': 'abilities.wisdom.bonus'}],
    '7b73417d67': [{'value': 'abilities.wisdom.bonus'}],
    'cce71342f4': [{'value': 'abilities.charisma.bonus'}],
    '59879dbda8': [{'value': 'abilities.charisma.bonus'}],
    '69c751621c': [{'value': 'abilities.charisma.bonus'}],
}


def adjust_power_prepared(pc):
    """adjust 'prepared' value for pc's power_name power
        pc - dictionary class populated from xml with hierarchy flattened with underscores
             and lists turned into lists
    """
    powers = pc.find('./powers')
    if powers is not None:
        for power_data in powers:
            if ('name' in power_data
                    and 'prepared' in power_data
                    and 'version' in power_data
                    and power_data.version == '2024'):
                prepared = 0
                if power_data.name in power_prepared_adjustment:
                    for adj in power_prepared_adjustment[power_data.name]:
                        prepared += adjust_prepared_value(pc, power_data.name, adj)
                elif hash10hex(power_data.name) in power_prepared_adjustment:
                    for adj in power_prepared_adjustment[hash10hex(power_data.name)]:
                        prepared += adjust_prepared_value(pc, power_data.name, adj)
                else:
                    prepared = power_data.prepared
                if power_data.prepared != prepared:
                    print(
                        f"Info -   patching power: '{power_data.name}': prepared={power_data.prepared} => {prepared}")
                    prepared_data = power_data.find('prepared')
                    prepared_data.text = str(prepared)


def adjust_prepared_value(pc, power_name, adj):
    if 'value' in adj:
        adj_value = mako_render_str(f"${{{adj['value']}}}", pc)
        if adj_value is not None and adj_value != "":
            return max(1, int(adj_value))
        else:
            print(f"Error - PC value POWER {power_name}: {adj['value']} not in pc ({adj_value})")
    elif 'class' in adj:
        class_data = pc.find(f"classes/*[name='{adj['class']}']")  # find class with name=adj_class
        if class_data is not None:
            return adj['class_table'][int(class_data.level)]
    return 0

