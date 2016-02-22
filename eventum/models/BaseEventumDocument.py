import types


class BaseEventumDocument(object):
    _registered_attributes = []

    @classmethod
    def deregister_attribute(cls, name):
        if name not in cls._registered_attributes:
            raise ValueError('Cannot delete attribute.')
        cls._registered_attributes.remove(name)
        delattr(cls, name)

    @classmethod
    def register_method(cls, method):
        if hasattr(cls, method.__name__):
            raise ValueError('Method exists.')

        cls._registered_attributes.append(method.__name__)
        return setattr(cls,
                       method.__name__,
                       types.MethodType(method, None, cls))
