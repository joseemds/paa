#pragma once
#include <iostream>
#include <string>
#include <vector>

enum class Value { UNASSIGNED, FALSE, TRUE };

class Assignment {
public:
  explicit Assignment(int numVars) : assigns(numVars + 1, Value::UNASSIGNED) {}

  void set(int var, Value val) { assigns[var] = val; }

  Value get(int var) const { return assigns[var]; }

  bool isTrue(int var) const { return assigns[var] == Value::TRUE; }

  bool isFalse(int var) const { return assigns[var] == Value::FALSE; }

  bool isUnassigned(int var) const { return assigns[var] == Value::UNASSIGNED; }

  void reset() { std::fill(assigns.begin(), assigns.end(), Value::UNASSIGNED); }

  void print() const {
    for (size_t i = 1; i < assigns.size(); ++i) {
      std::cout << i << "=" << toString(assigns[i]) << " ";
    }
    std::cout << "\n";
  }

private:
  std::vector<Value> assigns;

  static std::string toString(Value v) {
    switch (v) {
    case Value::TRUE:
      return "T";
    case Value::FALSE:
      return "F";
    case Value::UNASSIGNED:
      return "U";
    }
    return "?";
  }
};
