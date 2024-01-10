import os
import csv
import sys

def read_config(config_file):
    params = {}
    with open(config_file, 'r') as file:
        for line in file:
            key, value = line.strip().split('=')
            params[key] = value
    return params

def read_summary(summary_file):
    summary = {}
    with open(summary_file, 'r') as file:
        for line in file:
            key, value = line.strip().split('=')
            summary[key] = value
    return summary

def collect_data(combinations_directory):
    data = []

    for subdir, dirs, files in os.walk(combinations_directory):
        config_path = os.path.join(subdir, 'config.txt')
        summary_path = os.path.join(subdir, 'coincidencias', 'summary.txt')

        if os.path.isfile(config_path) and os.path.isfile(summary_path):
            subdir_number = os.path.basename(subdir)

            config_data = read_config(config_path)
            summary_data = read_summary(summary_path)

            row = [subdir_number] + [config_data.get(key) for key in config_columns] + [summary_data.get(key) for key in summary_columns]
            data.append(row)

    return data

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Uso: python script.py /path/to/directory")
        sys.exit(1)

    root_directory = sys.argv[1].rstrip(os.sep)  # Elimina el separador de directorio al final si existe
    base_name = os.path.basename(root_directory)  # Obtiene el nombre base del directorio

    combinations_directory = None

    # Buscar subdirectorio que termina en "_combinaciones"
    for subdir, dirs, _ in os.walk(root_directory):
        if subdir.endswith('_combinaciones'):
            combinations_directory = subdir
            break

    if not combinations_directory:
        print(f"No se encontró un subdirectorio que termine en '_combinaciones' dentro de {root_directory}")
        sys.exit(1)

    config_columns = [
        'porcentaje_minimo_coincidencia',
        'longitud_minima_subseq',
        'porcentaje_minimo_coincidencia_estricto',
        'longitud_minima_subseq_estrica',
        'future_elements',
        'longitud_minima_total_subseqs',
        'ratio_minimo_longitud'
    ]
    summary_columns = ['TP', 'FP', 'FN', 'TN']

    data = collect_data(combinations_directory)
    data.sort(key=lambda x: int(x[0]))

    output_csv_path = os.path.join(root_directory, f"{base_name}_resultados.csv")
    with open(output_csv_path, 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(['N'] + config_columns + summary_columns)
        writer.writerows(data)

    print(f"Datos consolidados guardados en {output_csv_path}")
