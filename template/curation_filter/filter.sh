#!/bin/bash -x
#SBATCH --job-name=filterRun
#SBATCH --output=filter.out
#SBATCH --error=filter.err

START_TIME=$(date +%s)
echo "Ejecución iniciada en: $(date)"

module load Python/3.10.8-GCCcore-12.2.0
module load Biopython/1.79-foss-2021a


# Python script path
P1=./python_scripts/main.py

# Config file
CONFIG=./python_scripts/config.txt

# Directorios de alineamientos por defecto en el workflow
ALIGNMENTS_DIR=../alignments/Alineamientos_mafft
ALIGNMENTS_FILTERED_DIR=./Alineamientos_filtrados
ALIGNMENTS_DISCARDED_DIR=./Alineamientos_descartados
mkdir -p $ALIGNMENTS_DISCARDED_DIR

# Ejecucion del script
python3 $P1 $ALIGNMENTS_DIR $ALIGNMENTS_FILTERED_DIR $CONFIG

# Copiar alineamientos descartados en ALIGNMENTS_DISCARDED_DIR
for file in $ALIGNMENTS_DIR/*.mafft.fasta; do
    filename=$(basename "$file")
    if [ ! -f "$ALIGNMENTS_FILTERED_DIR/$filename" ]; then
        cp "$file" "$ALIGNMENTS_DISCARDED_DIR/"
    fi
done

echo "Ejecución finalizada en: $(date)"
