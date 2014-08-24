# -*- coding: utf-8 -*-
'''

'''
from __future__ import absolute_import
import inspect


def object_to_dict(obj, exclude_private = True):
    pr = {}
    for name in dir(obj):
        value = getattr(obj, name)
        if not name.startswith('__') and not inspect.ismethod(value):
            if exclude_private and name.startswith('_'):
                pass
            else:
                pr[name] = value
    return pr