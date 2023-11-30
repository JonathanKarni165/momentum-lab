import math


def multiply(*numbers):
    res = 1
    for num in numbers:
        res *= int(num)
    return res


def change_vector_direction(vector, direction):
    magnitude = math.sqrt(vector[0]**2 + vector[1]**2)
    ratio = direction[1] / direction[0]
    x = math.sqrt(magnitude**2 / (1 + ratio**2))

    if direction[0] < 0:
        x *= -1

    y = x * ratio

    return (x, y)


def change_vector_magnitude(vector, magnitude):
    ratio = vector[1] / vector[0]
    x = math.sqrt(magnitude**2 / (1 + ratio**2))

    if vector[0] < 0:
        x *= -1
    y = x * ratio
    return [x, y]


v1 = (1, 3)
v2 = (-0.5, -0.8)
print(change_vector_magnitude(v2, 5))
