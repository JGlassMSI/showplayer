from waiting import wait
from time import sleep

def sayHello():
    print("This is the function hello!")
    sleep(3)
    print("Ah, what a nice rest")
    return True

print("GO!")
sleep(2)
print("Hey let's wait")
wait(sayHello)
print("And this is the end")

'''
Cuelist Item TriggerWithTimout
Action = function:
    def isSerialAvailable:
        return serial.isAvailable()
    try:
        wait(isSerialAvailable, sleep_seconds=.25)
    except TimeoutExpired as err:
        #Jump to a new place in cue stack
        #Or do any other action??
    else:
        Do next cue as usual
'''