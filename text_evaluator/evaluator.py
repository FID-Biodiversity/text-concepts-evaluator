from typing import List

from text_evaluator.strategy import Strategy, DocumentMetadata


class TextConceptEvaluator:
    """Evaluates the statistics of a given annotated text and extracts the main concepts from these."""

    def __init__(self, strategy: Strategy):
        self.strategy = strategy

    def get_concepts_from_text(self, document_json_metadata: dict) -> List[str]:
        """Evaluates the given document metadata and returns a list of concepts that dominate the given text.
        The evaluation result may vary depending on the given Strategy provided to this object."""
        document_metadata = self.metadata2object(document_json_metadata)
        result = self.strategy.parse(document_metadata)
        return result.concepts

    def metadata2object(self, metadata: dict) -> DocumentMetadata:
        return DocumentMetadata(statistics=metadata['statistics'], text=metadata['fulltext'])
