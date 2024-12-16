#!/bin/bash

#SBATCH --job-name=buscar_alineamientos
#SBATCH --output=buscar_alineamientos.out
#SBATCH --error=buscar_alineamientos.err
#SBATCH --cpus-per-task=1

# Configuración de rutas
CSV_DIR="../resultados/" # Directorio que contiene los archivos CSV
FASTA_BASE_DIR="../../metionine_filter/resultados/" # Base de los subdirectorios de FASTA
OUTPUT_DIR="./output/" # Directorio de salida
PYTHON_SCRIPT="buscar_alineamientos.py" # Ruta al script Python
MAX_SEQUENCES=8 # Número máximo de secuencias

# Crear el directorio de salida si no existe
mkdir -p "$OUTPUT_DIR"

module load Python/3.10.8-GCCcore-12.2.0
module load Biopython/1.79-foss-2021a

# Procesar opciones de línea de comandos
while [[ "$#" -gt 0 ]]; do
    case $1 in
        --max) MAX_SEQUENCES="$2"; shift 2;;
        *) echo "Opción desconocida: $1"; exit 1;;
    esac
done

# Procesar cada archivo CSV que contenga "Match.csv" en su nombre
for csv_file in "$CSV_DIR"/*Match.csv; do
    if [[ -f "$csv_file" ]]; then
        echo "Procesando $csv_file..."
        python3 "$PYTHON_SCRIPT" --csv "$csv_file" \
                                 --fasta_base_dir "$FASTA_BASE_DIR" \
                                 --output_dir "$OUTPUT_DIR" \
                                 --max_sequences "$MAX_SEQUENCES"
    fi
done

echo "Procesamiento completado. Resultados en $OUTPUT_DIR."
