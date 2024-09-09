#!/bin/bash -x
#SBATCH --job-name=results
#SBATCH --output=results.out
#SBATCH --error=results.err

QUANT_DIR="../trinity/trinity_out_dir/salmon_outdir"
RESULTS_DIR="resultados"

# Crear el directorio "resultados" si no existe
if [ ! -d "$RESULTS_DIR" ]; then
    mkdir -p "$RESULTS_DIR"
    echo "Directorio de resultados $RESULTS_DIR creado."
fi

echo "Iniciando el procesamiento de CSVs con Python"

# Llamar al script Python para procesar los CSVs y añadir el TPM
module load Python/3.10.8-GCCcore-12.2.0
python3 ./python_scripts/tpm.py --quant_file "$QUANT_DIR/quant.sf" --results_dir "$RESULTS_DIR" --csv_dir "../superfamily/resultados"

echo "Proceso completado. CSVs actualizados en la carpeta $RESULTS_DIR"
