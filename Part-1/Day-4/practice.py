class Shape:
    def __init__(self, name):
        self.name = name

    def area(self):
        pass
    
    


class Circle(Shape):
    def __init__(self, radius):
        super().__init__("Circle")
        self.radius = radius

    def area(self):
        return 3.14 * self.radius**2
