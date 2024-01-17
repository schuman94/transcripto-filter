#!/bin/bash -x
#SBATCH --job-name=fastqcRun
#SBATCH --output=fastqc.out
#SBATCH --error=fastqc.err

# Asignacion de los reads como argumentos
P1=$1
P2=$2

echo "Iniciando el script en: $(date)"

mkdir -p ./output

module load FastQC/0.11.9-Java-11
ulimit unlimited
fastqc $P1 $P2 -o ./output/

echo "Ejecucion finalizada en: $(date)"
