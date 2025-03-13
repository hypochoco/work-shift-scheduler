
# runs validation on results.log

import json
from pathlib import Path
from cpinstance import CPInstance

d = []
with open("results.log", "r") as f:
    while (l := f.readline()) is not None:
        try:
            l = json.loads(l)
            d.append((l["Instance"], l["Solution"]))
        except:
            print("warning: error reading file")
            break

for i, s in d:
    input_file = Path("../input/"+i)
    filename = input_file.name
    cpinstanct = CPInstance.load(filename)

    break
