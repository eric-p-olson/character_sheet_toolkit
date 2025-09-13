# ${name}'s Spells

## spell slot tables
<% from char_sheet_toolkit.CoreRPG.CoreRPG_dnd_2024_utils import slot_row %>
{{wide
% if PC.find('powermeta/pactmagicslots1/max') is not None and int(powermeta.pactmagicslots1.max) > 0:
<div align="center"><h3>Pact Magic Slots</h3></div>
<table  style="margin: auto; text-align: center;font-size: 20px;">
  <tr><th>1st</th><th>2nd</th><th>3rd</th><th>4th</th><th>5th</th><th>6th</th><th>7th</th><th>8th</th><th>9th</th></tr>
    ${slot_row(PC,'powermeta/pactmagicslots{level}/max')}
</table>
% endif
% if PC.find('powermeta/spellslots1/max') is not None and int(powermeta.spellslots1.max) > 0:
<div align="center"><h3>Spell Slots</h3></div>
<table  style="margin: auto; text-align: center;font-size: 20px;">
  <tr><th>1st</th><th>2nd</th><th>3rd</th><th>4th</th><th>5th</th><th>6th</th><th>7th</th><th>8th</th><th>9th</th></tr>
    ${slot_row(PC,'powermeta/spellslots{level}/max')}
</table>
% endif
}}
<% # populate spell table
  spell_list = []
  spell_table = {0:{'label':'Cantrips','spells':[]},
                 1:{'label':'1st Level','spells':[]},
                 2:{'label':'2nd Level','spells':[]},
                 3:{'label':'3rd Level','spells':[]},
                 4:{'label':'4th Level','spells':[]},
                 5:{'label':'5th Level','spells':[]},
                 6:{'label':'6th Level','spells':[]},
                 7:{'label':'7th Level','spells':[]},
                 8:{'label':'8th Level','spells':[]},
                 9:{'label':'9th Level','spells':[]}}
  for spell in PC.xpath("powers/*"):  # [group='Spells']
       if 'Spells' in spell.group:
           spell_table[int(spell.level)]['spells'].append(spell.name)
           spell_list.append(spell.name)
%>

## spell list
% for level in spell_table:
%   if spell_table[level]['spells']:
${'#####'} ${spell_table[level]['label']}
%     for spell_name in sorted(spell_table[level]['spells']):
- ${spell_name}
%     endfor
%   endif
% endfor

## spell descriptions (alphabetical)
% for spell_name in sorted(spell_list):
<%  spell = PC.find(f"powers/*[name='{spell_name}']")  %>
<%  box = '&#x2610;' if int(spell.level) > 0 else '' %>
{{monster,frame
${'####'} ${box} ${spell.name}
*Level ${spell.level} ${spell.school} - ${spell.version} ${spell.group}*

**Casting Time:** :: ${spell.castingtime}
**Range:**        :: ${spell.range}
**Components:**   :: ${spell.components}
**Duration:**     :: ${spell.duration}

${spell.description.tostring(method='markdown')}
}}
% endfor
