from itertools import izip
import cPickle
from pickleslice import *  # for pickling slice objects

import numpy as np

class Dataset(object):
    """ Corresponds to a dataset in h5py, the items in the .attrs
        are regarded as pickled python objects.

        Since the dataset is an numpy array living in .h5 files,
        instances of this class support numpy indexing on them. Also
        instance.<attr> will try to return object (including methods)
        if they so initiated.
    """
    def __init__(self, dataset):
        self._dataset = dataset
        try:
            # in case there's a .attrs attached to this
            # dataset, we initiate its contents as attributes
            for n,v in dataset.attrs.iteritems():
                self.__setattr__(n, cPickle.loads(v))
        except AttributeError:
            pass

    def __getitem__(self, v):
        return self._dataset.__getitem__(v)

    def __setitem__(self, i, v):
        return self._dataset.__setitem__(i, v)

    def __getattr__(self, n):
        try:
            return getattr(self._dataset, n)
        except AttributeError:
            try:
                return self.__dict__[n]
            except KeyError:
                raise AttributeError, n

class IndexedArray(Dataset):

    def __init__(self, dataset=None):
        if isinstance(dataset, IndexedArray):
            Dataset.__init__(self, None)
            self.__dict__.update(dataset.__dict__)
        else:
            Dataset.__init__(self, dataset)

    def __getitem__(self, axname_or_idxarray):
        """(easy slicing) we want to say
                indexedarray[indexedarray['name']<.005]
                # __getitem__() on indexedarray twice.
           as a shorthand to
                indexedarray[:,:,:,(indexedarray.axis[indexedarray.axisnames.index('name')]<.005).squeeze(),:]
                # __getitem__ on indexedarray once and is indexing the _dataset
           how do you do this in matlab?

           if indexedarray['name'] returns full-sized True/False array as
           indexedarray, could be very memory-wasting, if let
           indexedarray['name'] returns only the axis, can be potentially
           interesting when the results are used to 'fancy'-index indexedarray
           itself. This implementation tries the latter, only returns
           True/False (1/0 actually) in the format of an ogrid.
        """
        axisnames = self.axisnames

        if isinstance(axname_or_idxarray, str):
            axname = axname_or_idxarray
            try:
                return self.axis[axisnames.index(axname)]
            except ValueError:
                # could be trying to index one of the field of the
                # underlying array (with fields)
                dataset = self._dataset.__getitem__(axname)
                obj = IndexedArray(self)
                obj._dataset = dataset
                return obj
        elif isinstance(axname_or_idxarray, np.ndarray):
            # idxarr.shape must equal one of the axes (CRITICAL!)
            idxarr = axname_or_idxarray
            idxarrbool = idxarr.astype(np.bool)
            if idxarrbool.size==1:
                if idxarrbool.flat[0]: # is True (select the only one)
                    indices = [slice(None) for ax in self.axis]
                    mutidx = -1  # no axis is changed
                else:
                    raise "Nothing is sliced and returned!"
            else:
                # when idxarr is of different shape than any axis, then
                # it has to be another variables we have data for, hence
                # full array is returned (do not recognize that new axis)
                indices = [idxarrbool.squeeze() if ax.shape==idxarr.shape else slice(None)
                           for ax in self.axis]
                isarray = [isinstance(i, np.ndarray) for i in indices]
                mutidx = isarray.index(1) if isarray else -1 # indices that are arrays (being sliced)

            dataset = self._dataset.__getitem__(tuple(indices))

            # make the output obj
            myaxis = self.axis[:]
            if mutidx>-1:
                # reshape .axis
                oldshape = self.axis[mutidx].shape
                newshape = tuple([1 if n==1 else -1 for n in oldshape])
                myaxis[mutidx] = self.axis[mutidx][idxarrbool].reshape(newshape)

            obj = IndexedArray(self)
            obj._dataset = dataset
            obj.axis = myaxis
            return obj
        else:
            return self._dataset.__getitem__(axname_or_idxarray)


    def squeeze(self):
        """ Squeeze multidimension data, put dimension with only one value into a
            key-value pair in .params; takes care of .axis and .axisnames
        """
        self._dataset = self._dataset.squeeze()
        axis, axnames = self.axis, self.axisnames

        singleax = ((name, ax.flat[0]) for ax,name in izip(axis, axnames) if ax.size==1)
        self.params.update(dict(singleax))
        remainax = [ax for ax in axis if ax.size>1]
        self.axisnames = [n for ax,n in izip(axis, axnames) if ax.size>1]

        # clean up the dimension of each axis by figuring out the indices
        takeall = [slice(None) for ax in axis]
        takefirst = [0 for ax in axis]
        single = [ax.size==1 for ax in axis]
        s = tuple(np.choose(single, [takeall, takefirst]))

        newaxis = [ax[s] for ax in remainax]
        self.axis = newaxis
        return self


    def get_params(self, indice_list):
        """ return parameter dict for a single data element we have, by
            suppling a list of the indices (a list of ints) of that data
            element.

            The length of indice_list has to be equal to that of self.axisnames,
            or that of the self.axis.
        """
        self.squeeze()
        res = self.params.copy()
        for name,axis,idx in izip(self.axisnames, self.axis, indice_list):
            res.update( {name : axis.flat[idx]} )
        return res

