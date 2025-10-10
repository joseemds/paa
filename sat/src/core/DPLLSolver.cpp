#include "core/DPLLSolver.h"
#include <math.h>

#define MAX_TRIES 1000

DPLLSolver::DPLLSolver(const Formula &f)
    : formula(f), assigns(f.numVariables + 1, 0) {}

bool DPLLSolver::solve() {
  Formula formula;

  for (int i = 1; i <= this->formula.numVariables; i++) {
    this->assigns[i] = 0;
  }
  bool result = DPLL();

  return result;
}

bool DPLLSolver::propagate() {
  bool changed = true;

  while (changed) {
    changed = false;

    for (int i = 0; i < formula.numClauses; i++) {
      const std::vector<int> &clause = formula.clauses[i];
      bool satisfied = false;
      std::vector<int> unassignedLits;

      for (int lit : clause) {
        int var = abs(lit);
        int val = assigns[var];

        if ((lit > 0 && val == 1) || (lit < 0 && val == -1)) {
          satisfied = true;
          break;
        }

        if (val == 0) {
          unassignedLits.push_back(lit);
        }
      }

      if (satisfied) {
        continue;
      }

      if (unassignedLits.empty()) {
        return false;
      }

      if (unassignedLits.size() == 1) {
        int lit = unassignedLits[0];
        int var = abs(lit);

        if (lit > 0) {
          assigns[var] = 1;
        } else {
          assigns[var] = -1;
        }

        changed = true;
      }
    }
  }

  return true;
}

bool DPLLSolver::DPLL() {
  bool result = propagate();
  if (result == false)
    return false;

  bool allAssigned = true;

  for (int i = 1; i <= this->formula.numVariables; i++) {
    allAssigned = allAssigned && this->assigns[i] != 0;
  }

  if (allAssigned)
    return true;

  int var = pickUnassigned();
  this->assigns[abs(var)] = 1;
  if (DPLL())
    return true;

  this->assigns[abs(var)] = -1;
  if (DPLL())
    return true;

  this->assigns[abs(var)] = 0;
  return false;
}

int DPLLSolver::pickUnassigned() {
  for (int i = 1; i <= this->formula.numVariables; i++) {
    if (this->assigns[i] == 0)
      return i;
  }

  return -1;
}
