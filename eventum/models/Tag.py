"""
.. module:: Tag
    :synopsis: A generic tag database model.

.. moduleauthor:: Evan Goldstein
"""

from datetime import datetime
from mongoengine import Document, DateTimeField, StringField, DoesNotExist
from eventum.models import BaseEventumDocument

now = datetime.now


class Tag(Document, BaseEventumDocument):
    """A generic tag object

    :ivar date_created: :class:`mongoengine.fields.DateTimeField` - The date
        the tag was created.
    :ivar date_modified: :class:`mongoengine.fields.DateTimeField` - The date
        the tag was last modified.
    :ivar tagname: :class: 'mongoengine.fields.StringField' - The name of the
        tag.
    """

    # MongoEngine ORM metadata
    meta = {
        'indexes': [],
        'ordering': []
    }

    date_created = DateTimeField(default=now, required=True)
    data_modified = DateTimeField(default=now, required=True)
    tagname = StringField(unique=True, max_length=255, required=True)

    def clean(self):
        """Called by Mongoengine on every ``.save()`` to the object.

        Update date_modified
        """

        self.date_modified = now()

    @classmethod
    def get_or_create_tags(cls, tagnames):
        """Get or creates the tags in tagnames

        :returns: list of tags

        :rtype: list of tag objects

        """
        tags_list = []
        for tagname in tagnames:
            try:
                tags_list.append(cls.objects().get(tagname=tagname))
            except DoesNotExist:
                tag = Tag(tagname=tagname)
                tag.save()
                tags_list.append(tag)
        return tags_list

    def __unicode__(self):
        """This tag, as a unicode string.

        :returns: The name of this tag
        :rtype: str
        """

        return self.tagname

    def __repr__(self):
        """The representation of this tag.

        :returns: The tag's name.
        :rtype: str
        """

        return self.tagname
