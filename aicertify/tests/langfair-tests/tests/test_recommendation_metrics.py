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

from langfair.metrics.recommendation import RecommendationMetrics
from langfair.metrics.recommendation.metrics import PRAG, SERP, JaccardSimilarity

datafile_path = "tests/data/recommendation/recommendation_dict_file.csv"
with open(datafile_path, "r") as f:
    data = json.load(f)


def test_jaccard():
    jaccard = JaccardSimilarity()
    x = jaccard.evaluate(data["female_rec_lists"][0], data["male_rec_lists"][0])
    assert x == 1 / 3


def test_prag():
    prag = PRAG()
    x = prag.evaluate(data["female_rec_lists"][0], data["male_rec_lists"][0])
    assert x == 0.16666666666666666


def test_prag2():
    prag = PRAG()
    x = prag.evaluate(data["female_rec_lists"][0][:1], data["male_rec_lists"][0])
    assert x == 0


def test_serp():
    serp = SERP()
    x = serp.evaluate(data["female_rec_lists"][0], data["male_rec_lists"][0])
    assert x == 0.25


def test_recommendation1():
    actual_result_file_path = (
        "tests/data/recommendation/recommendation_results_pairwise.json"
    )
    with open(actual_result_file_path, "r") as f:
        actual_result_pairwise = json.load(f)
    recommendation = RecommendationMetrics()
    score = recommendation.evaluate_pairwise(
        data["female_rec_lists"], data["male_rec_lists"]
    )
    assert score == actual_result_pairwise


def test_recommendation2():
    actual_result_file_path = (
        "tests/data/recommendation/recommendation_results_against_neutral.json"
    )
    with open(actual_result_file_path, "r") as f:
        actual_result_against_neutral = json.load(f)
    recommendation = RecommendationMetrics()
    score = recommendation.evaluate_against_neutral(
        neutral_dict=data["neutral_dict"],
        group_dict_list=[data["male_dict"], data["female_dict"]],
    )
    assert score == actual_result_against_neutral
