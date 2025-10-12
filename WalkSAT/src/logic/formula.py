from typing import List, Optional, Dict
from clause import Clause

class Formula:
    def __init__(self, num_variables: int) -> None:
        self.num_variables: int = num_variables
        self.clauses: List[Clause]

    def add_clause(self, literals: List[int]) -> None:
        """Add """
