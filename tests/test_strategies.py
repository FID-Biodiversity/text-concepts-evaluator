import pytest

from text_evaluator.strategy import (
    DocumentMetadata,
    ConceptFractionInAllWordsStrategy,
    ConceptFractionInAllConceptsStrategy,
    ConceptFractionFilteredByFractionAverageStrategy,
    ConceptFilteredByFractionAverageMentionsBoostedStrategy,
    Strategy,
)


class TestConceptFractionInAllWordsStrategy:
    @pytest.mark.parametrize(
        ["document_metadata", "strategy", "expected_concepts"],
        [
            (  # Scenario - Single annotation
                DocumentMetadata(
                    statistics={
                        "count": {
                            "https://www.biofid.de/ontology/2": 1,
                        }
                    },
                    text="<sentence id='12345'>Das ist ein annotierter Text.</sentence>"
                    "<sentence>Darin kommt auch ein "
                    "<em class='animal_fauna' biofid-uri-0='https://www.biofid.de/ontology/2'>Waschbär</em> "
                    "vor.</sentence>",
                ),
                {},
                [
                    "https://www.biofid.de/ontology/2",
                ],
            ),
            (  # Scenario - Threshold given at the edge of the URI fraction
                DocumentMetadata(
                    statistics={
                        "count": {
                            "https://www.biofid.de/ontology/2": 1,
                        }
                    },
                    text="<sentence id='12345'>Das ist ein annotierter Text.</sentence>"
                    "<sentence>Darin kommt auch ein "
                    "<em class='animal_fauna' biofid-uri-0='https://www.biofid.de/ontology/2'>Waschbär</em> "
                    "vor.</sentence>",
                ),
                {"min_fraction": 0.1},
                ["https://www.biofid.de/ontology/2"],
            ),
            (  # Scenario - Threshold higher than URI fraction
                DocumentMetadata(
                    statistics={
                        "count": {
                            "https://www.biofid.de/ontology/2": 1,
                        }
                    },
                    text="<sentence id='12345'>Das ist ein annotierter Text.</sentence>"
                    "<sentence>Darin kommt auch ein "
                    "<em class='animal_fauna' biofid-uri-0='https://www.biofid.de/ontology/2'>Waschbär</em> "
                    "vor.</sentence>",
                ),
                {"min_fraction": 0.11},
                [],
            ),
            (  # Scenario - Threshold higher than URI fraction
                DocumentMetadata(
                    statistics={
                        "count": {
                            "https://www.biofid.de/ontology/2": 2,
                            "https://www.biofid.de/ontology/1": 1,
                        }
                    },
                    text="<sentence id='12345'>Das ist ein annotierter Text.</sentence>"
                    "<sentence>Darin kommt auch ein "
                    "<em class='animal_fauna' biofid-uri-0='https://www.biofid.de/ontology/2'>Waschbär</em> "
                    "vor.</sentence>",
                ),
                {},
                [
                    "https://www.biofid.de/ontology/2",
                    "https://www.biofid.de/ontology/1",
                ],
            ),
            (  # Scenario - An annotated multi-token word should not change the result
                DocumentMetadata(
                    statistics={
                        "count": {
                            "https://www.biofid.de/ontology/2": 1,
                        }
                    },
                    text="<sentence id='12345'>Das ist ein annotierter Text.</sentence>"
                    "<sentence>Darin kommt auch ein "
                    "<em class='animal_fauna' biofid-uri-0='https://www.biofid.de/ontology/2'>Procyon lotor</em> "
                    "vor.</sentence>",
                ),
                {"min_fraction": 0.1},
                [
                    "https://www.biofid.de/ontology/2",
                ],
            ),
        ],
        indirect=["strategy"],
    )
    def test_evaluate(
        self,
        document_metadata: DocumentMetadata,
        strategy: Strategy,
        expected_concepts: list,
    ):
        result = strategy.parse(document_metadata)
        assert result.concepts == expected_concepts

    @pytest.fixture
    def strategy(self, request):
        return ConceptFractionInAllWordsStrategy(**request.param)


