""" Patching function for Fantasy Grounds CoreRPG 8_1 format data (dnd 2024 rules).
        Personal non-SRD data, not for public release
"""
import hashlib


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
#  power-prepared table number by property value or by level: [0,1,2,3,4,5,6,7,8,9,0,1,2,3,4,5,6,7,8,9,0]
power_prepared_adjustment_orig = {
    'Rage': [{'class': 'Barbarian', 'class_table': [0, 2, 2, 3, 3, 3, 4, 4, 4, 4, 4, 4, 5, 5, 5, 5, 5, 6, 6, 6, 6]}],
    'Channel Divinity': [
        {'class': 'Cleric',
         'class_table': [0, 0, 2, 2, 2, 2, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 4, 4, 4]},
        {'class': 'Paladin',
         'class_table': [0, 0, 2, 2, 2, 2, 2, 2, 2, 2, 2, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3]}],
    'Wild Shape': [
        {'class': 'Druid', 'class_table': [0, 0, 2, 2, 2, 2, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 3, 4, 4, 4, 4]}],
    'Second Wind': [
        {'class': 'Fighter', 'class_table': [0, 2, 2, 2, 3, 3, 3, 3, 3, 3, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4]}],
    'Action Surge': [
        {'class': 'Fighter', 'class_table': [0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 2, 2, 2, 2]}],
    'Superiority Dice': [
        {'class': 'Fighter', 'class_table': [0, 0, 0, 4, 4, 4, 4, 5, 5, 5, 5, 5, 5, 5, 5, 6, 6, 6, 6, 6, 6]}],
    'Psionic Energy': [
        {'class': 'Fighter', 'class_table': [0, 0, 0, 4, 4, 6, 6, 6, 6, 8, 8, 8, 8, 10, 10, 10, 10, 12, 12, 12, 12]},
        {'class': 'Rogue', 'class_table': [0, 0, 0, 4, 4, 6, 6, 6, 6, 8, 8, 8, 8, 10, 10, 10, 10, 12, 12, 12, 12]}],
    'Focus': [
        {'class': 'Monk', 'class_table': [0, 0, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20]}],
    'Favored Enemy': [
        {'class': 'Ranger', 'class_table': [0, 2, 2, 2, 2, 3, 3, 3, 3, 4, 4, 4, 4, 5, 5, 5, 5, 6, 6, 6, 6]}],
    'Sorcery Points': [{'class': 'Sorcerer',
                        'class_table': [0, 0, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20]}],
    "Black Dragonborn Breath Weapon": [{'value': 'profbonus'}],
    "Blue Dragonborn Breath Weapon": [{'value': 'profbonus'}],
    "Brass Dragonborn Breath Weapon": [{'value': 'profbonus'}],
    "Bronze Dragonborn Breath Weapon": [{'value': 'profbonus'}],
    "Copper Dragonborn Breath Weapon": [{'value': 'profbonus'}],
    "Gold Dragonborn Breath Weapon": [{'value': 'profbonus'}],
    "Green Dragonborn Breath Weapon": [{'value': 'profbonus'}],
    "Red Dragonborn Breath Weapon": [{'value': 'profbonus'}],
    "Silver Dragonborn Breath Weapon": [{'value': 'profbonus'}],
    "White Dragonborn Breath Weapon": [{'value': 'profbonus'}],
    'Stonecunning': [{'value': 'profbonus'}],
    "Cloud's Jaunt": [{'value': 'profbonus'}],
    "Fire's Burn": [{'value': 'profbonus'}],
    "Frost's Chill": [{'value': 'profbonus'}],
    "Hill's Tumble": [{'value': 'profbonus'}],
    "Stone's Endurance": [{'value': 'profbonus'}],
    "Storm's Thunder": [{'value': 'profbonus'}],
    "Adrenaline Rush": [{'value': 'profbonus'}],
    'Lucky': [{'value': 'profbonus'}],
    'Bardic Inspiration': [{'value': 'abilities.charisma.bonus'}],
    'Warding Flare': [{'value': 'abilities.wisdom.bonus'}],
    'Corona of Light': [{'value': 'abilities.wisdom.bonus'}],
    'War Priest': [{'value': 'abilities.wisdom.bonus'}],
    'Moonlight Step': [{'value': 'abilities.wisdom.bonus'}],
    'Star Map': [{'value': 'abilities.wisdom.bonus'}],
    'Cosmic Omen': [{'value': 'abilities.wisdom.bonus'}],
    'Wholeness of Body': [{'value': 'abilities.wisdom.bonus'}],
    "Glorious Defense": [{'value': 'abilities.charisma.bonus'}],  #?
    "Nature's Veil": [{'value': 'abilities.wisdom.bonus'}],  #?
    'Misty Wanderer': [{'value': 'abilities.wisdom.bonus'}],  #?
    'Dread Ambusher': [{'value': 'abilities.wisdom.bonus'}],  #?
    "Restore Balance": [{'value': 'abilities.charisma.bonus'}],
    "Steps of the Fey": [{'value': 'abilities.charisma.bonus'}],  #?
    "Dark One's Own Luck": [{'value': 'abilities.charisma.bonus'}],
}


# utility
def dump_array(power_prepared_adjustment_orig):
    hashed_array = {}
    for power in power_prepared_adjustment_orig:
        hashed_array[hash10hex(power)] = power_prepared_adjustment_orig[power]
        print(f"    '{hash10hex(power)}': {power_prepared_adjustment_orig[power]}, ")