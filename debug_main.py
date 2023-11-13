import Q_schedule
from functools import partial

def foo():
    print("Foo called")

def bar():
    print("Bar stool")

def drink(number):
    print(f"The Number Is: {number}")

sched = Q_schedule.schedule()

# should be zero
print(f"GTime: {sched.getTime()}")

sched.add(135, partial(drink, 134))
sched.add(90, bar)
sched.add(45, foo)

sched.evalAll()