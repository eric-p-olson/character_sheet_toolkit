## abilities.mako
##  Loop thorugh traits, feats, and powers, dumping all abilities
##
##  TODO: check name vs power-prepared and make little usage diamonds &loz;
##
<% from char_sheet_toolkit.CoreRPG.CoreRPG_dnd_2024_utils import use_boxes %>
<% done = {} %>
# ${name}

${'###'}  ${species} Traits
% for trait in PC.xpath('traitlist/*'):
<%   done[trait.text] = trait.name %>\
<%   track = use_boxes(trait,'prepared','&loz;')  %>\
${   '####'} ${track} ${trait.name}
${   trait.tostring('text',method='markdown')}
% endfor

${'###'} Feats
% for feat in PC.xpath('featlist/*'):
<%   done[feat.text] = feat.name %>\
<%   track = use_boxes(feat,'prepared','&loz;')  %>\
${   '####'} ${track} ${feat.name} (${feat.category})
${   feat.tostring('text',method='markdown')}
% endfor

## class features
% for pc_class in PC.xpath('classes/*'):
${   '###'} ${pc_class.name} class abilities
%    for class_ability in PC.xpath('powers/*'):
%      if class_ability.group == f"Class ({pc_class.name})":
<%       description = class_ability.tostring('description',method='markdown') %>\
<%       done[description] = class_ability.name %>\
<%       track = use_boxes(class_ability,'prepared','&loz;') %>\
${       '####'} ${track} ${class_ability.name}
${       description}
%      endif
%    endfor
%    for class_ability in PC.xpath('powers/*'):
%      if pc_class.name in class_ability.group and 'Spells' not in class_ability.group:
<%       description = class_ability.tostring('description',method='markdown') %>\
%        if description not in done:
<%          done[description] = class_ability.name %>
<%          track = use_boxes(class_ability,'prepared','&loz;') %>\
${          '####'} ${track} ${class_ability.name} - ${class_ability.group}
${          description}
%        endif
%     endif
%   endfor
% endfor

${'###'} Additional Features
% for feature in PC.xpath('featurelist/*'):
<%  text = feature.tostring('text',method='markdown') %>\
%   if text not in done:
${    '####'} ${feature.name}
${    text}
%   endif
% endfor