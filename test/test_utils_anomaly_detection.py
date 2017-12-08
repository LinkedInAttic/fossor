# Copyright 2017 LinkedIn Corporation. All rights reserved. Licensed under the BSD-2 Clause license.
# See LICENSE in the project root for license information.

import sys
import random
import logging

from fossor.utils import anomaly_detection

logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)
log = logging.getLogger(__name__)


def test_rare_distribution():
    foo = [random.randint(0, 10) for x in range(1000)]
    assert not anomaly_detection.abnormal_distribution(foo)

    foo = [random.randint(0, 10) for x in range(1000)] + [11 for x in range(25)]
    assert anomaly_detection.abnormal_distribution(foo)

    foo = [random.randint(0, 10) for x in range(500)] + [5 for x in range(100)] + [random.randint(0, 10) for x in range(500)]
    assert anomaly_detection.abnormal_distribution(foo)

    foo = [random.randint(0, 10) for x in range(1000)] + [14 for x in range(15)]
    assert anomaly_detection.abnormal_distribution(foo)


def test_within_three_sigma():
    values = [1 for x in range(1000)]
    assert anomaly_detection.within_three_sigma(values=values)


def test_outside_two_and_three_sigma():
    values = [1 for x in range(1000)] + [1000 for x in range(100)]
    assert not anomaly_detection.within_three_sigma(values=values)


def test_outside_two_and_three_2_sigma():
    values = [1 for x in range(100)] + [50 for x in range(1000)] + [1000 for x in range(100)]
    assert not anomaly_detection.within_three_sigma(values=values)


def test_outside_third_sigma():
    values = [1 for x in range(50)] + [50 for x in range(1000)] + [1000 for x in range(50)]
    assert not anomaly_detection.within_three_sigma(values=values)
