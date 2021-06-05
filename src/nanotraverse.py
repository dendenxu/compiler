from nanoast import *

CHILDREN = "_children"
NAME = "name"


def traverse(node: Node):
    if not isinstance(node, Node):
        tree = {}
        tree[NAME] = str(node)
        return tree
    tree = {}
    tree[NAME] = node.__class__.__name__[:-4]
    tree[CHILDREN] = []

    attrnames = [attrname for attrname in node.__dict__.keys() if not attrname.startswith('_')]

    FLAG = False

    if len(attrnames) == 1:
        attr = getattr(node, attrnames[0])
        if not isinstance(attr, list) or len(attr) == 1:
            if isinstance(attr, list):
                attr = attr[0]
            ctree = traverse(attr)
            tree[NAME] += f"{{{ctree[NAME]}}}"
            if CHILDREN in ctree:
                for c in ctree[CHILDREN]:
                    tree[CHILDREN].append(c)
        else:
            FLAG = True
    else:
        FLAG = True

    if FLAG:
        for attrname in attrnames:
            attr = getattr(node, attrname)
            if isinstance(attr, list):
                for a in attr:
                    tree[CHILDREN].append(traverse(a))
            else:
                tree[CHILDREN].append(traverse(attr))

    if len(tree[CHILDREN]) == 0:
        del tree[CHILDREN]

    return tree


def depth(tree: dict):
    d = 0
    if isinstance(tree, dict) and CHILDREN in tree:
        for c in tree[CHILDREN]:
            cur_d = depth(c)
            if cur_d > d:
                d = cur_d
    return d + 1
