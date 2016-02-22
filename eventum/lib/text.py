import re


def truncate_html(text, truncate_len, truncate_text):
    """Truncates HTML to a certain number of words (not counting tags and
    comments). Closes opened tags if they were correctly closed in the given
    HTML. If text is truncated, truncate_text will be appended to the result.

    Newlines in the HTML are preserved.

    Modified from django.utils.text
    https://github.com/django/django/blob/master/django/utils/text.py

    :param str text: The text to truncate.
    :param str truncate_len: The number of words to shorten the HTML to
    :param int truncate_len: Text like '...' to append to the end of tuncated
        text.

    :returns: The truncated HTML
    :rtype: str
    """
    re_words = re.compile(r'<.*?>|((?:\w[-\w]*|&.*?;)+)', re.U | re.S)
    re_tag = re.compile(r'<(/)?([^ ]+?)(?:(\s*/)| .*?)?>', re.S)

    length = truncate_len

    if length <= 0:
        return ''

    html4_singlets = (
        'br', 'col', 'link', 'base', 'img',
        'param', 'area', 'hr', 'input'
    )

    # Count non-HTML chars/words and keep note of open tags
    pos = 0
    end_text_pos = 0
    current_len = 0
    open_tags = []

    while current_len <= length:
        m = re_words.search(text, pos)
        if not m:
            # Checked through whole string
            break
        pos = m.end(0)
        if m.group(1):
            # It's an actual non-HTML word or char
            current_len += 1
            if current_len == truncate_len:
                end_text_pos = pos
            continue
        # Check for tag
        tag = re_tag.match(m.group(0))
        if not tag or current_len >= truncate_len:
            # Don't worry about non tags or tags after our truncate point
            continue
        closing_tag, tagname, self_closing = tag.groups()
        # Element names are always case-insensitive
        tagname = tagname.lower()
        if self_closing or tagname in html4_singlets:
            pass
        elif closing_tag:
            # Check for match in open tags list
            try:
                i = open_tags.index(tagname)
            except ValueError:
                pass
            else:
                # SGML: An end tag closes, back to the matching start tag,
                # all unclosed intervening start tags with omitted end tags
                open_tags = open_tags[i + 1:]
        else:
            # Add it to the start of the open tags list
            open_tags.insert(0, tagname)

    if current_len <= length:
        return text
    out = text[:end_text_pos]
    if truncate_text:
        out += truncate_text
    # Close any tags still open
    for tag in open_tags:
        out += '</{}>'.format(tag)
    # Return string
    return out


def clean_markdown(markdown):
    """Formats markdown text for easier plaintext viewing.  Performs the
    following substitutions:

    - Removes bad or empty links
    - Removes images
    - Formats hyperlinks from ``[link](http://adicu.com)`` to
    ``link (http://adicu.com)``.

    :param str markdown: The markdown text to format.

    :returns: the formatted text:
    :rtype: str
    """
    substitutions = [
        # Remove images: '\t   ![hello](anything)' -> ''
        (r'\s*\!\[[^\]]*\]\([^\)]*\)', r''),
        # Remove empty links: '\t   [\t   ](anything)' -> ''
        (r'\s*\[\s*\]\([^\)]*\)', r''),
        # Links: '[hello](http://google.com)' -> 'hello (http://google.com)'
        (r'\[(?P<text>.*)\]\((?P<link>http[s]?://[^\)]*)\)', r'\1 (\2)'),
        # Bad links: '[hello](garbage)' -> 'hello'
        (r'\[(?P<text>.*)\]\((?P<link>[^\)]*)\)', r'\1'),
        # Remove italics / bold: '*' -> ''
        (r'\*', r''),
    ]

    for pattern, repl in substitutions:
        markdown = re.sub(pattern, repl, markdown)

    return markdown
