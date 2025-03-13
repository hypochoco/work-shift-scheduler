
# runs validation on results.log

import json
from cpinstance import CPInstance

d = []
with open("results.log", "r") as f:
    while (l := f.readline()) is not None:
        try:
            l = json.loads(l)
            d.append((l["Instance"], l["Solution"]))
        except:
            print("warning: error reading file")
            break # NOTE: end of file
for i, s in d:
    cpi = CPInstance.load("input/"+i)
    valid = True
    note = ""

    raw = s.split(" ")
    for _ in range(cpi.n_days):
        for _ in range(cpi.n_employees):
            
            # 

    # respect shifts -> off shift, 0-8, 8-16, 16-24
    # minDemandDayShift[day][shift] -> number of employees on day shift
    # minDailyOperation -> min hours daily
    # training requirement
    # no more than 8 hours, no less than 4 hours
    # at most 40 per week, no less than 20 per week
    # total night shifts
    # consecutive night shifts

    print(f"instance {i}: {"valid" if valid else "invalid " + note}")