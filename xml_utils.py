# -*- coding: utf-8 -*-

def xmlToDict(root):
    """
    Turns an XML tree into a nested python dictionary.

    If an element has multiple children with the same tag, they will
    be stored as a list of dictionaries.
    """
    if list(root):
        ret = {}
        for child in root:
            if child.tag in ret:
                val = ret[child.tag]
                if isinstance(val, list):
                    val.append(xmlToDict(child))
                else:
                    val = [val, xmlToDict(child)]
                ret[child.tag] = val
            else:
                ret[child.tag] = xmlToDict(child)
        return ret
        
    return root.text

