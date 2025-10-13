from pathlib import Path
import argparse
import json


def read_summary(file):
  path = Path(file)
  return json.loads(path.read_text(encoding="utf-8"))['summary']


parser = argparse.ArgumentParser()
parser.add_argument("input_files", nargs="+")

fields = [
    ("total_instances", "Total Instances"),
    ("solved_count", "Solved"),
    ("unsolved_count", "Unsolved"),
    ("success_rate", "Success Rate"),
    ("avg_solve_time_solved", "Avg Solve Time (s)"),
    ("median_solve_time_solved", "Median Solve Time (s)"),
    ("avg_flips_solved", "Avg Flips"),
    ("avg_restarts_solved", "Avg Restarts"),
    ("avg_flips_per_second", "Flips/sec"),
    ("avg_final_satisfied_unsolved", "Avg Final Sat (unsolved)"),
]

label_a = "Local Search"
label_b = "DPLL"

args = parser.parse_args()
localsearch_data = read_summary(args.input_files[0])
dpll_data = read_summary(args.input_files[1])


header = f"Metric & {label_a} & {label_b} \\\\ \\hline\n"
rows = ""
for key, label in fields:
    val_a = dpll_data.get(key, "-")
    val_b = localsearch_data.get(key, "-")

    # Format floats nicely
    if isinstance(val_a, float):
        val_a = f"{val_a:.4g}"
    if isinstance(val_b, float):
        val_b = f"{val_b:.4g}"

    rows += f"{label} & {val_a} & {val_b} \\\\\n"

latex = (
    "\\begin{table}[h!]\n"
    "\\centering\n"
    "\\begin{tabular}{|l|c|c|}\n"
    "\\hline\n"
    + header
    + rows
    + "\\hline\n"
    "\\end{tabular}\n"
    "\\caption{Comparison of aggregated SAT solver results}\n"
    "\\label{tab:solver-summary-comparison}\n"
    "\\end{table}"
)

print(latex)

args = parser.parse_args()
