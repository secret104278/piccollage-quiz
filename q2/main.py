def g(num: int) -> int:
    """
    Let g(N) be the count of numbers that contain a 7 when you write out all the numbers from 1 to N.

    Time: worst/avg: O(logN), best O(1)
    Space: worst/avg: O(logN), best O(1), can be always O(1) if use iterative approach
    """
    assert num >= 0

    length = len(str(num))
    if length == 0:
        return 0

    # 1234567 -> first_digit = 1, remaining_digits = 234567
    first_digit = num // (10 ** (length - 1))
    remaining_digits = num % (10 ** (length - 1))

    if length == 1:
        return 1 if first_digit >= 7 else 0

    res = 10 ** (length - 1) - 9 ** (length - 1)

    if first_digit < 7:
        res *= first_digit
        res += g(remaining_digits)
    elif first_digit == 7:
        res *= first_digit
        res += remaining_digits + 1
    elif first_digit > 7:
        res *= first_digit - 1  # i = 0 ~ first_digit - 1, except i == 7
        res += 10 ** (length - 1)  # i == 7
        res += g(remaining_digits)  # i = first_digit

    return res
