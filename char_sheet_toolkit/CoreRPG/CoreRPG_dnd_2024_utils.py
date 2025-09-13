""" Utility functions for Fantasy Grounds CoreRPG format data
      Used for deriving data for dnd 5e.24 rules.
        weapon attack data
        prepared powers (for extra counters)
        spellslot table
"""
import re
from lxml import etree


# def weapon_info(pc, weapon, template):
#     stats = weapon_stats(pc, weapon)
#     info = mako_render_str(template, pc, stats)
#     return info


def weapon_info(pc, weapon):
    """compute stats for a weaponlist weapon on a pc"""
    # FIXME - missing fighting feats: two-weapon, archery, dueling, thrown

    # 'handling': 0-prime, 1-two,2-offhand
    # 'type': 0-melee, 1-range, 2-thrown
    # 'attackstat': defaults to 'base'
    # damage.stat: 'base' with damage.statmult
    handling = ['', ' (two-handed)', ' (off-hand)']
    weapon_type = ['', '', ' (thrown)']

    stats = {'name': weapon.name,
             'usage': handling[int(weapon.handling)] + weapon_type[int(weapon.type)],
             'atk_bonus': get_weapon_atk_bonus(pc, weapon),
             'damage': get_attack_dmg(pc, weapon),
             'notes': get_weapon_notes(pc, weapon)
             }
    return stats


def cantrip_info(pc, power):
    """compute stats for a spell power on a pc"""
    # FIXME - missing feats that might modify?
    atk_dmg = power.find("actions/*[type='damage']")
    if atk_dmg is None:
        return None
    dmg = get_attack_dmg(pc, atk_dmg)
    atk_hit = power.find("actions/*[type='cast']")
    if atk_hit is None:  # automatic
        atk_bonus = "auto"
    elif 'atktype' in atk_hit:
        atk_bonus = get_ranged_spell_atk_bonus(pc, spell=power, cast=atk_hit)
    elif 'savemagic' in atk_hit:
        atk_bonus = get_spell_dc(pc, spell=power, cast=atk_hit)
    else:
        atk_bonus = "?"
    # if not power.group.startswith('Spells '):
    if 'level' in power and power.level != '0':
        return None
    stats = {'name': power.name,
             'usage': "",
             'atk_bonus': atk_bonus,
             'damage': dmg,
             'notes': power.range if 'range' in power else ""
             }
    return stats


def get_stat(pc, weapon, item_stat):
    """attack or damage stat based on weapon type or damage type"""
    stat = item_stat
    if stat == 'base':
        if 'finesse' in str(weapon.properties).lower():
            if int(pc.abilities.strength.score) > int(pc.abilities.dexterity.score):
                stat = 'strength'
            else:
                stat = 'dexterity'
        elif weapon.type == '1':  # ranged
            stat = 'dexterity'
        else:
            stat = 'strength'
    return stat


def get_stat_bonus(pc, stat_name):
    """get stat 'bonus' (or level...) """
    if stat_name is None:
        return 0
    stat_class = pc.find(f"classes/*[name='{stat_name[:1].upper() + stat_name[1:]}']")
    if stat_name == 'prf':
        stat_bonus = int(pc.profbonus)
    elif stat_name in pc.abilities:
        stat_bonus = int(pc.abilities.find(stat_name).bonus)
    elif stat_name:
        stat_bonus = int(stat_class.level)
    else:
        stat_bonus = 0
        print(f"debug - stat bonus for {stat_name} unknown")
    return stat_bonus


def get_weapon_atk_bonus(pc, weapon):
    attack_stat = get_stat(pc, weapon, weapon.get_text('attackstat'))
    atk_bonus = int(weapon.attackbonus)
    atk_bonus += int(pc.profbonus) * int(weapon.prof)
    atk_bonus += get_stat_bonus(pc, attack_stat)
    return f"{atk_bonus:+}"


def get_attack_dmg(pc, weapon):
    damages = []
    for dmg_type in weapon.xpath('damagelist/*'):
        damages.append(compute_attack_damage(pc, weapon, dmg_type))
    return "/".join(damages)


