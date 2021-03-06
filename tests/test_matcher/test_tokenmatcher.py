"""Tests for tokenmatcher module."""
from typing import List, Tuple

import pytest
from spacy.language import Language
from spacy.tokens import Doc, Span

from spaczz.matcher import TokenMatcher


def add_name_ent(
    matcher: TokenMatcher, doc: Doc, i: int, matches: List[Tuple[str, int, int, None]]
) -> None:
    """Callback on match function. Adds "NAME" entities to doc."""
    _match_id, start, end, _ = matches[i]
    entity = Span(doc, start, end, label="NAME")
    doc.ents += (entity,)


@pytest.fixture
def matcher(model: Language) -> TokenMatcher:
    """It returns a token matcher."""
    matcher = TokenMatcher(vocab=model.vocab)
    matcher.add(
        "DATA",
        [
            [
                {"TEXT": "SQL"},
                {"LOWER": {"FREGEX": "(database){s<=1}"}},
                {"LOWER": {"FUZZY": "access"}, "POS": "NOUN"},
            ],
            [{"TEXT": {"FUZZY": "Sequel"}}, {"LOWER": "db"}],
        ],
    )
    matcher.add("NAME", [[{"TEXT": {"FUZZY": "Garfield"}}]])
    return matcher


@pytest.fixture
def example(model: Language) -> Doc:
    """Example doc for search."""
    return model(
        """The manager gave me SQL databesE acess so now I can acces the Sequal DB.
        My manager's name is Grfield.
        """
    )


def test_adding_patterns(matcher: TokenMatcher) -> None:
    """It adds the "TEST" label and some patterns to the matcher."""
    assert matcher.patterns == [
        {
            "label": "DATA",
            "pattern": [
                {"TEXT": "SQL"},
                {"LOWER": {"FREGEX": "(database){s<=1}"}},
                {"LOWER": {"FUZZY": "access"}, "POS": "NOUN"},
            ],
            "type": "token",
        },
        {
            "label": "DATA",
            "pattern": [{"TEXT": {"FUZZY": "Sequel"}}, {"LOWER": "db"}],
            "type": "token",
        },
        {
            "label": "NAME",
            "pattern": [{"TEXT": {"FUZZY": "Garfield"}}],
            "type": "token",
        },
    ]


def test_add_without_sequence_of_patterns_raises_error(matcher: TokenMatcher,) -> None:
    """Trying to add non-sequences of patterns raises a TypeError."""
    with pytest.raises(TypeError):
        matcher.add("TEST", [{"TEXT": "error"}])


def test_add_with_zero_len_pattern(matcher: TokenMatcher) -> None:
    """Trying to add zero-length patterns raises a ValueError."""
    with pytest.raises(ValueError):
        matcher.add("TEST", [[]])


def test_len_returns_count_of_labels_in_matcher(matcher: TokenMatcher,) -> None:
    """It returns the sum of unique labels in the matcher."""
    assert len(matcher) == 2


def test_in_returns_bool_of_label_in_matcher(matcher: TokenMatcher,) -> None:
    """It returns whether a label is in the matcher."""
    assert "DATA" in matcher


def test_labels_returns_label_names(matcher: TokenMatcher) -> None:
    """It returns a tuple of all unique label names."""
    assert all(label in matcher.labels for label in ("DATA", "NAME"))


def test_vocab_prop_returns_vocab(matcher: TokenMatcher, model: Language) -> None:
    """It returns the vocab it was initialized with."""
    assert matcher.vocab == model.vocab


def test_remove_label(matcher: TokenMatcher) -> None:
    """It removes a label from the matcher."""
    matcher.add("TEST", [[{"TEXT": "test"}]])
    assert "TEST" in matcher
    matcher.remove("TEST")
    assert "TEST" not in matcher


