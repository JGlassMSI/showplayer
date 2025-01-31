from os import listdir
from datetime import date

for f in [fl for fl in listdir("./logs") if "debug" in fl]:
    if "-" in f:
        date = f.split(".")[-1]
    else:
        date = date.today()
    print(f"\n ===={date}====")
    showRuns = 0
    sawTrigger = False
    
    with open("./logs/" + f, "r") as infile:
        for line in infile:
            if "New Trigger Flag is now True" in line:
                sawTrigger = True
            if "Running cue number 0" in line:
                startTime = line.split(" | ")[0].split(" ")[-1]
                print(f"Show started at {startTime}, ", end = "")
                showRuns += 1

                if sawTrigger:
                    print("started by trigger")
                else:
                    print("started due to schedule")

                sawTrigger = False

    print(f"Total Runs Today: {showRuns}")
                