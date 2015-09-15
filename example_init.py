#!/usr/bin/env python
""" Example of building a dataset
"""
from cPickle import dumps
import numpy as np
from numpy import s_

from dataset import Dataset


if __name__=='__main__':

    # parameter that are kept constant across this data, e.g. dates etc.
    meta = {'Param'             : -70,
            'n_of_neuron'       : 1000,
            'n_dend.per.neuron' : 40,
            'lower.param'       : 0,
            'soma.gkbar_hh3'    : .0001,
            'exposure'          : .1,
            'learnng rate'      : .01,
           }

    # slower-changing dimensions first
    # variable myaxis is not saved, only mygrid is saved. This makes myaxis
    # specification more flexible, for example, we specify the exponent with the
    # proper name, and then massage the final mygrid.
    step = .0001
    myaxis = [
        ('syn1.maxg.AMPA2exp',    s_[ -1 :  2 : 1 ]), # log2 ratio over the unit maxg
        ('syn1.maxg.NMDA_MgNN',   s_[ -1 :  2 : 1 ]), # log2 ratio over the unit maxg
        ('syn1.x',                s_[ 0  : .8 : .1]), # at 0.3
        ('dt_syn2_syn1',          s_[-20 : 21 : 1 ]),
    ]
    myaxes = [ax for axname,ax in myaxis]
    mygrid = np.ogrid[myaxes] # this gives a list of n arrays, n==ndim
    # here we massage mygrid to be what it actually should be:
    mygrid[0] = (2**mygrid[0]) * step
    mygrid[1] = (2**mygrid[1]) * step

    # shall we run locally to get the data back so we know the returned data type?
    gridshape = sum(mygrid).shape # this quick and dirty, but needs memory broadcasted
    dtype = {'names':   ['depvar1','dep.var2','dep var 3. v(0.5)'],
             'formats': ['int','float64','float64']}

    import h5py
    f = h5py.File('test.h5','a')
    #exps = f.create_group('experiments')
    result = f.create_dataset('result', shape=gridshape, dtype=dtype)

    result.attrs['params']      = dumps( meta, protocol=2 )
    result.attrs['axis']        = dumps( mygrid, protocol=2 )
    result.attrs['axisnames']   = dumps( [n for n,v in myaxis], protocol=2 )

    f.close()
