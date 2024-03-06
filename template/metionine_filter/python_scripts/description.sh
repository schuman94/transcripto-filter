#!/bin/bash -x
#SBATCH --job-name=description
#SBATCH --output=description.out
#SBATCH --error=description.err

START_TIME=$(date +%s)
echo "Ejecución iniciada en: $(date)"

module load Python/3.10.8-GCCcore-12.2.0
module load Biopython/1.79-foss-2021a

ALINEAMIENTOS=$1
FASTA=$2

python3 description.py $ALINEAMIENTOS $FASTA

echo "Ejecución finalizada en: $(date)"
