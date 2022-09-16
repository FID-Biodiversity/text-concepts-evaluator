import pytest

from text_evaluator.evaluator import TextConceptEvaluator
from text_evaluator.strategy import Result, DocumentMetadata


class TestTextConceptEvaluator:
    def test_evaluate_text(self, evaluator, document_json_metadata):
        main_concepts = evaluator.get_concepts_from_text(document_json_metadata)
        assert main_concepts == [
            "https://www.biofid.de/ontology/1",
            "https://www.biofid.de/ontology/2",
            "https://www.biofid.de/ontology/3",
        ]

    @pytest.fixture
    def evaluator(self):
        strategy = DummyStrategy()
        return TextConceptEvaluator(strategy)

    @pytest.fixture
    def document_json_metadata(self):
        return {
            "statistics": {
                "count": {
                    "https://www.biofid.de/ontology/1": 2,
                    "https://www.biofid.de/ontology/3": 5,
                    "https://www.biofid.de/ontology/2": 4,
                }
            },
            "fulltext": "No text",
        }


class DummyStrategy:
    def parse(self, document_metadata: DocumentMetadata) -> Result:
        concepts = [
            key
            for key, value in sorted(
                document_metadata.statistics["count"].items(), key=lambda x: x[1]
            )
        ]
        return Result(concepts=concepts)
