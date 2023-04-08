"""Example use of interpreter inside Python script.

Available functions are made available to the program through the "builtins" parameter.
The pass in `car` object is made available through the $ inside the script.

And will be changed by it.
"""
import random
from ringneck import run


class Car:
    color: str = "unknown"
    doors: int = 0

    def __str__(self):
        return f"A {self.color} car with {self.doors} doors."


program = """
colors=['red', 'green', 'blue']

$.color = choice(colors)
$.doors = randint(2, 5)
"""

car = Car()

print(car)  # Outputs `A unknown car with 0 doors.`

run(program, global_variables=car, builtins={
    'choice': random.choice, 'randint': random.randint})

print(car)  # Outputs line with coor and number of doors changed.
