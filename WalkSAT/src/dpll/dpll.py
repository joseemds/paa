from typing import List, Optional
from logic.formula import Formula
from logic.clause import Clause
from .heuristic import DecisionHeuristic, FirstUnassignedHeuristic, VsidsHeuristic
import os

class Dpll:
    def __init__(self, formula: Formula, heuristic: Optional[DecisionHeuristic] = None):
        self.formula = formula
        self.assigns: List[Optional[bool]] = [None] * (formula.num_variables + 1)
        self.conflict_clause: Optional[Clause] = None
        self.seed = int.from_bytes(os.urandom(16), 'big')

        if heuristic is None:
            self.heuristic = VsidsHeuristic()
        else:
            self.heuristic = heuristic
        
        self.heuristic.initialize(self.formula)

    def propagate(self) -> bool:
        """
        Performs unit propagation. Returns False if a conflict is found.
        Stores the conflict clause when one is found.
        """
        self.conflict_clause = None
        changed = True
        while changed:
            changed = False
            for clause in self.formula.clauses:
                if clause.is_satisfied(self.assigns):
                    continue

                unassigned = [lit for lit in clause.literals if self.assigns[abs(lit)] is None]
                
                is_falsified = all(
                    (lit > 0 and self.assigns[abs(lit)] is False) or 
                    (lit < 0 and self.assigns[abs(lit)] is True)
                    for lit in clause.literals if self.assigns[abs(lit)] is not None
                )

                if not unassigned and is_falsified:
                    self.conflict_clause = clause
                    return False

                if len(unassigned) == 1:
                    literal = unassigned[0]
                    var = abs(literal)
                    if self.assigns[var] is None:
                        value = literal > 0
                        self.assigns[var] = value
                        changed = True
        return True

    def pick_unassigned(self) -> Optional[int]:
        """
        Delegates the choice of the next variable to the heuristic strategy.
        """
        return self.heuristic.pick_unassigned_variable(self.assigns)

    def dpll(self) -> bool:
        if not self.propagate():
            self.heuristic.handle_conflict(self.conflict_clause)
            return False

        if all(a is not None for a in self.assigns[1:]):
            return self.formula.is_satisfied(self.assigns)

        var = self.pick_unassigned()
        if var is None:
            return self.formula.is_satisfied(self.assigns)

        saved_assigns = self.assigns.copy()

        self.assigns[var] = True
        if self.dpll():
            return True

        self.assigns = saved_assigns.copy()
        self.heuristic.handle_conflict(self.conflict_clause)

        self.assigns[var] = False
        if self.dpll():
            return True

        self.assigns = saved_assigns
        self.heuristic.handle_conflict(self.conflict_clause)
        
        return False

    def solve(self) -> bool:
        return self.dpll()

    def solve_with_stats(self, *args, **kwargs) -> dict:
        result = self.solve()
        stats = {
            'solution_found': result,
            'assignment': self.assigns if result else None,
            'restarts_used': 0,
            'flips_used': 0,
            'final_satisfied': int(result)
        }
        return stats
