#!/bin/bash -x
#SBATCH --job-name=makeblastdb
#SBATCH --output=blastdb.out
#SBATCH --error=blastdb.err

#Fichero fasta con la base de datos de peptidos
DB=$1

module load BLAST+/2.13.0-gompi-2022a
makeblastdb -in $DB -dbtype prot