class TestConceptFractionInAllConceptStrategy:
    @pytest.mark.parametrize(
        ["document_metadata", "strategy", "expected_concepts"],
        [
            (  # Scenario - Single annotation
                DocumentMetadata(
                    statistics={
                        "count": {
                            "https://www.biofid.de/ontology/2": 2,
                            "https://www.biofid.de/ontology/1": 1,
                            "https://www.biofid.de/ontology/3": 3,
                            "https://www.biofid.de/ontology/4": 4,
                            "https://www.biofid.de/ontology/5": 5,
                        }
                    },
                ),
                {},
                [
                    "https://www.biofid.de/ontology/5",
                    "https://www.biofid.de/ontology/4",
                    "https://www.biofid.de/ontology/3",
                    "https://www.biofid.de/ontology/2",
                    "https://www.biofid.de/ontology/1",
                ],
            ),
            (  # Scenario - Threshold given at the edge of the URI fraction
                DocumentMetadata(
                    statistics={
                        "count": {
                            "https://www.biofid.de/ontology/2": 2,
                            "https://www.biofid.de/ontology/1": 1,
                            "https://www.biofid.de/ontology/3": 3,
                            "https://www.biofid.de/ontology/4": 4,
                            "https://www.biofid.de/ontology/5": 5,
                        }
                    },
                ),
                {"min_fraction": 0.2},
                [
                    "https://www.biofid.de/ontology/5",
                    "https://www.biofid.de/ontology/4",
                    "https://www.biofid.de/ontology/3",
                ],
            ),
            (  # Scenario - Threshold higher than URI fraction
                DocumentMetadata(
                    statistics={
                        "count": {
                            "https://www.biofid.de/ontology/2": 2,
                            "https://www.biofid.de/ontology/1": 1,
                            "https://www.biofid.de/ontology/3": 3,
                            "https://www.biofid.de/ontology/4": 4,
                            "https://www.biofid.de/ontology/5": 5,
                        }
                    },
                ),
                {"min_fraction": 0.21},
                [
                    "https://www.biofid.de/ontology/5",
                    "https://www.biofid.de/ontology/4",
                ],
            ),
        ],
        indirect=["strategy"],
    )
    def test_evaluate(
        self,
        document_metadata: DocumentMetadata,
        strategy: Strategy,
        expected_concepts: list,
    ):
        result = strategy.parse(document_metadata)
        assert result.concepts == expected_concepts

    @pytest.fixture
    def strategy(self, request):
        return ConceptFractionInAllConceptsStrategy(**request.param)


class TestUriFractionFilteredByFractionAverageStrategy:
    @pytest.mark.parametrize(
        ["document_metadata", "expected_concepts"],
        [
            (  # Scenario - Default case
                DocumentMetadata(
                    statistics={
                        "count": {
                            "https://www.biofid.de/ontology/2": 2,
                            "https://www.biofid.de/ontology/1": 1,
                            "https://www.biofid.de/ontology/3": 3,
                            "https://www.biofid.de/ontology/4": 4,
                            "https://www.biofid.de/ontology/5": 5,
                        }
                    },
                ),
                [
                    "https://www.biofid.de/ontology/5",
                    "https://www.biofid.de/ontology/4",
                    "https://www.biofid.de/ontology/3",
                ],
            ),
            (  # Scenario - All annotations have same count -> Concepts come out as in the dict
                DocumentMetadata(
                    statistics={
                        "count": {
                            "https://www.biofid.de/ontology/2": 1,
                            "https://www.biofid.de/ontology/1": 1,
                            "https://www.biofid.de/ontology/3": 1,
                        }
                    },
                ),
                [
                    "https://www.biofid.de/ontology/2",
                    "https://www.biofid.de/ontology/1",
                    "https://www.biofid.de/ontology/3",
                ],
            ),
            (  # Scenario - No concepts are present
                DocumentMetadata(statistics={'count': {}}),
                [],
            ),
        ],
    )
    def test_evaluate(
        self,
        document_metadata: DocumentMetadata,
        strategy: Strategy,
        expected_concepts: list,
    ):
        result = strategy.parse(document_metadata)
        assert result.concepts == expected_concepts

    @pytest.fixture
    def strategy(self):
        return ConceptFractionFilteredByFractionAverageStrategy()


class TestConceptFractionFilteredByFractionAverageMentionsBoostedStrategy:
    @pytest.mark.parametrize(
        ["document_metadata", "expected_concepts"],
        [
            (  # Scenario - A concept (https://www.biofid.de/ontology/2) is pushed, because it is part of the fulltext
                DocumentMetadata(
                    statistics={
                        "count": {
                            "https://www.biofid.de/ontology/2": 2,
                            "https://www.biofid.de/ontology/1": 1,
                            "https://www.biofid.de/ontology/3": 3,
                            "https://www.biofid.de/ontology/4": 4,
                            "https://www.biofid.de/ontology/5": 5,
                        }
                    },
                    text="<sentence id='12345'>Das ist ein annotierter Text.</sentence>"
                    "<sentence>Darin kommt ein "
                    "<em class='animal_fauna' biofid-uri-0='https://www.biofid.de/ontology/2'>Waschbär</em> "
                    "vor.</sentence>",
                ),
                [
                    "https://www.biofid.de/ontology/5",
                    "https://www.biofid.de/ontology/2",
                    "https://www.biofid.de/ontology/4",
                    "https://www.biofid.de/ontology/3",
                ],
            ),
        ],
    )
    def test_evaluate(
        self,
        document_metadata: DocumentMetadata,
        strategy: Strategy,
        expected_concepts: list,
    ):
        result = strategy.parse(document_metadata)
        assert result.concepts == expected_concepts

    @pytest.fixture
    def strategy(self):
        ConceptFilteredByFractionAverageMentionsBoostedStrategy.MENTIONED_CONCEPT_BOOST = (
            2.0
        )
        return ConceptFilteredByFractionAverageMentionsBoostedStrategy()
