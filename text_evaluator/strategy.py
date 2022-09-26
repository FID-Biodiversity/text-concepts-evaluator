import re
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import List, Protocol, Optional


@dataclass
class DocumentMetadata:
    """An messenger class for required document data."""

    statistics: dict
    text: str = ""


@dataclass
class Result:
    """Holds the evaluation result of a Strategy class."""

    concepts: List[str]


class Strategy(Protocol):
    """An interface class for the single evaluation strategies."""

    def parse(self, document_metadata: DocumentMetadata) -> Result:
        """Runs an evaluation based on the given document metadata."""
        ...


class CountStatisticsStrategy(ABC):
    """A base class for all Strategies that rely on the count of URIs in the document."""

    evaluated_statistics_name = "count"


class FractionEvaluationStrategy(CountStatisticsStrategy):
    """A base class that relies on provides routines for evaluating fractional data of a count statistics.
    :param number_of_concepts: The maximum number of concepts returned (default: 10).
    :param min_fraction: A minimum fraction that has to be fulfilled for a term to be a concept.
    """

    def __init__(
        self, number_of_concepts: int = 10, min_fraction: Optional[float] = None
    ):
        self.number_of_concepts = number_of_concepts
        self.min_fraction = min_fraction

    @abstractmethod
    def evaluate_metadata(self, document_metadata: DocumentMetadata) -> dict:
        """Evaluates the given metadata and returns the result as a dict.
        The resulting dict should look like:
            {
                'concept_a': 0.3,
                'concept_b': 0.12,
                ...
            }
        with the key being the concept name and the value the fraction of this concept in the data.
        """
        pass

    def parse(self, document_metadata: DocumentMetadata) -> Result:
        evaluated_concept_statistics = self.evaluate_metadata(document_metadata)
        return self._create_result(evaluated_concept_statistics)

    def _create_result(self, evaluated_concept_statistics: dict) -> Result:
        filtered_concepts = self._filter_concepts(evaluated_concept_statistics)

        sorted_concepts = [
            concept_name
            for concept_name, _ in sorted(
                filtered_concepts.items(), key=lambda item: item[1], reverse=True
            )
        ]

        return Result(concepts=sorted_concepts[: self.number_of_concepts + 1])

    def _filter_concepts(self, evaluated_concept_statistics: dict) -> dict:
        return {
            uri: uri_fraction_in_text
            for uri, uri_fraction_in_text in evaluated_concept_statistics.items()
            if self.min_fraction is None or uri_fraction_in_text >= self.min_fraction
        }


class ConceptFractionInAllWordsStrategy(FractionEvaluationStrategy):
    """Calculates the fraction of each URI considering all words in the fulltext.
    Annotated multi-token words will be considered as a single word!"""

    re_extract_annotated_words = re.compile(r"<em.+>(.+?)</em>")
    re_word_split = re.compile(r"<.*?>|\s")

    def evaluate_metadata(self, document_metadata: DocumentMetadata) -> dict:
        text = document_metadata.text

        # Replace annotated (potentially multi-token) words with a single word
        text = self.re_extract_annotated_words.sub("foo", text, re.DOTALL)

        words = {word for word in self.re_word_split.split(text) if word}
        word_count = len(words)

        return {
            concept_name: count / word_count
            for concept_name, count in document_metadata.statistics[
                self.evaluated_statistics_name
            ].items()
        }


class ConceptFractionInAllConceptsStrategy(ConceptFractionInAllWordsStrategy):
    """Very similar to ConceptFractionInAllWordsStrategy, but only takes into account the numbers of annotations."""

    def evaluate_metadata(self, document_metadata: DocumentMetadata) -> dict:
        annotation_count = sum(
            document_metadata.statistics[self.evaluated_statistics_name].values()
        )

        return {
            concept_name: count / annotation_count
            for concept_name, count in document_metadata.statistics[
                self.evaluated_statistics_name
            ].items()
        }


class ConceptFractionFilteredByFractionAverageStrategy(CountStatisticsStrategy):
    """Calculates the average fraction of all URIs and filters out all concepts that are below that value.
    This approach leads to shorter texts having probably fewer returned concepts than longer texts."""

    def parse(self, document_metadata: DocumentMetadata) -> Result:
        evaluated_concept_statistics = self.evaluate_metadata(document_metadata)

        avg_concept_fraction = self._calculate_concept_fraction_average(
            document_metadata
        )

        if avg_concept_fraction == 0.0:
            return self._create_result()

        filtered_concepts = self._filter_concepts(
            evaluated_concept_statistics, avg_concept_fraction
        )

        return self._create_result(filtered_concepts)

    def evaluate_metadata(self, document_metadata: DocumentMetadata) -> dict:
        return {
            concept_name: count
            for concept_name, count in document_metadata.statistics[
                self.evaluated_statistics_name
            ].items()
        }

    def _calculate_concept_fraction_average(
        self, document_metadata: DocumentMetadata
    ) -> float:
        annotation_count = sum(
            document_metadata.statistics[self.evaluated_statistics_name].values()
        )
        number_of_concepts = len(
            document_metadata.statistics[self.evaluated_statistics_name]
        )

        if number_of_concepts == 0:
            return 0.0

        return annotation_count / number_of_concepts

    def _create_result(
        self,
        evaluated_concept_statistics: dict,
    ) -> Result:
        sorted_concepts = [
            concept_name
            for concept_name, _ in sorted(
                evaluated_concept_statistics.items(),
                key=lambda item: item[1],
                reverse=True,
            )
        ]

        return Result(concepts=sorted_concepts)

    def _filter_concepts(
        self, evaluated_concept_statistics: dict, acceptance_threshold: float
    ) -> dict:
        return {
            concept_name: count
            for concept_name, count in evaluated_concept_statistics.items()
            if count >= acceptance_threshold
        }


class ConceptFilteredByFractionAverageMentionsBoostedStrategy(
    ConceptFractionFilteredByFractionAverageStrategy
):
    """Works like ConceptFractionFilteredByFractionAverageStrategy, but boosts concepts that are specifically
    mentioned in the text."""

    MENTIONED_CONCEPT_BOOST: float = 2.0

    def evaluate_metadata(self, document_metadata: DocumentMetadata) -> dict:
        def concept_value(concept_name: str, concept_count: float) -> float:
            if concept_name in document_metadata.text:
                return pow(concept_count, self.MENTIONED_CONCEPT_BOOST)
            else:
                return concept_count

        return {
            concept_name: concept_value(concept_name, count)
            for concept_name, count in document_metadata.statistics[
                self.evaluated_statistics_name
            ].items()
        }
