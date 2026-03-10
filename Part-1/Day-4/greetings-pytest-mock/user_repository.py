class UserRepository:
    def get_user(self, user_id):
        users = {
            1: {"name": "Ram", "age": 30},
            2: {"name": "mihir", "age": 25},
            3: {"name": "sahil", "age": 35},
        }
        return users.get(user_id, None)
