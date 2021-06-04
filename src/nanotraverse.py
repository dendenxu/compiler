from nanoast import *


def traverse(node: Node):
    if not isinstance(node, Node):
        tree = {}
        tree['name'] = str(node)
        return tree
    tree = {}
    tree['name'] = node.__class__.__name__
    children = [c for c in node.__dict__.keys() if not c.startswith('_')]
    if len(children) == 0:
        return tree
    tree['children'] = []
    for child in children:
        child = getattr(node, child)
        if isinstance(child, list):
            for c in child:
                tree['children'].append(traverse(c))
        else:
            tree['children'].append(traverse(child))

    return tree
