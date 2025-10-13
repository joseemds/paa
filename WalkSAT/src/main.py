from benchmark.benchmarks import BenchmarkRunner

def main():
    """Example usage"""
    runner = BenchmarkRunner()

    results = runner.run_all_benchmarks(
        max_flips=5000,
        max_restarts=50,
        noise_prob=0.57
    )

if __name__ == "__main__":
    main()
