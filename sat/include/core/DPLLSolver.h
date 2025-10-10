#include "core/Formula.h"
#include "core/Solver.h"

class DPLLSolver {
public:
  DPLLSolver(const Formula &formula);
  bool solve();

private:
  Formula formula;
  std::vector<int> assigns;
  std::vector<int> trail;
  std::vector<int> decisionLevel;
  bool propagate();
  int pickUnassigned();
  bool DPLL();
};
