import argparse
from benchmark.benchmarks import BenchmarkRunner
from walksat.walksat import WalkSAT
from dpll.dpll import Dpll

SOLVERS = {
    "walksat": WalkSAT,
    "dpll": Dpll
}

def main(solver_class):
    print(f"Running benchmarks using solver: {solver_class.__name__}")
    runner = BenchmarkRunner(solver_class)
    
    results = runner.run_all_benchmarks(
        max_flips=5000,
        max_restarts=50,
        noise_prob=0.57
    )
    
    print("Benchmarking complete.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run methods benchmarks.")

    parser.add_argument(
        "data",
        nargs="?",
        default="data/uf20-91",
        help="Dataset to be used in tests"
    )
    parser.add_argument(
        "solver",
        choices=SOLVERS.keys(),
        nargs="?",
        default="walksat",
        help="Solver to use (default: walksat)"
    ) 

    args = parser.parse_args()
    
    solver_class = SOLVERS[args.solver.lower()]
    
    main(
        solver_class,
    )
