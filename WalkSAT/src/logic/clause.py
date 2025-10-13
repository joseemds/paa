from typing import List, Optional
from dataclasses import dataclass

@dataclass
class Clause:
    """
    This class represents the clauses and its operations.

    Since the formulas are in CNF, all clauses are disjuction of literals,
    which can be negated. An example would be:
        `x1 ∨ x2 ∨ ¬x4`.

    The representation in code is a list of integers, where each integer
    is the 'index' of the variable that appear on the clause.
    If the number is negative, the variable appears negated.

    The example above would be encoded as:
        `[1, 2, -4]`.
    Whatever index doesn't appear is simply not in the clause.
    """

    literals: List[int]

    def is_satisfied(self, assignment: List[Optional[bool]]) -> bool:
        """
        Check if the clause is satisfied under given assignment.

        The process is quite simple: since any clause is a disjunction of
        literals, if any of them turns out to be true, then the clause is
        true, hence satisfied.
        """

        for literal in self.literals:
            # Extract the variable index.
            var: int = abs(literal)

            # Skip if assignment does not cover the current variable.
            if var >= len(assignment) or assignment[var] is None:
                continue

            # Is any of the literals true? Then early return.
            if (literal > 0 and assignment[var]) or (literal < 0 and not assignment[var]):
                return True

        # No literals are true. We had to check them all.
        return False

    def get_variables(self) -> List[int]:
        """Get all variables mentioned in the clause."""

        return [abs(literal) for literal in self.literals]

    def __len__(self) -> int:
        """Overrides length to reflect the length of the literals list."""
        return len(self.literals)

    def __repr__(self) -> str:
        """Overrides printing form."""

        return "∨".join(
            f"{'¬' if index < 0 else ''}x{abs(index)}"
            for index in self.literals
        )
