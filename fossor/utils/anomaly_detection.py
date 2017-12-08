# Copyright 2017 LinkedIn Corporation. All rights reserved. Licensed under the BSD-2 Clause license.
# See LICENSE in the project root for license information.

import math
import logging
import statistics


log = logging.getLogger(__name__)

# Percent of values with X sigmas, used in various standard 3 sigma checks.
ONE_SIGMA_PERCENT = 0.68
TWO_SIGMA_PERCENT = .9545
THREE_SIGMA_PERCENT = .9973


def within_stdev_percent(values, x_stdev, percent_threshold, min_values=100):
    '''Return True if percent_threshold of values are within x_stdev of the mean.'''
    if len(values) < min_values:
        return True

    mean = statistics.mean(values)
    stdev = statistics.stdev(values)
    found = []
    for v in values:
        diff = abs(mean - v)
        if diff <= (stdev * x_stdev):
            found.append(v)
    percent_found = len(found) / len(values)
    result = percent_found > percent_threshold
    log.debug(f"Within {x_stdev} sigma check was {result}. {percent_found:.2f}%/{percent_threshold:.2f}% within stdev*{x_stdev}. "
              f"Mean: {mean:.2f}. Stdev: {stdev:.2f}. Acceptable range was: {mean - stdev * x_stdev:.2f} - {mean + stdev * x_stdev:.2f}")
    return result


def within_one_sigma(values, percent_threshold=ONE_SIGMA_PERCENT, min_values=100):
    return within_stdev_percent(values=values, x_stdev=1, percent_threshold=percent_threshold, min_values=min_values)


def within_two_sigma(values, percent_threshold=TWO_SIGMA_PERCENT, min_values=100):
    return within_stdev_percent(values, x_stdev=2, percent_threshold=percent_threshold, min_values=min_values)


def within_three_sigma(values, percent_threshold=THREE_SIGMA_PERCENT, min_values=100):
    return within_stdev_percent(values, x_stdev=3, percent_threshold=percent_threshold, min_values=min_values)


def within_all_three_sigma(values, min_values=100):
    '''
    Return false if something does not pass a standard three sigma test.
    If the number of values is less than min_values, will always return False
    '''
    return within_one_sigma(values) and within_two_sigma(values) and within_three_sigma(values)


def abnormal_distribution(values, ignore_zero=False, probability=1e-30):
    '''
    Return True if too many values fall within the same sigma consecutively, meaning the distribution is not normal according to the 3 sigma rule.
    Probability is loosely the likelihood of this test triggering during a normal distribution. A lower value means fewer false positives.
    '''

    result = False

    if ignore_zero:
        values = [value for value in values if value != 0]

    one_sigma_threshold = math.log10(probability) / math.log10(1 - ONE_SIGMA_PERCENT)
    two_sigma_threshold = math.log10(probability) / math.log10(1 - TWO_SIGMA_PERCENT)
    three_sigma_threshold = math.log10(probability) / math.log10(1 - THREE_SIGMA_PERCENT)

    mean = statistics.mean(values)
    stdev = statistics.stdev(values)

    one_sigma = stdev * 1
    two_sigma = stdev * 2
    three_sigma = stdev * 3

    one_sigma_count = 0
    two_sigma_count = 0
    three_sigma_count = 0

    one_sigma_count_max = 0
    two_sigma_count_max = 0
    three_sigma_count_max = 0
    for v in values:
        diff = abs(mean - v)
        if diff < one_sigma:
            one_sigma_count += 1
            one_sigma_count_max = max(one_sigma_count, one_sigma_count_max)
            two_sigma_count = 0
            three_sigma_count = 0
        elif diff < two_sigma:
            one_sigma_count = 0
            two_sigma_count += 1
            two_sigma_count_max = max(two_sigma_count, two_sigma_count_max)
            three_sigma_count = 0
        elif diff < three_sigma:
            one_sigma_count = 0
            two_sigma_count = 0
            three_sigma_count += 1
            three_sigma_count_max = max(three_sigma_count, three_sigma_count_max)
        if one_sigma_count > one_sigma_threshold or \
           two_sigma_count > two_sigma_threshold or \
           three_sigma_count > three_sigma_threshold:
            result = True

    log.debug(f"Abnormal Distribution: {result}. Max consecutive values within one, two, and three sigma in a row: "
              f"{one_sigma_count_max}/{one_sigma_threshold:.2f}, "
              f"{two_sigma_count_max}/{two_sigma_threshold:.2f}, "
              f"{three_sigma_count_max}/{three_sigma_threshold:.2f}. "
              f"Mean: {mean:.2f}. Stdev: {stdev:.2f}.")
    return result
