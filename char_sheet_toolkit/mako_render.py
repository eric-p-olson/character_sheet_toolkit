import mako
from mako.template import Template
from lxml import etree
from markdownify import markdownify


def markdown(html_string):
    """filter"""
    return markdownify(html_string)


def signed(number):
    """filter: return number with forced +/-"""
    return f"{int(number):+}"


def markup(html_string):
    # html_string = html_string.replace(' & ', ' &amp; ')  # TODO need a better way to sanitize or report errors
    print(f"<root>{html_string}</root>")
    text_tree = etree.fromstring(f"<root>{html_string}</root>")
    return xml_to_markup(text_tree)


def xml_to_markup(element):
    """converts xml to markup - replaces tags with markup language, some operation are more fancy"""

    def fix_table(s, e):
        table_rows = s.split('\n')
        columns = table_rows[0].count('|') - 1
        index = next((i for i, s in enumerate(table_rows) if "*" not in s), -1)
        table_rows.insert(index, "|:-" * columns + "|")
        s = "\n\n" + "\n".join(table_rows)
        return s

    markup_map = {
        'p': lambda s, e: s,
        '/p': lambda s, e: s + "\n\n",
        'i': lambda s, e: s + '*',  # italics
        '/i': lambda s, e: s + '*',
        'b': lambda s, e: s + '**',
        '/b': lambda s, e: s + '**',
        'h': lambda s, e: s + '**',
        '/h': lambda s, e: s + ':** ',
        'table': lambda s, e: s,
        '/table': fix_table,
        'tr': lambda s, e: s,
        '/tr': lambda s, e: s + '|\n',
        'td': lambda s, e: s + '| ',
        '/td': lambda s, e: s + '|' * (int(e.get('colspan', 1)) - 1),
        'list': lambda s, e: s,
        '/list': lambda s, e: s,
        'linklist': lambda s, e: s,
        '/linklist': lambda s, e: s,
        'link': lambda s, e: s,
        '/link': lambda s, e: s,
        'li': lambda s, e: s + "* ",
        '/li': lambda s, e: s + "\n",
        'default': lambda s, e: s + f"<{e.tag}>",
        '/default': lambda s, e: s + f"</{e.tag}>"
    }
    result = ""
    if element.text:
        result += f"{element.text}"
    for child in element:
        child_result = ""
        child_result = markup_map.get(child.tag, markup_map['default'])(child_result, child)
        child_result += xml_to_markup(child)
        child_result = markup_map.get('/' + child.tag, markup_map['/default'])(child_result, child)
        if child.tail:
            child_result += (' ' * (child_result[-1] == '*')) + child.tail
        result += child_result
    return result


def mako_render(template_filename, pc_data, other_data=None):
    if other_data is None:
        other_data = {}
    template = Template(filename=template_filename)
    rendered_output = template.render(**pc_data.get_kwargs(), **other_data, PC=pc_data,
                                      markdown=markdown, signed=signed)
    return rendered_output


def mako_render_str(template_str, pc_data, other_data=None, debug_info=""):
    if other_data is None:
        other_data = {}
    rendered_output = None
    try:
        template = Template(template_str)
        rendered_output = template.render(**pc_data.get_kwargs(), **other_data, PC=pc_data,
                                          markdown=markdown, signed=signed)
    except mako.exceptions.SyntaxException:
        print(f"Error - mako syntax error in string: {template_str}{debug_info}")
    except NameError:
        print(f"Error - undefined variable in mako string: {template_str}{debug_info}")
    except TypeError as e:
        print(
            f"Error - unsupported format in mako string: '{template_str}' {debug_info}"
            f"({e}) [{type(template_str)}={str(template_str)}]")
    except AttributeError as e:
        print(
            f"Error - error resolving attribute in mako string: '{template_str}' {debug_info}"
            f"({e})")
    except ValueError as e:
        print(
            f"Error - error resolving value in mako string: '{template_str}' {debug_info}"
            f"({e})")
    return rendered_output
