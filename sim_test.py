from src import _mock_embed, compute_similarity

pairs = [
    ("I love programming in Python.", "Coding in Python is my passion."),
    ("The cat sat on the mat.", "A dog barked loudly at the mailman."),
    ("Artificial intelligence is the future.", "Machine learning shapes tomorrow."),
    ("I want to eat pizza tonight.", "The weather is very nice today."),
    ("Water boils at 100 degrees Celsius.", "H2O becomes gas at 100C.")
]

for i, (a, b) in enumerate(pairs, 1):
    vec_a = _mock_embed(a)
    vec_b = _mock_embed(b)
    score = compute_similarity(vec_a, vec_b)
    print(f"Pair {i}: {score:.4f}")
