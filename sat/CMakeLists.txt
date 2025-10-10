cmake_minimum_required(VERSION 3.16)
project(SATSolver LANGUAGES CXX)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_EXPORT_COMPILE_COMMANDS ON)

add_compile_options(-Wall -Wextra -Wpedantic -O2)

list(APPEND CMAKE_MODULE_PATH "${CMAKE_SOURCE_DIR}/cmake")

include_directories(${PROJECT_SOURCE_DIR}/include)

add_executable(millisat src/core/DPLLSolver.cpp src/utils/CNFParser.cpp src/main.cpp)
