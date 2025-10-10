#include "utils/CNFParser.h"
#include <core/DPLLSolver.h>
#include <iostream>

int main(int argc, char *argv[]) {
  CNFParser cnfParser;
  Formula f = cnfParser.parse(argv[1]);
  DPLLSolver solver(f);
  std::cout << f.numClauses << "\n";
  std::cout << f.numVariables << "\n";

  std::string out = solver.solve() ? "SAT" : "UNSAT";

  std::cout << "Result: " << out << ";";
}
