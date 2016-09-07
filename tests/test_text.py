import pytest

from eventum.lib.text import clean_markdown


@pytest.mark.parametrize(["markdown", "output"], [
    ('**Bold** text is unbolded.', 'Bold text is unbolded.'),
    ('So is *underlined* text.', 'So is underlined text.'),
    ('An [](http://empty-link).', 'An.'),
    ('A [test](https://adicu.com)', 'A test (https://adicu.com)'),
    ('A [test](http://adicu.com)', 'A test (http://adicu.com)'),
    ('A [test](garbage) passes.', 'A test passes.'),
    ('An ![image](http://anything) gets removed.', 'An gets removed.'),
    ('An ![image](garbage), [link](http://adicu.com), and an '
     '[![image in a link](imgurl)](http://adicu.com).',
     'An, link (http://adicu.com), and an.'),
])
def test_clean_markdown(markdown, output):
    assert clean_markdown(markdown) == output