def test_remove_label_raises_error_if_label_not_in_matcher(
    matcher: TokenMatcher,
) -> None:
    """It raises a ValueError if trying to remove a label not present."""
    with pytest.raises(ValueError):
        matcher.remove("TEST")


def test_matcher_returns_matches(matcher: TokenMatcher, example: Doc) -> None:
    """Calling the matcher on a `Doc` object returns matches."""
    assert matcher(example) == [
        ("DATA", 4, 7, None),
        ("DATA", 13, 15, None),
        ("NAME", 22, 23, None),
    ]


def test_matcher_returns_empty_list_if_no_matches(nlp: Language) -> None:
    """Calling the matcher on a `Doc` object with no matches returns empty list."""
    matcher = TokenMatcher(nlp.vocab)
    matcher.add("TEST", [[{"TEXT": {"FUZZY": "blah"}}]])
    doc = nlp("No matches here.")
    assert matcher(doc) == []


def test_matcher_warns_if_unknown_pattern_elements(nlp: Language) -> None:
    """Calling the matcher on a `Doc` object with no matches returns empty list."""
    matcher = TokenMatcher(nlp.vocab)
    matcher.add("TEST", [[{"TEXT": {"fuzzy": "test"}}]])
    doc = nlp("test")
    with pytest.warns(UserWarning):
        matcher(doc)


def test_matcher_uses_on_match_callback(matcher: TokenMatcher, example: Doc) -> None:
    """It utilizes callback on match functions passed when called on a Doc object."""
    matcher(example)
    ent_text = [ent.text for ent in example.ents]
    assert "Grfield" in ent_text


def test_matcher_pipe(nlp: Language) -> None:
    """It returns a stream of Doc objects."""
    doc_stream = (
        nlp("test doc 1: Corvold"),
        nlp("test doc 2: Prosh"),
    )
    matcher = TokenMatcher(nlp.vocab)
    output = matcher.pipe(doc_stream)
    assert list(output) == list(doc_stream)


def test_matcher_pipe_with_context(nlp: Language) -> None:
    """It returns a stream of Doc objects as tuples with context."""
    doc_stream = (
        (nlp("test doc 1: Corvold"), "Jund"),
        (nlp("test doc 2: Prosh"), "Jund"),
    )
    matcher = TokenMatcher(nlp.vocab)
    output = matcher.pipe(doc_stream, as_tuples=True)
    assert list(output) == list(doc_stream)


def test_matcher_pipe_with_matches(nlp: Language) -> None:
    """It returns a stream of Doc objects and matches as tuples."""
    doc_stream = (
        nlp("test doc 1: Corvold"),
        nlp("test doc 2: Prosh"),
    )
    matcher = TokenMatcher(nlp.vocab)
    matcher.add(
        "DRAGON", [[{"TEXT": {"FUZZY": "Korvold"}}], [{"TEXT": {"FUZZY": "Prossh"}}]]
    )
    output = matcher.pipe(doc_stream, return_matches=True)
    matches = [entry[1] for entry in output]
    assert matches == [[("DRAGON", 4, 5, None)], [("DRAGON", 4, 5, None)]]


def test_matcher_pipe_with_matches_and_context(nlp: Language) -> None:
    """It returns a stream of Doc objects and matches and context as tuples."""
    doc_stream = (
        (nlp("test doc 1: Corvold"), "Jund"),
        (nlp("test doc 2: Prosh"), "Jund"),
    )
    matcher = TokenMatcher(nlp.vocab)
    matcher.add(
        "DRAGON", [[{"TEXT": {"FUZZY": "Korvold"}}], [{"TEXT": {"FUZZY": "Prossh"}}]]
    )
    output = matcher.pipe(doc_stream, return_matches=True, as_tuples=True)
    matches = [(entry[0][1], entry[1]) for entry in output]
    assert matches == [
        ([("DRAGON", 4, 5, None)], "Jund"),
        ([("DRAGON", 4, 5, None)], "Jund"),
    ]
