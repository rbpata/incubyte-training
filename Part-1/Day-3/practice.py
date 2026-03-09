class Person:
    def __init__(self,name,age,gender):
        self.name= name
        self.age= age
        self.gender= gender
    
    def __str__(self):
        return f"Name: {self.name}, Age: {self.age}, Gender: {self.gender}"
    
    def __repr__(self):
        return f"Person(name='{self.name}', age={self.age}, gender='{self.gender}')"


person1 = Person("Ram",22,"male")
print(person1)
print(repr(person1))

print(isinstance(person1, Person))  


class Car:
    def __init__(self,make,model,year):
        self.make= make
        self.model= model
        self.year= year
    
    def __str__(self):
        return f"Make: {self.make}, Model: {self.model}, Year: {self.year}"
    
    def __repr__(self):
        return f"Car(make='{self.make}', model='{self.model}', year={self.year})"
    
    

