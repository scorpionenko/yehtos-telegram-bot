ratings = {}


def add_rating(user_id, score):

    if user_id not in ratings:
        ratings[user_id] = []

    ratings[user_id].append(score)


def get_average_rating(user_id):

    if user_id not in ratings or len(ratings[user_id]) == 0:
        return 0

    return round(sum(ratings[user_id]) / len(ratings[user_id]), 2)