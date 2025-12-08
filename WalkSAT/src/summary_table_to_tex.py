from pathlib import Path
import argparse
import json


def read_summary(file):
  path = Path(file)
  return json.loads(path.read_text(encoding="utf-8"))['summary']


parser = argparse.ArgumentParser()
parser.add_argument("input_file")

fields = [
    ("total_instances", "Total Instances"),
    ("total_time", "Total Time"),
    # ("unsolved_count", "Unsolved"),
    # ("success_rate", "Success Rate"),
    ("avg_unsolve_time_solved", "Avg Solve Time (s)"),
    ("median_unsolve_time_solved", "Median Solve Time (s)"),
    ('avg_final_satisfied_unsolved', 'Avg Satisfied Clauses')
    # ("avg_flips_solved", "Avg Flips"),
    # ("avg_restarts_solved", "Avg Restarts"),
    # ("avg_flips_per_second", "Flips/sec"),
    # ("avg_final_satisfied_unsolved", "Avg Final Sat (unsolved)"),
]

label = "Local Search"

args = parser.parse_args()
data = read_summary(args.input_file)


header = f"Metric & {label} \\\\ \\hline\n"
rows = ""
for key, label in fields:
    val = data.get(key, "-")

    if isinstance(val, float):
        val = f"{val:.4g}"

    rows += f"{label} & {val}  \\\\\n"

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
