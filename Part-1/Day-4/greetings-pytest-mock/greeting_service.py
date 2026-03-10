class GreetingService:
    def __init__(self, user_repository):
        self.user_repository = user_repository

    def get_greeting(self, user_id):
        user = self.user_repository.get_user(user_id)
        if user:
            return f"Hello, {user['name']}!"
        return "Hello, Guest!"
