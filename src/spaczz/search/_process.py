"""Module for various text/doc processing functions/classes."""
from typing import Callable, Dict

from rapidfuzz import fuzz
from spacy.tokens import Doc


def map_chars_to_tokens(doc: Doc) -> Dict[int, int]:
    """Maps characters in a `Doc` object to tokens."""
    chars_to_tokens = {}
    for token in doc:
        for i in range(token.idx, token.idx + len(token.text)):
            chars_to_tokens[i] = token.i
    return chars_to_tokens


class FuzzyFuncs:
    """Container class housing fuzzy matching functions.

    Functions are accessible via the classes `get()` method
    by their given key name. All rapidfuzz matching functions
    with default settings are available.

    Attributes:
        _fuzzy_funcs (Dict[str, Callable[[str, str], int]]):
            The available fuzzy matching functions:
            "simple" = `ratio`
            "partial" = `partial_ratio`
            "token_set" = `token_set_ratio`
            "token_sort" = `token_sort_ratio`
            "partial_token_set" = `partial_token_set_ratio`
            "partial_token_sort" = `partial_token_sort_ratio`
            "quick" = `QRatio`
            "weighted" = `WRatio`
            "quick_lev" = `quick_lev_ratio`
    """

    def __init__(self) -> None:
        """Initializes a fuzzyfuncs container."""
        self._fuzzy_funcs: Dict[str, Callable[[str, str], int]] = {
            "simple": fuzz.ratio,
            "partial": fuzz.partial_ratio,
            "token_set": fuzz.token_set_ratio,
            "token_sort": fuzz.token_sort_ratio,
            "partial_token_set": fuzz.partial_token_set_ratio,
            "partial_token_sort": fuzz.partial_token_sort_ratio,
            "quick": fuzz.QRatio,
            "weighted": fuzz.WRatio,
            "quick_lev": fuzz.quick_lev_ratio,
        }

    def get(self, fuzzy_func: str) -> Callable[[str, str], float]:
        """Returns a fuzzy matching function based on it's key name.

        Args:
            fuzzy_func: Key name of the fuzzy matching function.

        Returns:
            A fuzzy matching function.

        Raises:
            ValueError: The fuzzy function was not a valid key name.

        Example:
            >>> import spacy
            >>> from spaczz.search._process import FuzzyFuncs
            >>> ff = FuzzyFuncs()
            >>> simple = ff.get("simple")
            >>> simple("hi", "hi")
            100.0
        """
        try:
            return self._fuzzy_funcs[fuzzy_func]
        except KeyError:
            raise ValueError(
                (
                    f"No fuzzy matching function called: {fuzzy_func}.",
                    "Matching function must be in the following:",
                    f"{list(self._fuzzy_funcs.keys())}",
                )
            )