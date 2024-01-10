#!/bin/bash -x
#SBATCH --job-name=buscoRun
#SBATCH --output=busco.out
#SBATCH --error=busco.err
#SBATCH --cpus-per-task=10

# Fichero fasta resultante del ensamblaje
A=$1

# Base de datos de linaje de referencia
B=/LUSTRE/home/qin/u49047421/transcriptomica/data/BUSCO_DB/metazoa_odb10 

echo "Iniciando el script en: $(date)"

module load BUSCO
busco --offline -m transcriptome -i $A -o busco_output -c 10 -l $B 

echo "Ejecucion finalizada en $(date)"
