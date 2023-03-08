import random
import string


def generate_random_key(size: int) -> str:
    """Generates a random key of given size

    Args:
        size: the number of digits the key is to have.

    Returns:
        the generated key
    """
    chars = string.ascii_letters + string.digits + string.punctuation
    return "".join(random.choice(chars) for _ in range(size))
