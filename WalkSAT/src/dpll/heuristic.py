from abc import ABC, abstractmethod
from typing import List, Optional

from logic.formula import Formula
from logic.clause import Clause

class DecisionHeuristic(ABC):
    @abstractmethod
    def initialize(self, formula: Formula):
        pass

    @abstractmethod
    def pick_unassigned_variable(self, assignments: List[Optional[bool]]) -> Optional[int]:
        pass

    @abstractmethod
    def handle_conflict(self, conflict_clause: Clause):
        pass


class FirstUnassignedHeuristic(DecisionHeuristic):
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
        for i in range(1, len(self.scores)):
            self.scores[i] *= self.decay_factor

    def handle_conflict(self, conflict_clause: Clause):
        if conflict_clause:
            for literal in conflict_clause.literals:
                self.scores[abs(literal)] += 1.0
            self.conflicts_since_decay += 1
            if self.conflicts_since_decay >= self.decay_period:
                self.decay_scores()
                self.conflicts_since_decay = 0

    def pick_unassigned_variable(self, assignments: List[Optional[bool]]) -> Optional[int]:
        max_score = -1.0
        best_var = None
        for i in range(1, self.num_variables + 1):
            if assignments[i] is None:
                if self.scores[i] > max_score:
                    max_score = self.scores[i]
                    best_var = i
        return best_var
