class GreetingService:

    def greet(self, name: str) -> str:
        if not name:
            return "Hello, Guest!"

        return f"Hello, {name}!"