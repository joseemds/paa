import argparse
import json
from pathlib import Path

def read_individual_results(file_path):
    """Lê a chave 'individual_results' de um arquivo JSON."""
    path = Path(file_path)
    if not path.exists():
        print(f"Erro: Arquivo não encontrado {file_path}")
        exit(1)
    data = json.loads(path.read_text(encoding="utf-8"))
    return data.get('individual_results', [])

def format_value(value, is_bool=False, is_float=False):
    """Formata valores para a tabela LaTeX."""
    if value is None:
        return "-"
    if is_bool:
        return "Yes" if value else "No"
    if is_float:
        try:
            return f"{float(value):.4g}"
        except (ValueError, TypeError):
            return str(value)
    return str(value)

def escape_latex(text):
    """Escapa caracteres especiais do LaTeX no texto."""
    if text is None:
        return ""
    return text.replace('_', '\\_').replace('%', '\\%').replace('&', '\\&')

# --- Configuração do Argparse ---
parser = argparse.ArgumentParser(
    description="Compara resultados individuais de dois solvers SAT e gera uma tabela LaTeX."
)
# Mantém a mesma lógica de entrada do seu primeiro script
parser.add_argument(
    "input_files",
    nargs=2,
    metavar=("WALKSAT_JSON", "DPLL_JSON"),
    help="Dois arquivos JSON de entrada: primeiro o WalkSAT/LocalSearch, depois o DPLL."
)
args = parser.parse_args()

# --- Carregamento e Mapeamento de Dados ---

# Assume input_files[0] é WalkSAT e input_files[1] é DPLL
walksat_results = read_individual_results(args.input_files[0])
dpll_results = read_individual_results(args.input_files[1])

# Mapeia resultados por nome de arquivo para fácil consulta
# item['filename'] -> item
walksat_map = {item['filename']: item for item in walksat_results}
dpll_map = {item['filename']: item for item in dpll_results}

# Obtém uma lista única e ordenada de todos os nomes de arquivos de ambos os conjuntos
all_filenames = sorted(list(
    set(walksat_map.keys()) | set(dpll_map.keys())
))

# --- Geração da Tabela LaTeX ---

# Define os cabeçalhos das colunas
labels = ["Filename", "DPLL Solved", "DPLL Time (s)", "WalkSAT Solved", "WalkSAT Time (s)"]
header = " & ".join(labels) + " \\\\ \\hline\n"
col_format = "|l|c|c|c|c|" # l=left (filename), c=center (data)

rows = ""
for filename in all_filenames:
    # Obtém os dados de cada solver; pode ser None se o arquivo não estiver nesse conjunto
    dpll_data = dpll_map.get(filename)
    walksat_data = walksat_map.get(filename)

    # Extrai e formata os valores desejados, usando 'None' para dados ausentes
    dpll_solved = format_value(dpll_data.get('solution_found') if dpll_data else None, is_bool=True)
    dpll_time = format_value(dpll_data.get('solve_time_seconds') if dpll_data else None, is_float=True)
    
    walksat_solved = format_value(walksat_data.get('solution_found') if walksat_data else None, is_bool=True)
    walksat_time = format_value(walksat_data.get('solve_time_seconds') if walksat_data else None, is_float=True)

    # Escapa o nome do arquivo para LaTeX
    safe_filename = escape_latex(filename)

    # Constrói a linha da tabela
    row_data = [safe_filename, dpll_solved, dpll_time, walksat_solved, walksat_time]
    rows += " & ".join(row_data) + " \\\\\n"

# Monta a tabela LaTeX final
latex = (
    "\\begin{table}[h!]\n"
    "\\centering\n"
    "\\resizebox{\\textwidth}{!}{%\n"
    f"\\begin{{tabular}}{{{col_format}}}\n"
    "\\hline\n"
    + header
    + rows
    + "\\hline\n"
    "\\end{tabular}}\n"
    "\\caption{Comparison of individual SAT solver results (DPLL vs. WalkSAT)}\n"
    "\\label{tab:solver-individual-comparison}\n"
    "\\end{table}"
)

print(latex)
