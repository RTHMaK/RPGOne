from typing import Any, Dict, List

from .word_splitter import word_splitters
from .word_stemmer import word_stemmers
from .word_filter import word_filters
from ...common.params import get_choice_with_default, ConfigurationError


class WordProcessor:
    """
    A WordProcessor handles the splitting of strings into words (with the use of a WordSplitter) as well as any
    desired post-processing (e.g., stemming, filtering, etc.)

    Parameters
    ----------
    word_splitter: str, default="simple"
        The string name of the ``WordSplitter`` of choice (see the options at the bottom of
        ``word_splitter.py``).

    word_filter: str, default="pass_through"
        The name of the ``WordFilter`` to use (see the options at the bottom of
        ``word_filter.py``).

    word_stemmer: str, default="pass_through"
        The name of the ``WordStemmer`` to use (see the options at the bottom of
        ``word_stemmer.py``).
    """
    def __init__(self, params: Dict[str, Any]):
        word_splitter_choice = get_choice_with_default(params, 'word_splitter', list(word_splitters.keys()))
        self.word_splitter = word_splitters[word_splitter_choice]()
        word_filter_choice = get_choice_with_default(params, 'word_filter', list(word_filters.keys()))
        self.word_filter = word_filters[word_filter_choice]()
        word_stemmer_choice = get_choice_with_default(params, 'word_stemmer', list(word_stemmers.keys()))
        self.word_stemmer = word_stemmers[word_stemmer_choice]()
        if len(params.keys()) != 0:
            raise ConfigurationError("You passed unrecognized parameters: " + str(params))

    def get_tokens(self, sentence: str) -> List[str]:
        """
        Does whatever processing is required to convert a string of text into a sequence of tokens.

        At a minimum, this uses a ``WordSplitter`` to split words into text.  It may also do
        stemming or stopword removal, depending on the parameters given to the constructor.
        """
        words = self.word_splitter.split_words(sentence)
        filtered_words = self.word_filter.filter_words(words)
        stemmed_words = [self.word_stemmer.stem_word(word) for word in filtered_words]
        return stemmed_words
