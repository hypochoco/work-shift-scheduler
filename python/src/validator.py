
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
            break # NOTE: end of file
for n, s in d:
    cpi = CPInstance.load("input/"+n)
    valid = True
    note = ""

    st = [ 24*x//3 for x in range(3) ]
    def to_shift(a,b): # convert hour into shift index
        if b>24 or b<a: return -1
        if b == -1 and a == -1: return 0
        for i in range(len(st)):
            if st[i] <= a and a <= st[i]+8 and st[i] <= b and b <= st[i]+8: return i+1
        return -1
    
    schedule = [] # [day][employee][shift,hours]
    raw = list(map(int,s.split(" ")))
    for i in range(cpi.n_days):
        day = []
        for j in range(cpi.n_employees):
            a,b = raw[2*(j*cpi.n_days+i):2*(j*cpi.n_days+i+1)]
            u = to_shift(a,b)
            # respect shifts -> off shift, 0-8, 8-16, 16-24
            if u == -1: valid = False; note = "invalid start and end times"
            # no more than 8 hours, no less than 4 hours
            if u!= 0 and b-a < cpi.employee_min_daily or b-a > cpi.employee_max_daily: valid = False; note = "invalid work interval"
            day.append((u, b-a))
        # minDemandDayShift[day][shift] -> number of employees on day shift
        for j in range(1,cpi.n_shifts):
            if len([0 for x in day if x[0] == j]) < cpi.min_shifts[i][j]: valid = False; note = "invalid min shifts"
        # minDailyOperation -> min hours daily
        if sum(x[1] for x in day) < cpi.min_daily: valid = False; note = "invalid min daily"
        schedule.append(day)
    if not valid: print(f"instance {n} invalid, {note}"); continue

    for i in range(cpi.n_employees):
        for j in range(0,cpi.n_days,cpi.n_days_in_week):
            w_rep = [x[i] for x in schedule[j:j+cpi.n_days_in_week]]
            wh = sum(x[1] for x in w_rep)
            # at most 40 per week, no less than 20 per week
            if wh < cpi.employee_min_weekly or wh > cpi.employee_max_weekly: valid = False; note = "invalid weekly hours"
        # training requirement
        if len(set([x[i][0] for x in schedule[:4]])) < 4: valid = False; note = "invalid training requirement"
        # total night shifts
        if len([x[i][0] for x in schedule if x[i][0] == 1]) > cpi.employee_max_total_night_shifts: valid = False; note = "invalid max total night shifts"
        # consecutive night shifts
        for j in range(cpi.n_days-cpi.employee_max_consecutive_night_shifts+1):
            if len([x[i][0] for x in schedule[i:i+cpi.employee_max_consecutive_night_shifts] if x[i][0] == 1]) > cpi.employee_max_consecutive_night_shifts: valid = False; note = "invalid consec night shifts"
    if not valid: print(f"instance {n} invalid, {note}"); continue

    print(f"instance {n} valid")
    