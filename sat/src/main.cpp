#include "utils/CNFParser.h"
#include <iostream>

int main(int argc, char *argv[]) {
  CNFParser cnfParser;
  Formula f = cnfParser.parse(argv[1]);
  std::cout << f.numClauses << "\n";
  std::cout << f.numVariables << "\n";
}
