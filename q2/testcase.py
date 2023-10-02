import random

from main import g
from tqdm import tqdm


def ground_truth(n: int) -> int:
    return len([i for i in range(1, n + 1) if "7" in str(i)])


if __name__ == "__main__":
    assert g(0) == 0
    assert g(1) == 0
    assert g(7) == 1
    assert g(20) == 2
    assert g(70) == 8
    assert g(71) == 9
    assert g(100) == 19

    for _ in tqdm(range(1000)):
        n = random.randint(0, 10**5)
        # print(n, g(n), ground_truth(n))
        assert g(n) == ground_truth(n)
