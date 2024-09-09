#!/bin/bash -x
#SBATCH --job-name=QuantifyTPM
#SBATCH --output=quantify.out
#SBATCH --error=quantify.err
#SBATCH --cpus-per-task=40
#SBATCH --mem=200G

# Cargar el módulo Trinity (que incluye Salmon)
module load Trinity

# Inicializar variables
R1=""
R2=""
TRINITY=""
QUANT_DIR="output_salmon"
RESULTS_DIR="resultados"

# Procesar los argumentos
while [[ "$#" -gt 0 ]]; do
    case $1 in
        --r1) R1="$2"; shift ;;
        --r2) R2="$2"; shift ;;
        --trinity) TRINITY="$2"; shift ;;
        *) echo "Argumento desconocido: $1"; exit 1 ;;
    esac
    shift
done

# Verificar que se pasaron los argumentos necesarios
if [[ -z "$R1" || -z "$R2" || -z "$TRINITY" ]]; then
    echo "Uso: sbatch quantify.sh --r1 read1.fastq --r2 read2.fastq --trinity ensamblado.fasta"
    exit 1
fi

echo "Iniciando la cuantificación de TPM con Salmon en: $(date)"

# Crear el directorio de cuantificación si no existe
if [ ! -d "$QUANT_DIR" ]; then
    mkdir -p "$QUANT_DIR"
    echo "Directorio de cuantificación $QUANT_DIR creado."
fi


# Ejecutar la cuantificación de abundancia usando Salmon
$TRINITY_HOME/util/align_and_estimate_abundance.pl \
--seqType fq \
--left "$R1" \
--right "$R2" \
--transcripts "$TRINITY" \
--est_method salmon \
--output_dir "$QUANT_DIR" \
--thread_count 40 \
--trinity_mode \
--prep_reference

echo "Cuantificación finalizada en: $(date)"

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
