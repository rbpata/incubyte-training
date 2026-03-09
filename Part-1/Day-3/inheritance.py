class Dog:
    def __init__(self,name,sound):
        self.name= name
        self.sound= sound
    def __str__(self):
        return f"Name: {self.name}, Sound: {self.sound}"
    def speak(self):
        return f"{self.name} says {self.sound}"
    @classmethod
    def dog_info(cls):
        return "Dogs are loyal and friendly animals."
    @staticmethod
    def dog_breed_info():
        return "There are many dog breeds, each with unique characteristics."

    
class JackRussellTerrier(Dog):
    def __init__(self,name,sound,breed):
        super().__init__(name,sound)
        self.breed= breed
    def __str__(self):
        return f"Name: {self.name}, Sound: {self.sound}, Breed: {self.breed}"
    

dog1 = JackRussellTerrier("Buddy","Woof","Jack Russell Terrier")
print(dog1.dog_info())
print(dog1.dog_breed_info())