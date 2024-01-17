#!/bin/bash -x
#SBATCH --job-name=blastxRun
#SBATCH --output=blastx.out
#SBATCH --error=blastx.err
#SBATCH --cpus-per-task=4

# Fichero fasta obtenido en Trinity
QUERY=$1

# Fichero fasta de la base de datos de peptidos
DB=$2

# Nombre del fichero de salida en formato csv
OUT=./blastx_out.csv

echo "Iniciando el script en $(date)"

module load BLAST+/2.13.0-gompi-2022a
ulimit unlimited
blastx -query $QUERY -db $DB -evalue 1e-6 -outfmt 10 -out $OUT -num_threads 4

echo "Ejecucion finalizada en $(date)"
