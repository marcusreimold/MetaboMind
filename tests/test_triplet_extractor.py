import sys
import os
import logging
import types

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
import triplet_extractor


def test_duplicate_removal(caplog):
    text = str([('du', 'kannst', 'es')] * 13)
    with caplog.at_level(logging.INFO):
        triples = triplet_extractor.extract_triplets(text)
    assert triples == [('du', 'kannst', 'es')]
    assert any('Duplikate entfernt' in m.message for m in caplog.records)


def test_limit_results(caplog):
    data = [ (str(i), 'ist', 'x') for i in range(12) ]
    text = str(data)
    with caplog.at_level(logging.INFO):
        triples = triplet_extractor.extract_triplets(text)
    assert len(triples) == 10
    assert triples == data[:10]
    assert any('limiting to' in m.message for m in caplog.records)


def test_invalid_input(caplog):
    with caplog.at_level(logging.INFO):
        triples = triplet_extractor.extract_triplets('nonsense')
    assert triples == []
    assert any('No triplets extracted' in m.message for m in caplog.records)
