#!/usr/bin/env python

import h5py
from dataset import IndexedArray


def h5url(url, suffix=".h5"):
    """
    url in the form of path/xxx.h5/groupname
                       path/xxx.h5/groupname1/groupname2
    """
    items = url.split(suffix)
    path = items[0] + suffix
    try:
        grpname = items[1]
        if grpname.startswith("/"):
            grpname = grpname[1:]
        if grpname.endswith("/"):
            grpname = grpname[:-1]
    except:
        grpname = None

    return path, '/'+grpname


def build_indexedarray(dataname):
    fpath, dpath = h5url(dataname)
    datafile = h5py.File(fpath, 'r')
    result = IndexedArray(datafile[dpath])
    return result
