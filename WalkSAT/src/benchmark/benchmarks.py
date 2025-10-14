import json
import time
import statistics
from pathlib import Path
from typing import List, Dict, Any, Optional
from datetime import datetime

from logic.formula import Formula
from walksat.walksat import WalkSAT
from dpll.dpll import Dpll


class BenchmarkRunner:
    """
    Class to run benchmarks of the code.

    It simply fetches the instances from the CNF files, pass them to the WalkSAT
    solver and annotate benchmarks, such as execution time, number of flips, etc.

    Saves all results in a file.
    """

    def __init__(self, solver = WalkSAT, data_dir: str = "data/uf20-91", results_dir: str = "results"):
        self.data_dir = Path(data_dir)
        self.results_dir = Path(results_dir)
        self.results_dir.mkdir(exist_ok=True)
        self.solver = solver

    def find_cnf_files(self) -> List[Path]:
        """Find all .cnf files in the data directory."""

        return list(self.data_dir.glob("*.cnf"))

    def run_benchmark(self, cnf_file: Path, max_flips: int = 10000,
max_restarts: int = 100, noise_prob: float = 0.57, seed: Optional[int] = None) -> Dict[str, Any]:
        """Run WalkSAT on a single CNF file and return metrics."""

        print(f"Benchmarking: {cnf_file.name}")

        # Load and transform the formula
        start_load = time.time()
        instance = Formula.from_dimacs(str(cnf_file))
        load_time = time.time() - start_load

        # Solve with WalkSAT
        solver = self.solver(instance, seed=seed)

        start_solve = time.time()
        stats = solver.solve_with_stats(
            max_flips=max_flips,
            max_restarts=max_restarts,
            noise_prob=noise_prob
        )
        solve_time = time.time() - start_solve

        # Compile results
        result = {
            'seed': solver.seed,
            'filename': cnf_file.name,
            'variables': instance.num_variables,
            'clauses': len(instance.clauses),
            'solution_found': stats['solution_found'],
            'restarts_used': stats['restarts_used'],
            'flips_used': stats['flips_used'],
            'final_satisfied': stats['final_satisfied'],
            'load_time_seconds': round(load_time, 4),
            'solve_time_seconds': round(solve_time, 4),
            'total_time_seconds': round(load_time + solve_time, 4),
            'flips_per_second': round(stats['flips_used'] / solve_time, 2) if solve_time > 0 else 0,
            'timestamp': datetime.now().isoformat()
        }

        print(f"  Result: {'SOLVED' if result['solution_found'] else 'UNSOLVED'} "
              f"in {result['solve_time_seconds']}s "
              f"({result['flips_used']} flips)")

        return result

    def run_all_benchmarks(self, max_files: Optional[int] = None, seed: Optional[int] = None, **solver_kwargs) -> Dict[str, Any]:
        """Run benchmarks on all CNF files"""

        cnf_files = self.find_cnf_files()
        if max_files:
            cnf_files = cnf_files[:max_files]

        print(f"Found {len(cnf_files)} CNF files")

        results = []
        for cnf_file in cnf_files:
            try:
                result = self.run_benchmark(cnf_file, **solver_kwargs, seed=seed)
                results.append(result)
            except Exception as e:
                print(f"Error processing {cnf_file.name}: {e}")
                continue

        # Compute aggregate statistics
        summary = self._compute_summary(results)

        # Save results
        output = {
            'summary': summary,
            'individual_results': results,
            'benchmark_config': {
                'solver_parameters': solver_kwargs,
                'total_files_processed': len(results),
                'run_timestamp': datetime.now().isoformat()
            }
        }

        self._save_results(output)
        self._print_summary(summary)

        return output

    def _compute_summary(self, results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Compute aggregate statistics from individual results."""

        solved = [r for r in results if r['solution_found']]
        unsolved = [r for r in results if not r['solution_found']]

        return {
            'total_instances': len(results),
            'solved_count': len(solved),
            'unsolved_count': len(unsolved),
            'success_rate': len(solved) / len(results) if results else 0,

            # Time statistics (only for solved instances)
            'avg_solve_time_solved': statistics.mean([r['solve_time_seconds'] for r in solved]) if solved else 0,
            'median_solve_time_solved': statistics.median([r['solve_time_seconds'] for r in solved]) if solved else 0,
            'avg_flips_solved': statistics.mean([r['flips_used'] for r in solved]) if solved else 0,
            'avg_restarts_solved': statistics.mean([r['restarts_used'] for r in solved]) if solved else 0,

            # Performance metrics
            'avg_flips_per_second': statistics.mean([r['flips_per_second'] for r in results]) if results else 0,

            # For unsolved instances
            'avg_final_satisfied_unsolved': statistics.mean([r['final_satisfied'] for r in unsolved]) if unsolved else 0,
        }

    def _save_results(self, output: Dict[str, Any], format: str = "json"):
        """Save results to file."""

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        solver_name = self.solver.__name__.lower()
        filename = self.results_dir / f"benchmark_{solver_name}_results_{timestamp}.{format}"

        if format == "json":
            with open(filename, 'w') as f:
                json.dump(output, f, indent=2)
        elif format == "csv":
            self._save_as_csv(output, filename)

        print(f"Results saved to: {filename}")

    def _save_as_csv(self, output: Dict[str, Any], filename: Path):
        """Save individual results as CSV for easy analysis."""

        import csv

        with open(filename, 'w', newline='') as f:
            writer = csv.writer(f)
            # Header
            writer.writerow([
                'filename', 'variables', 'clauses', 'solution_found',
                'restarts_used', 'flips_used', 'final_satisfied',
                'load_time_seconds', 'solve_time_seconds', 'total_time_seconds',
                'flips_per_second', 'timestamp'
            ])
            # Data
            for result in output['individual_results']:
                writer.writerow([
                    result['filename'],
                    result['variables'],
                    result['clauses'],
                    result['solution_found'],
                    result['restarts_used'],
                    result['flips_used'],
                    result['final_satisfied'],
                    result['load_time_seconds'],
                    result['solve_time_seconds'],
                    result['total_time_seconds'],
                    result['flips_per_second'],
                    result['timestamp']
                ])

    def _print_summary(self, summary: Dict[str, Any]):
        """Print a nice summary to console."""

        print("\n" + "="*50)
        print("BENCHMARK SUMMARY")
        print("="*50)
        print(f"Total instances: {summary['total_instances']}")
        print(f"Solved: {summary['solved_count']} / {summary['total_instances']}")
        print(f"Success rate: {summary['success_rate']:.1%}")
        print(f"Average solve time (solved): {summary['avg_solve_time_solved']:.3f}s")
        print(f"Average flips (solved): {summary['avg_flips_solved']:.0f}")
        print(f"Average restarts (solved): {summary['avg_restarts_solved']:.1f}")
        print(f"Average flips/second: {summary['avg_flips_per_second']:.0f}")
        if summary['unsolved_count'] > 0:
            print(f"Avg satisfied clauses (unsolved): {summary['avg_final_satisfied_unsolved']:.1f}")
