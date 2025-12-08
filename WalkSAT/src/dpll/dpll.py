from typing import List, Optional
from logic.formula import Formula
from logic.clause import Clause
from .heuristic import DecisionHeuristic, FirstUnassignedHeuristic, VsidsHeuristic
import os

class Dpll:
    def __init__(self, formula: Formula, heuristic: Optional[DecisionHeuristic] = None, seed = None):
        self.formula = formula
        self.assigns: List[Optional[bool]] = [None] * (formula.num_variables + 1)
        self.conflict_clause: Optional[Clause] = None
        self.stats = {}
        self.seed = seed or int.from_bytes(os.urandom(16), 'big')

        if heuristic is None:
            self.heuristic = VsidsHeuristic()
        else:
            self.heuristic = heuristic

        self.heuristic.initialize(self.formula)

    def propagate(self) -> bool:
        self.conflict_clause = None
        changed = True
        while changed:
            changed = False
            for clause in self.formula.clauses:
                satisfied = False
                unassigned_literals = []
                for lit in clause.literals:
                    val = self.assigns[abs(lit)]
                    if val is None:
                        unassigned_literals.append(lit)
                    else:
                        if (lit > 0 and val is True) or (lit < 0 and val is False):
                            satisfied = True
                            break
                if satisfied:
                    continue
                if not unassigned_literals:
                    self.conflict_clause = clause
                    return False
                if len(unassigned_literals) == 1:
                    literal = unassigned_literals[0]
                    var = abs(literal)
                    value = literal > 0
                    if self.assigns[var] is None:
                        self.assigns[var] = value
                        changed = True
        return True

    def pick_unassigned(self) -> Optional[int]:
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
            'final_satisfied': int(result)
        }
        self.stats = stats
        return stats
