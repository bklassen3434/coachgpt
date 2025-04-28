import nltk
from nltk.corpus import stopwords
from collections import Counter
from typing import List


# ------------------ Overview ------------------ #
# This module provides helper functions for text quality analysis and filtering.
# It includes functionality to check word count, word diversity, and stopword density.

# Download NLTK stopwords data (uncomment on first run)
# nltk.download("stopwords")
# Create a set of English stopwords for efficient lookups
stop_words = set(stopwords.words("english"))

# ------------------ Text Quality Analysis ------------------ #
class TextQualityAnalyzer:
    def __init__(self, min_unique_ratio: float = 0.5, min_word_count: int = 10,
                 max_stopword_ratio: float = 0.85):
        self.min_unique_ratio = min_unique_ratio
        self.min_word_count = min_word_count
        self.max_stopword_ratio = max_stopword_ratio

    def _tokenize(self, text: str) -> List[str]:
        """Convert text to lowercase words"""
        return text.strip().lower().split()

    def _check_word_count(self, words: List[str]) -> bool:
        """Check if text meets minimum word count"""
        return len(words) >= self.min_word_count

    def _check_word_diversity(self, words: List[str]) -> bool:
        """Check if text has sufficient unique word ratio"""
        word_counts = Counter(words)
        unique_ratio = len(word_counts) / len(words)
        return unique_ratio >= self.min_unique_ratio

    def _check_stopword_density(self, words: List[str]) -> bool:
        """Check if stopword ratio is acceptable"""
        stopword_ratio = sum(1 for w in words if w in stop_words) / len(words)
        return stopword_ratio <= self.max_stopword_ratio

    def is_garbage(self, text: str) -> bool:
        """
        Determines if text is likely low-quality or meaningless based on several metrics.
        
        This function analyzes text quality by checking:
        1. Text length - ensures minimum meaningful content
        2. Word diversity - detects repetitive or nonsensical content
        3. Stopword density - identifies text with low semantic value
        
        Args:
            text (str): The input text to analyze
            
        Returns:
            bool: True if text appears to be garbage, False if it seems valid
        """
        words = self._tokenize(text)
        
        return not all([
            self._check_word_count(words),
            self._check_word_diversity(words),
            self._check_stopword_density(words)
        ])
