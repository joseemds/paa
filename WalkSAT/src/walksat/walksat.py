from logic.clause import Clause
from logic.formula import Formula

from typing import List, Optional, Tuple
import random
import os

class WalkSAT:
    """
    Class to handle the WalkSAT algorithm execution, which solves the satisfiability
    of a formula.

    It is a simple algorithm that can be described in these steps:
        1. Start a random assingment.
        2. If the assignment satisfies the formula, return it.
        3. If not, pick a clause that is unsatisfied by the current assignment,
           flip a variable (which can be random or chosen by a greedy procedure,
           and the decision itself is random).
        4. Go to step 2.

    If no solution is found for "too long", the algorithm may restart with a new
    random assignment.
    """

    def __init__(self, formula: Formula, seed=None):
        self.formula = formula
        # Precompute occurrence lists for performance
        self.occurrence_lists = self._build_occurrence_lists()
        self.seed = seed or int.from_bytes(os.urandom(16), 'big')
        random.seed(self.seed)

    def _build_occurrence_lists(self) -> List[List[int]]:
        """
        Build lists of clauses where each variable appears.

        It outputs a lookup table `occurence`, where, for some
        variable index `i`, `ocurrence[i]` is a list of clause indexes (on the formula)
        where the variable `xi` appear.
        """

        # +1 because variables start at index 1
        occurrence = [[] for _ in range(self.formula.num_variables + 1)]

        for clause_idx, clause in enumerate(self.formula.clauses):
            for literal in clause.literals:
                var = abs(literal)
                occurrence[var].append(clause_idx)

        return occurrence

    def _calculate_break_count(self, variable: int, assignment: List[Optional[bool]]) -> int:
        """
        Calculate how many currently SATISFIED clauses would become UNSATISFIED
        if we flip a particular variable.
        """

        break_count = 0

        # Check all clauses that contain this variable.
        # (Here is where computing the occurrences list is useful!)
        for clause_idx in self.occurrence_lists[variable]:
            clause = self.formula.clauses[clause_idx]

            # If clause is currently satisfied...
            if clause.is_satisfied(assignment):
                # Check if it would become unsatisfied after flip.
                temp_assignment = assignment.copy()
                temp_assignment[variable] = not temp_assignment[variable]

                # If flipping the variable causes the clause to be not satisfied, add to the count.
                if not clause.is_satisfied(temp_assignment):
                    break_count += 1

        return break_count

    def _choose_best_variable(self, clause: 'Clause', assignment: List[Optional[bool]]) -> int:
        """
        Choose variable from clause with minimum break count.

        This is a greedy procedure. It selects the variable with the least break count,
        i.e. the minimum number of unsatisfied clauses under its flipping, and label it
        as the "best variable to flip".

        Effectively, we are greedily selecting the flipping that maximizes the number of
        satisfied clauses.
        """

        best_vars = []
        best_break_count = float('inf')

        for literal in clause.literals:
            variable = abs(literal)
            break_count = self._calculate_break_count(variable, assignment) # How many unsat from the flip?

            # Update (or not) the minimum break count and set the variable as the current best.
            if break_count < best_break_count:
                best_break_count = break_count
                best_vars = [variable]
            elif break_count == best_break_count:
                best_vars.append(variable) # If the minimum didn't change, add as a tie.

        # If there are ties, choose randomly.
        return random.choice(best_vars)

    def solve(self, max_flips: int = 10000, max_restarts: int = 100, 
              noise_prob: float = 0.57) -> Tuple[Optional[List[Optional[bool]]], bool]:
        """
        Solve the satisfiability of a formula using WalkSAT algorithm.

        Parameters:
            - `max_flips`    : The maximum number of flips allowed per restart.
            - `max_restarts` : The maximum number of times the algorithm is allowed a fresh restart.
            - `noise_prob`   : Probability of making a random move (walk) vs a greedy move (best).
                               Defaults to an empirically tested value from the papers.

        Returns:
            Tuple of (assignment, found_solution).
        """

        # Only try as long as can restart.
        for restart in range(max_restarts):
            # Generate random assignment
            assignment: List[Optional[bool]] = [None] * (self.formula.num_variables + 1)
            for i in range(1, self.formula.num_variables + 1):
                assignment[i] = random.choice([True, False])

            # Only flip as long as can flip.
            for flip in range(max_flips):
                # Check if we found a solution.
                if self.formula.is_satisfied(assignment):
                    return assignment, True

                # Get all unsatisfied clauses and pick one randomly.
                unsatisfied_clauses = self.formula.get_unsatisfied_clauses(assignment)
                random_clause = random.choice(unsatisfied_clauses)

                # With probability `noise_prob`, do random walk.
                if random.random() < noise_prob:
                    # Flip a random variable from the unsatisfied clause.
                    random_literal = random.choice(random_clause.literals)
                    var_to_flip = abs(random_literal)
                else:
                    # Greedy step: choose the variable with minimal break count.
                    var_to_flip = self._choose_best_variable(random_clause, assignment)

                # Flip the chosen variable, wether random or greedy.
                assignment[var_to_flip] = not assignment[var_to_flip]

        return None, False

    def solve_with_stats(self, max_flips: int = 10000, max_restarts: int = 100,
                        noise_prob: float = 0.57) -> dict:
        """Solve with detailed statistics, like number of restarts and flips."""

        stats = {
            'solution_found': False,
            'assignment': None,
            'restarts_used': 0,
            'flips_used': 0,
            'final_satisfied': 0
        }

        for restart in range(max_restarts):
            assignment: List[Optional[bool]] = [None] * (self.formula.num_variables + 1)
            for i in range(1, self.formula.num_variables + 1):
                assignment[i] = random.choice([True, False])

            for flip in range(max_flips):
                if self.formula.is_satisfied(assignment):
                    stats.update({
                        'solution_found': True,
                        'assignment': assignment,
                        'restarts_used': restart + 1,
                        'flips_used': flip + 1,
                        'final_satisfied': len(self.formula.clauses)
                    })
                    return stats

                unsatisfied_clauses = self.formula.get_unsatisfied_clauses(assignment)
                random_clause = random.choice(unsatisfied_clauses)

                if random.random() < noise_prob:
                    random_literal = random.choice(random_clause.literals)
                    var_to_flip = abs(random_literal)
                else:
                    var_to_flip = self._choose_best_variable(random_clause, assignment)

                assignment[var_to_flip] = not assignment[var_to_flip]

            stats['restarts_used'] = restart + 1

        stats['final_satisfied'] = self.formula.count_satisfied(assignment)
        return stats
