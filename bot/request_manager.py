import random

requests = []


def add_request(user_id, text):

    requests.append({
        "user_id": user_id,
        "text": text
    })


def get_random_request():

    if not requests:
        return None

    return random.choice(requests)