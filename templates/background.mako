## background.mako
##    TODO: check name vs power-prepared and make little usage diamonds &loz;
##
# ${name}'s Background
${'###'} Description
${race}

% for story in PC.xpath('adventurelist/*'):
${'###'} ${story.name}
${story.tostring('text', method='markdown')}
% endfor
