from __future__ import annotations

from typing import List, Tuple
import logging

from parsing.triplet_parser_llm import _parse_response

logger = logging.getLogger(__name__)


def extract_triplets(text: str, max_triplets: int = 10, debug: bool = False) -> List[Tuple[str, str, str]]:
    """Extract and clean triples from ``text``.

    Parameters
    ----------
    text:
        Raw output from the LLM containing triples.
    max_triplets:
        Maximum number of triples to return.
    debug:
        If ``True``, print triples before and after filtering.
    """
    triples = _parse_response(text) or []
    if debug:
        print("[debug] raw:", triples)

    if not triples:
        logger.info("No triplets extracted.")
        return []

    # detect consecutive repetition of the same triple
    repeat_count = 1
    warned = False
    for i in range(1, len(triples)):
        if triples[i] == triples[i - 1]:
            repeat_count += 1
            if repeat_count > 3 and not warned:
                logger.warning("[TripletExtractor] repeated triple: %r", triples[i])
                warned = True
        else:
            repeat_count = 1

    # remove duplicates while preserving order
    unique = list(dict.fromkeys(triples))
    if len(unique) != len(triples):
        logger.info("[TripletExtractor] Duplikate entfernt (%d → %d)", len(triples), len(unique))
    triples = unique

    if len(triples) > max_triplets:
        logger.info("[TripletExtractor] limiting to %d triplets", max_triplets)
        triples = triples[:max_triplets]

    if debug:
        print("[debug] filtered:", triples)

    return triples
