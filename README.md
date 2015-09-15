The Problem
============

Quantitative (scientific) data collected in controlled experiments consist of
factors known as the independent variables and the dependent variables. A
collection of data must incorporate both to be complete and possibly useful.

The way a lot of exploratory experiments or parameter searching are done is
expressed by the following pseudo-code:

for indep_var1 in [v10, v11, ..., v1m]:
    for indep_var2 in [v20, v21, ..., v2n]:
        dep_var1, dep_var2, dep_var3,... = do_experiment(indep_var1, indep_var2)
    end
end

We see plenty of this kind of code. But it has the following problems:

1. does not take care of the storage of the data (dep_var1, dep_var2,...);

2. forgets the mapping between the values of dependent variables and the
independent variable values;

3. is strictly serial, meaning it does not use the cluster to parallelly
sample through independent variables.


A Solution
=============

How should we store/manage/retrieve data in our experiments? I have been
thinking about this and this is the answer I came up with to solve the first 2
problems. It's been working for me for more than one year already, and the code
are pretty stabilized without much change for about one year. It should have
been in form of a Python module, but my initial attempt to package it as such
failed for insufficient time. Since recently I heard conversations within the
lab about how our data should be better organized, I am putting this code out
without much of formal packaging. Simple checkout or copy over the files in one
directory and run example_init.py to initialize an example data file. Then run
example.py to play with that data (now loaded as variable M).

Here are some examples I composed long before for using this kind of data, not
necessarily identical in terms of dimensionality of data, axis etc etc, but you
will get an idea:


In [11]: M                      # M is a 7-dim array
Out[11]: <dataset.IndexedArray object at 0x9ca126c>

In [12]: M.shape
Out[12]: (2, 1, 9, 9, 10, 75, 41)

In [13]: M.dtype
Out[13]: dtype([('dt', '<i4'), ('nonlinearity', '<f8'), ('int_depol soma.v(0.5)', '<f8')])

In [14]: M['nonlinearity'].shape
Out[14]: (2, 1, 9, 9, 10, 75, 41)

In [15]: M['nonlinearity'].dtype
Out[15]: dtype('float64')

In [16]: M.axisnames            # Names of independent variables (axes)
Out[16]:
['syn1.maxg.AMPA2exp',
 'syn1.maxg.NMDA_MgNN',
 'syn1.x',
 'syn2.x',
 'syn2.maxg.AMPA2exp',
 'syn2.maxg.NMDA_MgNN',
 'dt_syn2_syn1']

In [17]: M['syn1.x']            # Values of one independent variable
Out[17]:
array([[[[[[[ 0.1]]]],
         [[[[ 0.2]]]],
         [[[[ 0.3]]]],
         [[[[ 0.4]]]],
         [[[[ 0.5]]]],
         [[[[ 0.6]]]],
         [[[[ 0.7]]]],
         [[[[ 0.8]]]],
         [[[[ 0.9]]]]]]])

In [18]: M2 = M[ M['syn1.x']<.5 ][ M['syn2.x']>.5 ]     # Fancier indexing!

In [19]: M2
Out[19]: <dataset.IndexedArray object at 0xd3fa28c>

In [20]: M2.shape
Out[20]: (2, 1, 4, 4, 10, 75, 41)

In [22]: M2['syn1.x']
Out[22]:
array([[[[[[[ 0.1]]]],
         [[[[ 0.2]]]],
         [[[[ 0.3]]]],
         [[[[ 0.4]]]]]]])

In [21]: M2.dtype
Out[21]: dtype([('dt', '<i4'), ('nonlinearity', '<f8'), ('int_depol soma.v(0.5)', '<f8')])

In [22]: M.params
Out[22]: ...                    # the dictionary of meta data
