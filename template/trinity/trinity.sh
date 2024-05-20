#!/bin/bash -x
#SBATCH --job-name=TrinityRun
#SBATCH --output=trinity.out
#SBATCH --error=trinity.err
#SBATCH --cpus-per-task=40
#SBATCH --mem=200G
#SBATCH --time=7-00:00

P1=$1
P2=$2

echo "Iniciando el script en: $(date)"

module load Trinity
ulimit unlimited
Trinity --trimmomatic --seqType fq --left $P1 --right $P2 --max_memory 200G --CPU 40 --no_version_check

echo "Ejecucion finalizada en: $(date)"
