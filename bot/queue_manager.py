import random

support_queue = []


def add_request(user_id, text):
    support_queue.append({
        "user_id": user_id,
        "text": text
    })


def get_request():
    if support_queue:
        return support_queue.pop(0)
    return None


# НОВА ФУНКЦІЯ
def get_random_request():

    if not support_queue:
        return None

    return random.choice(support_queue)