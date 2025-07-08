from parsing import triplet_parser_llm


def test_parse_newline_brackets():
    content = (
        "[Es, bedeutet, ständig neue Informationen zu integrieren]\n"
        "[Es, bedeutet, bestehende Verknüpfungen zu überdenken]\n"
        "[Es, bedeutet, durch Reflexion und Anpassung an neue Herausforderungen zu wachsen]"
    )
    triples = triplet_parser_llm._parse_response(content)
    assert triples == [
        ("Es", "bedeutet", "ständig neue Informationen zu integrieren"),
        ("Es", "bedeutet", "bestehende Verknüpfungen zu überdenken"),
        ("Es", "bedeutet", "durch Reflexion und Anpassung an neue Herausforderungen zu wachsen"),
    ]
