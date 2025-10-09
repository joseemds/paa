#pragma once

#include "core/Formula.h"
#include <string>
#include <vector>

class CNFParser {
public:
  Formula parse(const std::string &filepath) const;

private:
  std::vector<int> parseClause(const std::string &line) const;

  bool isSkippable(const std::string &line) const;

  void parseHeader(const std::string &line, int &numVars,
                   int &numClauses) const;
};
