#!/bin/bash -x
#SBATCH --job-name=mafft
#SBATCH --output=mafft.out
#SBATCH --error=mafft.err

START_TIME=$(date +%s)
echo "Ejecución iniciada en: $(date)"

# Comprobar que se proporciona el archivo FASTA
if [ -z "$1" ]; then
    echo "Error: Debes proporcionar un archivo FASTA como argumento."
    exit 1
fi

# Input fasta file containing sequences
FASTA=$1

# Verificar que el archivo FASTA existe
if [ ! -f "$FASTA" ]; then
    echo "Error: El archivo FASTA '$FASTA' no existe."
    exit 1
fi

# Obtener el nombre base del archivo sin importar la extensión
BASENAME=$(basename "$FASTA")
BASENAME_NO_EXT="${BASENAME%.*}"  # Eliminar cualquier extensión (fasta, fa, FASTA, etc.)

# Definir el archivo de salida con la extensión .mafft.fasta
OUTPUT="${BASENAME_NO_EXT}.mafft.fasta"

# Cargar el módulo de MAFFT
module load MAFFT

# Ejecutar MAFFT
echo "Ejecutando MAFFT..."
if mafft --anysymbol "$FASTA" > "$OUTPUT"; then
    echo "MAFFT finalizado con éxito."
else
    echo "Error al ejecutar MAFFT."
    exit 1
fi

# Verificar si el archivo MAFFT se creó correctamente
if [ -f "$OUTPUT" ]; then
    echo "Archivo $OUTPUT creado exitosamente"
else
    echo "Error al crear el archivo $OUTPUT"
    exit 1
fi

# Calcular el tiempo total de ejecución
END_TIME=$(date +%s)
TOTAL_TIME=$((END_TIME - START_TIME))

echo "Ejecución finalizada en: $(date)"
echo "Tiempo total de ejecución: $TOTAL_TIME segundos."
