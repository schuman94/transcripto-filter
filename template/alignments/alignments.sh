#!/bin/bash -x
#SBATCH --job-name=alignmentsRun
#SBATCH --output=alignments.out
#SBATCH --error=alignments.err

START_TIME=$(date +%s)
echo "Ejecución iniciada en: $(date)"

module load R

# R script paths
R1=./RScripts/1-Find_extract_create.R
R2=./RScripts/2-Create_sequences_groups_modified.R

# PARAMETROS1

# Fichero csv obtenido en Blastx
BLAST_CSV=$1

# Fichero fasta obtenido en Trinity
TRINITY_FASTA=$2

EXTRACTED=./extracted_sequences.fasta
NO_HIT=./no_hit_sequences.fasta

# Ejecucion del script 1
echo "Executing the first R script: find_extract_create"
Rscript $R1 $BLAST_CSV $TRINITY_FASTA $EXTRACTED $NO_HIT

sleep 5

#PARAMETROS2
ALINEAMIENTOS=Alineamientos

# Fichero fasta de la base de datos de peptidos
DB=$3

mkdir -p $ALINEAMIENTOS

# Ejecucion del script 2
echo "Executing the second R script: create_sequences_groups"
Rscript $R2 $BLAST_CSV $EXTRACTED $DB $ALINEAMIENTOS

echo "R scripts finished"

# Clean and MAFFT
module load MAFFT

mkdir -p ./Alineamientos_mafft

# First loop: Remove specified lines in the files
for f in ./Alineamientos/*.fasta
do
    base=$(basename $f)
    # Removing the first 2 lines of the file
    sed -i '1,2d' $f
    # Removing all lines from line 413 to the end of the file
    sed -i '413,$d' $f
done

# Second loop: Convert lower case in sequences to upper case
for f in ./Alineamientos/*.fasta
do
    awk '/^>/ {print($0)} !/^>/ {print(toupper($0))}' $f > temp && mv temp $f
done

# Third loop: Perform alignment with MAFFT
for f in ./Alineamientos/*.fasta
do
    base=$(basename $f)
    mafft --anysymbol $f > "./Alineamientos_mafft/${base%.fasta}".mafft.fasta
done

# Fourth loop: Remove newline characters within each sequence
for f in ./Alineamientos_mafft/*.fasta
do
    awk 'BEGIN{p=0} /^>/ {if(p){printf("\n%s\n",$0);next;}else{p=1;printf("%s\n",$0);next;}} {printf("%s",$0);} END{printf("\n");}' $f > temp && mv temp $f
done

echo "Clean and MAFFT finished"
END_TIME=$(date +%s)
echo "Ejecución finalizada en: $(date)"
DURATION=$((END_TIME - START_TIME))

HOURS=$((DURATION / 3600))
MINUTES=$((DURATION % 3600 / 60))

echo "La ejecución ha durado $HOURS horas y $MINUTES minutos aproximadamente"
