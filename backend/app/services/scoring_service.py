def calculate_score(text):
    words = text.split()
    length = len(words)

    grammar_score = 5
    fluency_score = min(10, length // 2)

    if "go yesterday" in text:
        grammar_score -= 2

    return {
        "fluency": fluency_score,
        "grammar": max(1, grammar_score),
        "pronunciation": 7,  # placeholder
        "vocabulary": min(10, len(set(words)))
    }