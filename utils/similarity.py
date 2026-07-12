from math import sqrt


def cosine_similarity(
    vector_a: list[float],
    vector_b: list[float],
) -> float:
    if len(vector_a) != len(vector_b):
        raise ValueError(
            "Les deux vecteurs doivent avoir la même dimension."
        )

    dot_product = sum(
        a * b
        for a, b in zip(vector_a, vector_b)
    )

    norm_a = sqrt(sum(a**2 for a in vector_a))
    norm_b = sqrt(sum(b**2 for b in vector_b))

    if norm_a == 0 or norm_b == 0:
        return 0.0

    return dot_product / (norm_a * norm_b)