# pickle slices
import copy_reg

def pickleSlice(slice):
    return unpickleSlice, (slice.start, slice.stop, slice.step)

def unpickleSlice(start, stop, step):
    return slice(start, stop, step)

copy_reg.pickle(slice, pickleSlice, unpickleSlice)