def compute_attack_damage(pc, attack, dmg_element):
    """compute each weapon damage by pc"""
    dmg_stat = get_stat(pc, attack, dmg_element.get_text('stat'))

    dmg_dice = dmg_element.dice
    if dmg_dice is None:
        dmg_dice = ""
    if 'properties' in attack:
        versatile_dmg = re.search(r'\bVersatile\s+\((\d+d\d+)\)', attack.properties)
        if attack.handling == '1' and versatile_dmg:
            dmg_dice = versatile_dmg.group(1)

    dmg_type = dmg_element.type if 'type' in dmg_element else ''

    dmg_bonus = int(dmg_element.bonus)
    if dmg_stat is None:
        pass
    elif 'handling' in attack and attack.handling == '2':  # off-hand: only neg
        if int(pc.abilities.find(dmg_stat).bonus) < 0:
            dmg_bonus += get_stat_bonus(pc, dmg_stat)  # int(pc.abilities.find(dmg_stat).bonus)
    else:
        statmult = int(dmg_element.statmult) if 'statmult' in dmg_element else 1
        dmg_bonus += statmult * get_stat_bonus(pc, dmg_stat)
    dmg_bonus = f"{dmg_bonus:+}" if (dmg_type != "" and dmg_bonus != 0) else ""
    return f"{dmg_dice}{dmg_bonus} {dmg_type}"


def get_weapon_notes(pc, weapon):
    """add range and item properties"""
    notes = ""
    if 'properties' in weapon:
        range_info = re.search(r'\bRange\s+(\d+)/(\d+)\b', weapon.properties)
        if range_info and int(weapon.type) > 0:
            notes += f" ({range_info.group(0)})"
    notes += get_weapon_item_properties(pc, weapon)
    return notes


def get_weapon_item_properties(pc, weapon):
    """look up item referenced by attack and grab anything interesting (like mastery)"""
    item_properties = ""
    inventory_record = weapon.find('shortcut/recordname')
    if inventory_record is not None and inventory_record.text.startswith('.'):
        item = pc.find(inventory_record.text.lstrip('.').replace('.', '/'))
        if item is not None:
            if 'mastery' in item:
                item_properties = f" [{item.mastery}]"
    return item_properties


def get_ranged_spell_atk_bonus(pc, spell, cast):
    group_element = pc.find(f"powergroup/*[name='{spell.group}']")
    if group_element is not None:
        if 'stat' in group_element:
            save_dc_stat = group_element.stat
    stat_modifier = int(pc.abilities.find(save_dc_stat).bonus)
    atk_bonus = stat_modifier + int(pc.profbonus)
    return f"{atk_bonus:+}"


def get_spell_dc(pc, spell, cast):
    save_dc_stat = None
    if 'savedcstat' in cast:
        save_dc_stat = cast.savedcstat
    else:
        group_element = pc.find(f"powergroup/*[name='{spell.group}']")
        if group_element is not None:
            if 'stat' in group_element:
                save_dc_stat = group_element.stat
    stat_modifier = int(pc.abilities.find(save_dc_stat).bonus)
    save_dc = 8 + stat_modifier + int(pc.profbonus)
    return f"{save_dc} {cast.savetype[:3]}"


def slot_row(pc, slot_type, box='&#9671;'):
    """generate a table row with 9 columns: each with one 'box' per slot_type"""
    row = ""
    for level in range(1, 10):
        level_slots = int(pc.find(slot_type.replace('{level}', str(level))).text)
        row += '<td>' + box * level_slots + '</td>'
    return f"<tr>{row}</tr>"


def use_boxes(element, field, box='&#9671;'):
    if field in element:
        return box * int(element.find(field).text)
    return ""


def power_use_boxes(pc, power_name, box='&#9671;'):
    power_use = pc.find(f'powers/*[name="{power_name}"]')
    if power_use is not None:
        uses = use_boxes(power_use, 'prepared', box)
        return uses
    return ""


def generate_abbreviation(phrase, length=9, up=True):
    if not isinstance(phrase, str):
        return "?"
    phrase = phrase.replace("'", "")
    while len(phrase) > length + int('I' in phrase.upper()):
        words = re.split(r'\s+', phrase.strip())
        repl_orig = max(words, key=len)
        if repl_orig[-2].upper() in ['A', 'E', 'I', 'O', 'U']:
            repl_new = repl_orig[:-2] + repl_orig[-1]
        else:
            repl_new = repl_orig[:-1]
        if len(words) > 3:
            repl_orig = words[1]
            repl_new = ""
        for ex_wrd in [' of ', ' the ']:
            if ex_wrd in phrase:
                repl_orig = ex_wrd
                repl_new = " "
        phrase = phrase.replace(repl_orig, repl_new)
        phrase = phrase.replace('  ', ' ')
    if up:
        phrase = phrase.upper()
    return phrase
