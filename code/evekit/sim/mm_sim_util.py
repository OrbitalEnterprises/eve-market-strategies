"""
Market Maker sim utilities
"""
import scipy.interpolate
import numpy.random
import numpy as np


def create_sample_generator(data, bin_count, seed):
    counts, bins = np.histogram(data, bins=bin_count, density=True)
    cum_values = np.zeros(bins.shape)
    cum_values[1:] = np.cumsum(counts*np.diff(bins))
    inv_cdf = scipy.interpolate.interp1d(cum_values, bins)
    rnd = numpy.random.RandomState(seed)
    return lambda: int(inv_cdf(rnd.rand()))


def create_boolean_sample_generator(true_count, false_count, seed):
    true_threshold = true_count / (true_count + false_count)
    true_gen = numpy.random.RandomState(seed)
    return lambda: True if true_gen.rand() <= true_threshold else False
