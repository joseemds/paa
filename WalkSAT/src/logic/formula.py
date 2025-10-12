from typing import List, Optional
from clause import Clause
from dataclasses import dataclass

@dataclass
class Formula:
    num_variables: int
    clauses: List[Clause] = []

    def add_clause(self, literals: List[int]) -> None:
        """Add a new clause to the formula."""

        if not all(literal != 0 for literal in literals):
            raise ValueError("Clause literals cannot be zero.")
        self.clauses.append(Clause(literals))

    def is_satisfied(self, assignment: List[Optional[bool]]) -> bool:
        """
        Check if the formula is satisfied under the given assignment.

        Since a formula is a conjunction of clauses, all we ought to do
        is check if all clauses are satisfied under the assignment.
        """

        return all(
            clause.is_satisfied(assignment)
            for clause in self.clauses
        )

    def count_satisfied(self, assignment: List[Optional[bool]]) -> int:
        """Count how many clauses are satisfied under the given assignment."""

        return sum(
            1
            for clause in self.clauses
            if clause.is_satisfied(assignment)
        )

    def get_unsatisfied_clauses(self, assignment: List[Optional[bool]]) -> List[Clause]:
        """Get all clauses that are left unsatisfied under the given assignment."""

        return [
            clause
            for clause in self.clauses
            if not clause.is_satisfied(assignment)
        ]

    @classmethod
    def from_dimacs(cls, filename: str) -> 'Formula':
        """
        Class method that reads a DIMACS file and transforms it into a formula instance.

        This method reads a given text file, which is supposed to be in appropriate
        DIMACS format, reads the formula instance it describes, and outputs a
        Formula object.

        Such files have the following format:
            * Comments starting with the letter `c`, which we ignore.

            * A header, the first useful line, starting with `p cnf`,
              with two numbers following it, the first being the number
              of variables `num_vars`, and the second the number of clauses.
              We only use lists, so we won't worry about the second number.

            * Lines with a number of integers in the range [1, `num_vars`].
              Each line is a clause, a disjunction of the variables each integer represents.
              If the integer is negative, the variable appears negated in the clause.
              Each of those lines is ended by a 0.

              For example, a line `1 2 -4 0` represents the clause `x1 ∨ x2 ∨ ¬x4`.
        """

        formula: Optional[Formula] = None

        with open(filename, 'r') as f:
            for line in f:
                line = line.strip() # Remove any possible trailing whitespace.

                # If it's a comment, skip.
                if line.startswith('c') or not line:
                    continue

                # When the header is found, capture the number of variables and start a Formula object.
                if line.startswith('p cnf'):
                    parts: List[str] = line.split()
                    num_vars: int = int(parts[2])
                    formula = cls(num_vars) # A new formula with `num_vars` variables.
                    continue

                # If the first non-comment line is not the file header, flag an error.
                if formula is None:
                    raise ValueError(f"Error on {filename}:\nFile must have with the `p cnf` header.")

                # Get the line and transform in a list of integers.
                literals: List[int] = list(map(int, line.split()))

                if literals and not all(
                    1 <= abs(lit) <= formula.num_variables
                    for lit in literals
                ):
                    raise ValueError(f"Error on {filename}:\nVariables out of bounds [1, {formula.num_variables}].")

                # Remove the trailing 0.
                if literals[-1] == 0:
                    literals = literals[:-1]

                # Add literals as a clause in the formula.
                formula.add_clause(literals)

        # Safety check
        if formula is None:
            raise ValueError(f"Error on {filename}:\nNo valid SAT Formula found in file.")

        return formula
