import nltk
from nltk.corpus import stopwords
from collections import Counter


# Download NLTK stopwords data (uncomment on first run)
# nltk.download("stopwords")
# Create a set of English stopwords for efficient lookups
stop_words = set(stopwords.words("english"))

# ------------------ Filter Out Garbage Data ------------------ #
def is_garbage(text, min_unique_ratio=0.5, min_word_count=10):
    words = text.strip().lower().split()
    if len(words) < min_word_count:
        return True

    word_counts = Counter(words)
    unique_ratio = len(word_counts) / len(words)

    if unique_ratio < min_unique_ratio:
        return True

    stopword_ratio = sum(1 for w in words if w in stop_words) / len(words)
    if stopword_ratio > 0.85:
        return True

    return False




