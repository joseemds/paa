#pragma once

#include <vector>

struct Formula {
  int numVariables;
  int numClauses;
  std::vector<std::vector<int>> clauses;
};
