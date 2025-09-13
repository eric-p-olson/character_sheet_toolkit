# ${name}'s Inventory
% for item in PC.xpath('inventorylist/*'):
<%
    if int(item.count) > 1:
        count_str = f" ({item.count})"
    else:
        count_str = ""

    subtype = 'subtype' if 'subtype' in item else 'type'
    info = {subtype :'%s', 'rarity':'%s', 'cost':'%s', 'weight':'%s lbs'}
    info_str = "; ".join([info[key] % item.find(key).text for key in info if key in item])

    details = {'ac':'AC: %s', 'damage':'Damage: %s', 'properties':'Properties: %s', 'mastery':'Mastery: %s'}
    detail_str = "; ".join([details[key] % item.find(key).text for key in details if key in item])

%>\
${'####'} ${item.name}${count_str}
*${info_str}*
<br/>${detail_str}

%   if 'description' in item:
${item.description.tostring(method='markdown')}
%   endif
% endfor
