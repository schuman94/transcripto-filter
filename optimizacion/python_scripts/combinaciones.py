import os
import itertools
import argparse

def create_config_files(output_directory, parametros):
    if not os.path.exists(output_directory):
        os.makedirs(output_directory)

    # Separar parámetros fijos de variables
    fixed_params = {k: v for k, v in parametros.items() if not isinstance(v, list)}
    variable_params = {k: v for k, v in parametros.items() if isinstance(v, list)}

    # Generar combinaciones solo para los parámetros variables
    keys = list(variable_params.keys())
    values = list(itertools.product(*variable_params.values()))

    for i, combination in enumerate(values, start=1):
        subdirectory = os.path.join(output_directory, str(i))
        os.makedirs(subdirectory, exist_ok=True)

        config_file_path = os.path.join(subdirectory, "config.txt")
        with open(config_file_path, 'w') as config_file:
            # Escribir parámetros fijos
            for key, value in fixed_params.items():
                config_file.write(f"{key}={value}\n")
            # Escribir combinaciones de parámetros variables
            for key, value in zip(keys, combination):
                config_file.write(f"{key}={value}\n")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate configuration files for different parameter combinations.")
    parser.add_argument("output_dir", type=str, help="Output directory for configuration files")
    args = parser.parse_args()

    parametros = {
        "porcentaje_minimo_coincidencia": [0.3, 0.4, 0.5],
        "longitud_minima_subseq": [8, 10, 12],
        "porcentaje_minimo_coincidencia_estricto": [0.5, 0.625, 0.75],
        "longitud_minima_subseq_estrica": [3, 5, 7],
        "future_elements": 15, #[8, 9, 10]
        "longitud_minima_total_subseqs": [15, 20, 25],
        "ratio_minimo_longitud": [0.4, 0.45, 0.5]
    }

# PARAMETROS CON UN RANGO MAS AMPLIO
    #parametros = {
     #   "porcentaje_minimo_coincidencia": [0.25, 0.375, 0.5],
     #   "longitud_minima_subseq": [8, 10, 12],
     #   "porcentaje_minimo_coincidencia_estricto": [0.5, 0.625, 0.75],
     #   "longitud_minima_subseq_estrica": [3, 5, 7],
     #   "future_elements": [7, 10, 13],
     #   "longitud_minima_total_subseqs": [10, 20, 30],
     #   "ratio_minimo_longitud": [0.25, 0.5, 0.75]
    #}

    create_config_files(args.output_dir, parametros)
