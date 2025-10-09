#include "utils/CNFParser.h"
#include <fstream>
#include <iostream>
#include <sstream>
#include <string>
#include <vector>

Formula CNFParser::parse(const std::string &filepath) const {
  std::ifstream file(filepath);
  if (!file.is_open()) {
    // TODO: tratar erro
  }

  Formula formula;
  std::string line;
  bool headerFound = false;

  while (std::getline(file, line)) {
    if (isSkippable(line)) {
      continue;
    }

    if (!headerFound && line.rfind("p ", 0) == 0) {
      headerFound = true;
      parseHeader(line, formula.numClauses, formula.numVariables);
      continue;
    }

    auto clause = parseClause(line);
    if (!clause.empty()) {
      formula.clauses.push_back(clause);
    }
  }

  return formula;
}

std::vector<int> CNFParser::parseClause(const std::string &line) const {
  auto lineStream = std::stringstream(line);
  std::vector<int> out;
  int p;
  while (lineStream >> p) {
    if (p == 0)
      break;
    out.push_back(p);
  }

  return out;
}

void CNFParser::parseHeader(const std::string &line, int &numVars,
                            int &numClauses) const {
  auto lineStream = std::stringstream(line);
  std::string p, cnf;
  lineStream >> p >> cnf >> numVars >> numClauses;
  if (p != "p" || cnf != "cnf") {
    // TODO: error
    std::cout << "Invalid header";
  }
};

bool CNFParser::isSkippable(const std::string &line) const {
  // C -> Comment
  return line.rfind("c", 0) == 0 || line.empty();
}
