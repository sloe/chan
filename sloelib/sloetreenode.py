
class SloeTreeNode(object):
    def __init__(self, type):
        self._d = {
            "type": type
        }

    def get(self, name, default):
        node = object.__getattribute__(self, "_d")
        if name in node:
            return node[name]
        else:
            return default


    def set_value(self, name, value):
        self._d[name] = value


    def __getattr__(self, name):
        node = object.__getattribute__(self, "_d")
        if name in node:
            return node[name]
        else:
            raise AttributeError(name)


