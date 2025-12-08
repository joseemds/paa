from logic.clause import Clause
from logic.formula import Formula

from typing import List, Optional, Tuple
import random
import os

class IteratedLocalSearch:
    """
    Iterated Local Search for MAX-SAT
    Combines local search with perturbation to escape local optima
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

    def _local_search(self,
                      assignment: List[Optional[bool]],
                      max_flips: int = 10000,
                      noise_prob: float = 0.57) -> Tuple[List[Optional[bool]], int]:
        """
        Perform a local search procedure using WalkSAT algorithm, adapted to our context.
        Return the best partial assignment found, with the fitness being the number of clauses satisfied.

        Parameters:
            - `max_flips`    : The maximum number of flips allowed per restart.
            - `max_restarts` : The maximum number of times the algorithm is allowed a fresh restart.
            - `noise_prob`   : Probability of making a random move (walk) vs a greedy move (best).
                               Defaults to an empirically tested value from the papers.

        Returns:
            Tuple of (best_assignment, best_fitness).
        """

        # Initialize
        current_assignment = assignment.copy()
        best_assignment = assignment.copy()
        best_fitness = self.formula.count_satisfied(assignment)

        # Only flip as long as can flip.
        for _ in range(max_flips):
            # If we found a solution that satisfies the formula, we are done.
            if self.formula.is_satisfied(current_assignment):
                return current_assignment, len(self.formula.clauses)

            # Get all unsatisfied clauses and pick one randomly.
            unsatisfied_clauses = self.formula.get_unsatisfied_clauses(current_assignment)
            random_clause = random.choice(unsatisfied_clauses)

            # With probability `noise_prob`, do random walk.
            if random.random() < noise_prob:
                # Flip a random variable from the unsatisfied clause.
                random_literal = random.choice(random_clause.literals)
                var_to_flip = abs(random_literal)
            else:
                # Greedy step: choose the variable with minimal break count.
                var_to_flip = self._choose_best_variable(random_clause, current_assignment)

            # Flip the chosen variable, wether random or greedy.
            current_assignment[var_to_flip] = not current_assignment[var_to_flip]

            # Track best even if not perfect.
            current_fitness = self.formula.count_satisfied(current_assignment)
            if current_fitness > best_fitness:
                best_fitness = current_fitness
                best_assignment = current_assignment.copy()

        return best_assignment, best_fitness

    def _perturbation(self, assignment: List[Optional[bool]], strength: float) -> List[Optional[bool]]:
        """
        Perturb the current solution by flipping multiple variables.

        `strength`: proportion of variables to flip (0.0 to 1.0)
        """

        perturbed = assignment.copy()
        num_flips = max(1, int(self.formula.num_variables * strength))

        variables_to_flip = random.sample(
            range(1, self.formula.num_variables + 1),
            num_flips
        )

        for var in variables_to_flip:
            perturbed[var] = not perturbed[var]

        return perturbed

    def _generate_initial_solution(self) -> List[Optional[bool]]:
        """Generate random initial assignment"""

        assignment: List[Optional[bool]] = [None] * (self.formula.num_variables + 1)
        for i in range(1, self.formula.num_variables + 1):
            assignment[i] = random.choice([True, False])
        return assignment

    def solve(self,
              max_iterations: int = 100,
              local_search_flips: int = 1000,
              perturbation_strength: float = 0.1) -> Tuple[List[Optional[bool]], int, int]:
        """
        Solve MAX-SAT using Iterated Local Search

        Parameters:
        - max_iterations: maximum ILS iterations
        - local_search_flips: maximum flips per local search
        - perturbation_strength: proportion of variables to flip during perturbation

        Returns:
        - Best assignment found and its fitness (number of satisfied clauses)
        """

        # Generate initial solution
        current_solution: List[Optional[bool]] = self._generate_initial_solution()
        current_solution, current_fitness = self._local_search(current_solution, local_search_flips)
        best_solution = current_solution.copy()
        best_fitness = current_fitness
        best_iteration = 1

        print(f"Initial solution: {best_fitness}/{len(self.formula.clauses)} clauses satisfied")

        for iteration in range(max_iterations):
            # Perturbation phase
            perturbed_solution = self._perturbation(current_solution, perturbation_strength)

            # Local search phase
            candidate_solution, candidate_fitness = self._local_search(perturbed_solution, local_search_flips)


            # Update bests if improved the solution, or as per a small probability.
            # Allowing worsening solutions rarely to escape deep local minima.
            if candidate_fitness >= current_fitness or random.random() < 0.001:
                current_solution = candidate_solution
                current_fitness = candidate_fitness

                # Update best solution
                if candidate_fitness > best_fitness:
                    best_solution = candidate_solution.copy()
                    best_fitness = candidate_fitness
                    best_iteration = iteration
                    print(f"Iteration {iteration}: New best fitness = {best_fitness}")

            # Early termination if optimal solution found
            if best_fitness == len(self.formula.clauses):
                print("Optimal solution found!")
                break

        print(f"Final solution: {best_fitness}/{len(self.formula.clauses)} clauses satisfied")
        return best_solution, best_fitness, best_iteration

    def solve_with_stats(self, *args, **kwargs) -> dict:
      assignment, fitness, best_iteration = self.solve()
      return {
       'solution_found': (fitness == len(self.formula.clauses)),
       'assignment': assignment,
       'final_satisfied': fitness,
       'best_iteration': best_iteration
      }

