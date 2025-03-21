from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

import numpy as np
from docplex.cp.config import * 
from docplex.cp.model import *
from cpinstance import CPInstance
# silence logs
context.set_attribute("log_output", None)



def sudoku_example():
    def get_box(grid, i):
    #get the i'th box
        box_row = (i // 3) * 3
        box_col = (i % 3) * 3
        box = []
        for row in range(box_row, box_row + 3):
            for col in range(box_col, box_col + 3):
                box.append(grid[row][col])
        return box

    model = CpoModel()
    int_vars = np.array([np.array([integer_var(1,9) for j in range(0,9)]) for i in range(0,9)])
    #Columns are different
    for row in int_vars:
        model.add(all_diff(row.tolist()))
    #Rows are different
    for col_index in range(0,9):
        model.add(all_diff(int_vars[:,col_index].tolist()))
    
    for box in range(0,9):
        model.add(all_diff(get_box(int_vars,box)))
    sol = model.solve()
    if not sol.is_solution():
        print("ERROR")
    else:
        
        for i in range(0,9):
            for j in range(0,9):
                print(sol[int_vars[i,j]],end=" ")
            print()
    

def solveAustraliaBinary_example():
    Colors = ["red", "green", "blue"]
    try: 
        cp = CpoModel() 
        
        WesternAustralia =  integer_var(0,3)
        NorthernTerritory = integer_var(0,3)
        SouthAustralia = integer_var(0,3)
        Queensland = integer_var(0,3)
        NewSouthWales = integer_var(0,3)
        Victoria = integer_var(0,3)
        
        cp.add(WesternAustralia != NorthernTerritory)
        cp.add(WesternAustralia != SouthAustralia)
        cp.add(NorthernTerritory != SouthAustralia)
        cp.add(NorthernTerritory != Queensland)
        cp.add(SouthAustralia != Queensland)
        cp.add(SouthAustralia != NewSouthWales)
        cp.add(SouthAustralia != Victoria)
        cp.add(Queensland != NewSouthWales)
        cp.add(NewSouthWales != Victoria)

        params = CpoParameters(
            Workers = 1,
            TimeLimit = 300,
            SearchType="DepthFirst" 
        )
        cp.set_parameters(params)
        
        sol = cp.solve() 
        if sol.is_solution(): 
            
            print( "\nWesternAustralia:    " + Colors[sol[WesternAustralia]])
            print( "NorthernTerritory:   " +   Colors[sol[NorthernTerritory]])
            print( "SouthAustralia:      " +   Colors[sol[SouthAustralia]])
            print( "Queensland:          " +   Colors[sol[Queensland]])
            print( "NewSouthWales:       " +   Colors[sol[NewSouthWales]])
            print( "Victoria:            " +   Colors[sol[Victoria]])
        else:
            print("No Solution found!");
        
    except Exception as e:
        print(f"Error: {e}")




# [Employee][Days][startTime][EndTime]
Schedule = list[list[tuple[int, int]]]


@dataclass
class Solution:
    is_solution: bool #Is this a solution
    n_fails: int # Number of failures reported by the model
    schedule: Optional[Schedule] #The Employee Schedule. Should not be None if is_solution is true


class Scheduler:
    OFF_SHIFT = 0
    NIGHT_SHIFT = 1

    def __init__(self, config: CPInstance):
        self.config = config
        self.model = CpoModel()
        self.build_constraints()

    def build_constraints(self):
        
        # build representation
            # [day][employee](shift, hours on shift)
        self.rep = []
        for i in range(self.config.n_days):
            day = []
            for _ in range(self.config.n_employees):
                s, h = integer_var(0, self.config.n_shifts-1), integer_var(self.config.employee_min_daily, self.config.employee_max_daily)
                day.append((s,h))
            self.rep.append(day)

            # constraint -- min daily, min shifts
            self.model.add( sum_of(x[1]*min(x[0], 1) for x in day) >= self.config.min_daily )
            for j in range(1, self.config.n_shifts):
                self.model.add( count([x[0] for x in day], j) >= self.config.min_shifts[i][j] )
        
        # constraint -- training, max total night shift, ...
        for i in range(self.config.n_employees):
            t_rep = [u[i] for u in self.rep[:4]]
            n_rep = [u[i] for u in self.rep]
            self.model.add( all_diff([x[0] for x in t_rep]) )
            self.model.add( count([x[0] for x in n_rep], self.NIGHT_SHIFT) <= self.config.employee_max_total_night_shifts )
            for j in range(0, self.config.n_days, self.config.employee_max_consecutive_night_shifts): # consec night shift
                s_rep = [v[i] for v in self.rep[j:j+self.config.employee_max_consecutive_night_shifts]]
                if len(s_rep) == 0: continue
                self.model.add( (count([y[0] for y in s_rep], self.NIGHT_SHIFT) <= self.config.employee_max_consecutive_night_shifts) )
            for j in range(0, self.config.n_days, self.config.n_days_in_week): # weekly hours min/max
                w_rep = [v[i] for v in self.rep[j:j+self.config.n_days_in_week]]
                self.model.add( sum_of(y[1]*min(y[0],1) for y in w_rep) <= self.config.employee_max_weekly )
                self.model.add( sum_of(y[1]*min(y[0],1) for y in w_rep) >= self.config.employee_min_weekly )
        
    def solve(self) -> Solution:
        params = CpoParameters(
            Workers = 1,
            TimeLimit = 300,
            #Do not change the above values 
            SearchType="DepthFirst" # Uncomment for part 2
            # LogVerbosity = "Verbose"
        )
        self.model.set_parameters(params)    

        # value selector / chooser

        # # test01 
        # flat_var = [e for m in self.rep for r in m for e in r]
        # self.model.set_search_phases([search_phase(flat_var)])

        # test 02
        var_sel = [select_smallest(self.model.domain_size()), select_random_var()]
        val_sel = select_largest(self.model.value())
        flat_var = [e for m in self.rep for r in m for e in r]
        minDomainMax = search_phase(flat_var, var_sel, val_sel)
        self.model.set_search_phases([minDomainMax])

        # # test 03
        # var_sel = [select_smallest(self.model.domain_size()), select_random_var()]
        # val_sel_smallest = select_smallest(self.model.value())
        # flat_var = [e for m in self.rep for r in m for e in r]
        # minDomainMin = search_phase(flat_var, var_sel, val_sel_smallest)
        # self.model.set_search_phases([minDomainMin])

        # # test 04, 05, 06
        # flat_var_d = [r[0] for m in self.rep for r in m]
        # flat_var_h = [r[1] for m in self.rep for r in m]
        # minDomainMax_d = search_phase(flat_var_d, [select_smallest(self.model.domain_size())], select_largest(self.model.value()))
        # minDomainMax_h = search_phase(flat_var_h, [select_smallest(self.model.domain_size())], select_largest(self.model.value()))
        # self.model.set_search_phases([minDomainMax_d, minDomainMax_h])

        # # test 07 -> maxDomainMin
        # var_sel = [select_largest(self.model.domain_size()), select_random_var()]
        # val_sel = select_smallest(self.model.value())
        # flat_var = [e for m in self.rep for r in m for e in r]
        # maxDomainMin = search_phase(flat_var, var_sel, val_sel)
        # self.model.set_search_phases([maxDomainMin])

        # # test 08
        # var_sel = [select_largest(self.model.domain_size()), select_random_var()]
        # val_sel = select_largest(self.model.value())
        # flat_var = [e for m in self.rep for r in m for e in r]
        # maxDomainMax = search_phase(flat_var, var_sel, val_sel)
        # self.model.set_search_phases([maxDomainMax])



        


        solution = self.model.solve()
        n_fails = solution.get_solver_info(CpoSolverInfos.NUMBER_OF_FAILS)
        if not solution.is_solution():
            return Solution(False, n_fails, None)
        else:
            schedule = self.construct_schedule(solution)
            return Solution(True, n_fails, schedule)

    def construct_schedule(self, solution: CpoSolveResult) -> Schedule:
        """Convert the solution as reported by the model
        to an employee schedule (see handout) that can be returned

        Args:
            solution (CpoSolveResult): The solution as returned by the model

        Returns:
            Schedule: An output schedule that can returned
            NOTE: Schedule must be in format [Employee][Days][startTime][EndTime]
        """

        r = []
        st = [ 24*x//3 for x in range(3) ]
        for i in range(self.config.n_employees):
            rr = []
            for j in range(self.config.n_days):
                s, h = self.rep[j][i]
                s, h = solution[s], solution[h]
                if s == 0: rr.append((-1, -1))
                else: rr.append((st[s-1], st[s-1]+h))
            r.append(rr)
        return r

    @staticmethod
    def from_file(f) -> Scheduler:
        # Create a scheduler instance from a config file
        config = CPInstance.load(f)
        return Scheduler(config)

'''
   * Generate Visualizer Input
   * author: Adapted from code written by Lily Mayo
   *
   * Generates an input solution file for the visualizer. 
   * The file name is numDays_numEmployees_sol.txt
   * The file will be overwritten if it already exists.
   * 
   * @param numEmployees the number of employees
   * @param numDays the number of days
   * @param beginED int[e][d] the hour employee e begins work on day d, -1 if not working
   * @param endED   int[e][d] the hour employee e ends work on day d, -1 if not working
   '''
def generateVisualizerInput(numEmployees : int, numDays :int,  sched : Schedule ):
    solString = f"{numDays} {numEmployees}\n"

    for d in range(0,numDays):
        for e in range(0,numEmployees):
            solString += f"{sched[e][d][0]} {sched[e][d][1]}\n"

    fileName = f"{str(numDays)}_{str(numEmployees)}_sol.txt"

    try:
        with open(fileName,"w") as fl:
            fl.write(solString)
        fl.close()
    except IOError as e:
        print(f"An error occured: {e}")
        

