def multiply(*numbers):
    res = 1
    for num in numbers:
        res *= int(num)
    return res


print(multiply(1, 2, 3))
