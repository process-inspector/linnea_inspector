import random


def get_random_value(seed):
    random.seed(seed)
    return random.randint(1, 100)