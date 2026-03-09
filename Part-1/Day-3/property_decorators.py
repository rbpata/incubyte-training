class Person:
    def __init__(self,name,age):
        self._name = name
        self.__age = age

    @property
    def name(self):
        return self._name
    @property   
    def age(self):
        return self.__age
    
    @name.setter
    def name(self, new_name):
        self._name = new_name
    @age.setter
    def age(self, new_age):
        if new_age >= 0:
            self.__age = new_age
        else:
            raise ValueError("Age cannot be negative")

person1 = Person("Ram", 30)

print(person1.name)
print(person1.age)

person1.age = -12