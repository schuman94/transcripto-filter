#!/bin/bash -x
#SBATCH --job-name=blastxRun
#SBATCH --output=blastx.out
#SBATCH --error=blastx.err
#SBATCH --cpus-per-task=4

# Fichero fasta obtenido en Trinity
QUERY=$1

# Fichero fasta de la base de datos de peptidos
DB=$2

# Nombre del fichero de salida
OUT=./blastx_out.csv

echo "Iniciando el script en $(date)"

module load BLAST+/2.13.0-gompi-2022a
ulimit unlimited

# Ejecutar BLASTX con el formato extendido y separado por comas
blastx -query $QUERY -db $DB -evalue 1e-6 \
    -outfmt "10 qseqid sseqid pident length mismatch gapopen qstart qend sstart send evalue bitscore qframe" \
    -out $OUT -num_threads 4

# Reemplazar valores en la última columna (qframe) con nombres descriptivos
echo "Modificando valores de la columna qframe..."
awk -F',' 'BEGIN {OFS=","}
{
    if ($13 == "1") $13 = "Frame_F1";
    else if ($13 == "2") $13 = "Frame_F2";
    else if ($13 == "3") $13 = "Frame_F3";
    else if ($13 == "-1") $13 = "Frame_R1";
    else if ($13 == "-2") $13 = "Frame_R2";
    else if ($13 == "-3") $13 = "Frame_R3";
    print $0;
}' $OUT > temp.csv && mv temp.csv $OUT

echo "Ejecución finalizada en $(date)"
