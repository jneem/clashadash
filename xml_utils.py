# -*- coding: utf-8 -*-

def xmlToDict(root):
    if list(root):
        ret = {}
        for child in root:
            ret[child.tag] = xmlToDict(child)
        return ret
        
    return root.text
    