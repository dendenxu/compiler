from nanoast import *


def traverse(node: Node):
    if not isinstance(node, Node):
        tree = {}
        tree['name'] = str(node)
        return tree
    tree = {}
    tree['name'] = node.__class__.__name__[:-4]
    tree['_children'] = []

    attrnames = [attrname for attrname in node.__dict__.keys() if not attrname.startswith('_')]

    FLAG = False

    if len(attrnames) == 1:
        attr = getattr(node, attrnames[0])
        if not isinstance(attr, list) or len(attr) == 1:
            if isinstance(attr, list):
                attr = attr[0]
            ctree = traverse(attr)
            tree['name'] += f"{{{ctree['name']}}}"
            if '_children' in ctree:
                for c in ctree['_children']:
                    tree['_children'].append(c)
        else:
            FLAG = True
    else:
        FLAG = True

    if FLAG:
        for attrname in attrnames:
            attr = getattr(node, attrname)
            if isinstance(attr, list):
                for a in attr:
                    tree['_children'].append(traverse(a))
            else:
                tree['_children'].append(traverse(attr))

    if len(tree['_children']) == 0:
        del tree['_children']

    return tree
