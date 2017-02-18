def fibgen(num):
    """
    Generates Fibonacci numbers

    :param num: how many numbers to generate
    :return: generator of first num Fibonacci numbers

    >>> list(fibgen(10))
    [1, 1, 2, 3, 5, 8, 13, 21, 34, 55]
    """
    if type(num) is not int:
        raise TypeError("type of num argument should be int")
    if num <= 0:
        return
    x1 = 0
    x2 = 1
    i = 1
    yield 1
    while i < num:
        i += 1
        res = x1 + x2
        x1 = x2
        x2 = res
        yield res

if __name__ == "__main__":
    print(list(fibgen(10)))
