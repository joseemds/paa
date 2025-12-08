from pathlib import Path
import argparse
import json

parser = argparse.ArgumentParser()
parser.add_argument("input_file")

args = parser.parse_args()

columns = [
    ("filename", "Filename"),
    ("variables", "Vars"),
    ("clauses", "Clauses"),
    ("solution_found", "Solved"),
    ("load_time_seconds", "Load (s)"),
    ("solve_time_seconds", "Solve (s)"),
    ("total_time_seconds", "Total (s)"),
]

header = " & ".join(col[1] for col in columns) + " \\\\ \\hline\n"
rows = ""


args = parser.parse_args()
path = Path(args.input_file)
data = json.loads(path.read_text(encoding="utf-8"))['individual_results']


for item in data:
    row = " & ".join(
        str(item[key]) if not isinstance(item[key], bool)
        else ("Yes" if item[key] else "No")
        for key, _ in columns
    )
    rows += row + " \\\\\n"

latex = (
    "\\begin{table}[h!]\n"
    "\\centering\n"
    "\\resizebox{\\textwidth}{!}{%\n"
    "\\begin{tabular}{|" + "c|" * len(columns) + "}\n"
    "\\hline\n"
    + header
    + rows
    + "\\hline\n"
    "\\end{tabular}}\n"
    "\\caption{SAT solver results}\n"
    "\\label{tab:sat-results}\n"
    "\\end{table}"
)

print(latex)
