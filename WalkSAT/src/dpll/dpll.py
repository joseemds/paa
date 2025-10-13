from typing import List, Optional
from logic.formula import Formula

class DPLL:
    def __init__(self, formula: Formula):
        self.formula = formula
        self.assigns: List[Optional[bool]] = [None] * (formula.num_variables + 1)

    def propagate(self) -> bool:
        """
        Perform unit propagation.
        Return False if a conflict is found, True otherwise.
        """
        changed = True
        while changed:
            changed = False
            for clause in self.formula.clauses:
                if clause.is_satisfied(self.assigns):
                    continue

                unassigned = [lit for lit in clause.literals if self.assigns[abs(lit)] is None]

                if not unassigned:
                    return False

                if len(unassigned) == 1:
                    literal = unassigned[0]
                    var = abs(literal)
                    value = literal > 0
                    self.assigns[var] = value
                    changed = True
        return True

    def pick_unassigned(self) -> Optional[int]:
        for i in range(1, self.formula.num_variables + 1):
            if self.assigns[i] is None:
                return i
        return None

    def dpll(self) -> bool:
        if not self.propagate():
            return False

        if all(a is not None for a in self.assigns[1:]):
            return self.formula.is_satisfied(self.assigns)

        var = self.pick_unassigned()
        if var is None:
            return self.formula.is_satisfied(self.assigns)

        self.assigns[var] = True
        if self.dpll():
            return True

        self.assigns[var] = False
        if self.dpll():
            return True

        self.assigns[var] = None
        return False

    def solve(self) -> bool:
        return self.dpll()
