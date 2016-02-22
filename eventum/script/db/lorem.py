"""
.. module:: lorem
    :synopsis: This module contains dummy text variables for creating fake
        entries in the database.

.. moduleauthor:: Dan Schlosser <dan@schlosser.io>
"""


LOREM_SNIPPET = """Lorem ipsum **dolor sit amet**, consectetur *adipiscing*
elit. In sed ligula dolor. Morbi at mauris euismod, tincidunt dui eget, tempor
[augue](https://adicu.com).
"""

LOREM_MARKDOWN = """Lorem ipsum dolor sit amet, consectetur adipiscing elit.
In sed ligula dolor. **Maecenas ultrices eros id nisl mollis, sit amet tempor
ante** fermentum. Nulla non nisl hendrerit, porttitor velit id, tincidunt urna.
Nam mollis justo et lectus fringilla, quis maximus arcu faucibus. Cras henderit
eros id ipsum suscipit finibus. *Sed vitae consequat elit, in facilisis ipsum.*
Integer congue suscipit nunc, ac elementum tortor luctus lobortis. Pellentesque
habitant morbi tristique senectus et netus et malesuada fames ac turpis
egestas. Morbi at mauris euismod, tincidunt dui eget, tempor
[augue](https://adicu.com).

Aenean vel ullamcorper dui. Morbi ultrices ipsum vitae nisl malesuada sagittis.
Sed consectetur egestas augue in malesuada. Aenean pharetra est sem, at auctor
sem efficitur in. Nam eget erat egestas, sollicitudin massa sagittis, accumsan
neque. Fusce aliquam viverra nisl, ac finibus velit pharetra non. Sed semper
dui sit amet dolor tristique, eu mollis ante rutrum. Duis vel odio maximus
purus tincidunt bibendum congue id ante. Nulla bibendum arcu non nisl lobortis
tristique.

{}

- Vivamus iaculis vehicula tempor. Pellentesque habitant morbi tristique
senectus et netus et malesuada fames ac turpis egestas
- Donec porttitor risus sed ex ultrices, iaculis sagittis lectus porttitor
- Nunc sit amet convallis massa. Nullam vehicula cursus gravida
- Fusce ullamcorper nibh sed aliquet pretium
- Proin in sodales diam
- Mauris ut finibus tellus

Suspendisse placerat laoreet orci sit amet ultricies. Class aptent taciti
sociosqu ad litora torquent per conubia nostra, per inceptos himenaeos. Aenean
quam magna, viverra at consequat non, vehicula aliquet massa. Donec
condimentum, velit et laoreet interdum, tellus ex aliquam elit, vel condimentum
sem diam sit amet lorem.

```python
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        lookup_current_user()
        try:
            if g.user is None or 'gplus_id' not in session:
                return redirect(url_for('auth.login', next=request.url))
        except AttributeError:
            return redirect(url_for('auth.login', next=request.url))
        return f(*args, **kwargs)
    return decorated_function
```

Mauris pulvinar erat et metus volutpat, a scelerisque
mauris tempor. Quisque tristique massa in mi pretium, id sollicitudin justo
vehicula. Sed hendrerit tellus vitae suscipit sollicitudin. Nulla mollis
vehicula est, ut scelerisque leo mattis a. Suspendisse cursus felis non neque
pulvinar faucibus. Quisque ullamcorper, quam non vulputate convallis, odio enim
molestie metus, pretium eleifend massa massa ut nibh. Morbi posuere gravida
molestie.

1. Pellentesque habitant morbi tristique senectus et netus et malesuada fames
ac turpis egestas
2. Quisque quis turpis accumsan, pharetra risus sed, sagittis ligula
3. Ut interdum dui id sapien elementum molestie
4. Pellentesque habitant morbi tristique senectus et netus et malesuada fames
ac turpis egestas
5. Donec porta tempus magna sit amet vulputate
6. Duis tempus, nunc eget feugiat mollis, lorem justo sodales est, et finibus
nisl elit et elit
7. Etiam euismod aliquet ante in pulvinar.

Nullam nec eleifend ligula. Nunc feugiat sapien vitae urna sagittis, non
fringilla libero vulputate. Nulla sed ligula eget turpis fermentum
sollicitudin. Duis egestas metus vitae lacus feugiat, a fringilla mi rutrum.
Sed id ex non sapien dictum consectetur eu maximus turpis. Phasellus nulla
elit, mollis eu dolor in, sollicitudin convallis nunc. Maecenas nibh massa,
sollicitudin in pretium et, tempus et felis.
"""

# blog posts have images in the description.
LOREM_BLOG_POST = LOREM_MARKDOWN.format('![]({})\n\n![]({})')

# events do not
LOREM_EVENT = LOREM_MARKDOWN.format('')

LOREM_ADJECTIVES = ['Awesome', 'Amazing', 'Exciting', 'Educational', 'Fun',
                    'Incredible', 'Splendorous', 'Zany']
