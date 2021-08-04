import json
from typing import Dict

from src.user import User


def write_data_to_file(data: Dict[str, User]):
    file = open("data.txt", "w")
    for key in data.keys():
        file.write(json.dumps(data[key].__dict__))
        file.write("\n")
    file.close()

def read_data_from_file() -> Dict[str, User]:
    data: Dict[str, User] = {}
    with open("data.txt") as file:
        users: list(User) = list()
        for line in file:
            users.append(json.loads(line, object_hook=lambda d: User(**d)))
            for user in users:
                data[user.username] = user
    return data

