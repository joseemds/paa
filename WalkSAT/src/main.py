import argparse
import os
from benchmark.benchmarks import BenchmarkRunner
from walksat.walksat import WalkSAT
from dpll.dpll import Dpll
from pathlib import Path

SOLVERS = {
    "walksat": WalkSAT,
    "dpll": Dpll
}

def main(solver_class, data_path, seed=None):
    print(f"Running benchmarks using solver: {solver_class.__name__}")

    runner = BenchmarkRunner(solver_class, data_dir=data_path)

    if os.path.isdir(data_path):
        print(f"Detected directory: {data_path}. Running all benchmarks...")
        results = runner.run_all_benchmarks(
            max_flips=5000,
            max_restarts=50,
            noise_prob=0.57,
            seed=seed
        )
    elif os.path.isfile(data_path) and data_path.endswith(".cnf"):
        print(f"Detected CNF file: {data_path}. Running single benchmark...")
        results = [runner.run_benchmark(
            Path(data_path),
            max_flips=5000,
            max_restarts=50,
            noise_prob=0.57,
            seed=seed
        )]
        summary = runner._compute_summary(results)
        runner._save_results(results)
        runner._print_summary(summary)

    else:
        raise ValueError(f"Invalid data path: {data_path}. Must be a directory or .cnf file.")

    print("Benchmarking complete.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run methods benchmarks.")

    parser.add_argument(
        "data",
        nargs="?",
        default="data/uf20-91",
        help="Dataset directory or CNF file to be used in tests"
    )
    parser.add_argument(
        "solver",
        choices=SOLVERS.keys(),
        nargs="?",
        default="walksat",
        help="Solver to use (default: walksat)"
    ) 

    parser.add_argument(
        "--seed",
        type=int,
        default=None,
        help="Random seed for reproducibility"
    )


    args = parser.parse_args()
    
    solver_class = SOLVERS[args.solver.lower()]
    
    main(solver_class, args.data, seed=args.seed)
