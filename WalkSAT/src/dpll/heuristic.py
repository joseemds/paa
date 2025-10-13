from abc import ABC, abstractmethod
from typing import List, Optional

from logic.formula import Formula
from logic.clause import Clause

class DecisionHeuristic(ABC):
    """
    Abstract Base Class for decision heuristics.
    Defines the interface for initializing, picking variables, and handling conflicts.
    """
    @abstractmethod
    def initialize(self, formula: Formula):
        """Called once when the solver starts to set up the heuristic."""
        pass

    @abstractmethod
    def pick_unassigned_variable(self, assignments: List[Optional[bool]]) -> Optional[int]:
        """Selects the next variable to branch on."""
        pass

    @abstractmethod
    def handle_conflict(self, conflict_clause: Clause):
        """Called by the solver when a conflict is detected to update internal state."""
        pass


class FirstUnassignedHeuristic(DecisionHeuristic):
    """
    picks the first unassigned variable in numerical order.
    """
    def __init__(self):
        self.num_variables = 0

    def initialize(self, formula: Formula):
        self.num_variables = formula.num_variables

    def pick_unassigned_variable(self, assignments: List[Optional[bool]]) -> Optional[int]:
        for i in range(1, self.num_variables + 1):
            if assignments[i] is None:
                return i
        return None

    def handle_conflict(self, conflict_clause: Clause):
        pass



class VsidsHeuristic(DecisionHeuristic):
    """
    Variable State Independent Decaying Sum (VSIDS) heuristic.
    """
    def __init__(self, decay_factor: float = 0.95, decay_period: int = 256):
        self.scores: List[float] = []
        self.decay_factor = decay_factor
        self.decay_period = decay_period
        self.conflicts_since_decay = 0
        self.num_variables = 0

    def initialize(self, formula: Formula):
        self.num_variables = formula.num_variables
        self.scores = [0.0] * (self.num_variables + 1)
        for clause in formula.clauses:
            for literal in clause.literals:
                self.scores[abs(literal)] += 1.0
    
    def decay_scores(self):
        """Periodically decay all variable scores."""
        for i in range(1, len(self.scores)):
            self.scores[i] *= self.decay_factor

    def handle_conflict(self, conflict_clause: Clause):
        """
        Bumps scores of variables in the conflict clause and handles decay.
        """
        if conflict_clause:
            for literal in conflict_clause.literals:
                self.scores[abs(literal)] += 1.0
            
            self.conflicts_since_decay += 1
            if self.conflicts_since_decay >= self.decay_period:
                self.decay_scores()
                self.conflicts_since_decay = 0

    def pick_unassigned_variable(self, assignments: List[Optional[bool]]) -> Optional[int]:
        """
        Pick the unassigned variable with the highest activity score.
        """
        max_score = -1.0
        best_var = None
        for i in range(1, self.num_variables + 1):
            if assignments[i] is None:
                if self.scores[i] > max_score:
                    max_score = self.scores[i]
                    best_var = i
        return best_var

