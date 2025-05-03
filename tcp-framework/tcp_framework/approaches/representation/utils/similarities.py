def lccss(code1: str, code2: str) -> int:
    """
    Original: https://doi.org/10.1145/3425269.3425283
    """

    common_fixtures = 0
    bound = min(len(code1), len(code2))
    for i in range(bound):
        if code1[i] != code2[i]:
            break
        common_fixtures += 1
    return common_fixtures
