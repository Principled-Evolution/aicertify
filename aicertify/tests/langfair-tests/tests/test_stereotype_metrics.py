# Copyright 2024 CVS Health and/or one of its affiliates
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import json
import os
import platform
import unittest

import numpy as np

from langfair.metrics.stereotype import StereotypeMetrics
from langfair.metrics.stereotype.metrics import (
    CooccurrenceBiasMetric,
    StereotypeClassifier,
    StereotypicalAssociations,
)

datafile_path = "tests/data/stereotype/stereotype_data_file.json"
with open(datafile_path, "r") as f:
    data = json.load(f)

actual_result_file_path = "tests/data/stereotype/stereotype_results_file.json"
with open(actual_result_file_path, "r") as f:
    actual_results = json.load(f)


def test_associations1():
    association = StereotypicalAssociations(target_category="adjective")
    x = association.evaluate(responses=data["responses"])
    assert x == actual_results["test1"]


def test_associations2():
    association = StereotypicalAssociations(target_category="profession")
    x = association.evaluate(responses=data["responses_profession"])
    assert x == actual_results["test2"]


def test_coocurrence1():
    cobs = CooccurrenceBiasMetric(target_category="adjective")
    x = cobs.evaluate(responses=data["responses"])
    np.testing.assert_almost_equal(x, actual_results["test3"], 5)


def test_coocurrence2():
    cobs = CooccurrenceBiasMetric(target_category="profession")
    x = cobs.evaluate(responses=data["responses_profession"])
    np.testing.assert_almost_equal(x, actual_results["test4"], 5)


@unittest.skipIf(
    ((os.getenv("CI") == "true") & (platform.system() == "Darwin")),
    "Skipping test in macOS CI due to memory issues.",
)
def test_classifier1():
    classifier = StereotypeClassifier(metrics=["Stereotype Fraction"])
    x = classifier.evaluate(responses=data["responses_fraction"], return_data=True)
    assert x["metrics"] == actual_results["test5"]["metrics"]
    assert x["data"]["response"] == data["responses_fraction"]


@unittest.skipIf(
    ((os.getenv("CI") == "true") & (platform.system() == "Darwin")),
    "Skipping test in macOS CI due to memory issues.",
)
def test_classifier2():
    classifier = StereotypeClassifier()
    score = classifier.evaluate(
        responses=data["responses_fraction"], prompts=data["prompts"], return_data=False
    )
    ans = actual_results["test6"]["metrics"]
    assert all([abs(score["metrics"][key] - ans[key]) < 1e-5 for key in ans])


@unittest.skipIf(
    ((os.getenv("CI") == "true") & (platform.system() == "Darwin")),
    "Skipping test in macOS CI due to memory issues.",
)
def test_StereotypeMetrics():
    stereotypemetrics = StereotypeMetrics()
    score = stereotypemetrics.evaluate(
        responses=data["responses_fraction"], prompts=data["prompts"]
    )
    ans = actual_results["test7"]["metrics"]
    assert all([abs(score["metrics"][key] - ans[key]) < 1e-5 for key in ans])
