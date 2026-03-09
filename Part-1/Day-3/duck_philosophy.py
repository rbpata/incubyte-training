class Dog:
    def __init__(self, name):
        self.name = name

    def speak(self):
        return "Woof!"

class Cat:
    def __init__(self, name):
        self.name = name

    def speak(self):
        return "Meow!"

def make_sound(animal):
    return animal.speak()

dog = Dog("Buddy")
cat = Cat("Whiskers")

print(make_sound(dog))  # Output: Woof!
print(make_sound(cat))  # Output: Meow!