#!/bin/bash -x
#SBATCH --job-name=mafft
#SBATCH --output=mafft.out
#SBATCH --error=mafft.err

START_TIME=$(date +%s)
echo "Ejecución iniciada en: $(date)"

module load Python/3.10.8-GCCcore-12.2.0
module load Biopython/1.79-foss-2021a

# Input txt file containing sequences
INPUT_TXT_FILE=$1

# Python script path
P1=./txtToFasta.py

# Run the Python script to convert txt to fasta
python $P1 $INPUT_TXT_FILE

# Check if the fasta file was created
if [ -f secuencias.fasta ]; then
    echo "Archivo secuencias.fasta creado exitosamente"
else
    echo "Error al crear el archivo secuencias.fasta"
    exit 1
fi

# Ejecución de MAFFT
module load MAFFT
FASTA=./secuencias.fasta

mafft --anysymbol $FASTA > ./secuencias.mafft.fasta

# Verificar si el archivo mafft se creó correctamente
if [ -f secuencias.mafft.fasta ]; then
    echo "Archivo secuencias.mafft.fasta creado exitosamente"
else
    echo "Error al crear el archivo secuencias.mafft.fasta"
    exit 1
fi

# Python script path for single line fasta conversion
P2=./fastaToSingleLine.py

# Run the Python script to convert fasta to single line fasta
python $P2 secuencias.mafft.fasta

# Check if the single line fasta file was created
if [ -f secuencias_single_line.fasta ]; then
    echo "Archivo secuencias_single_line.fasta creado exitosamente"
else
    echo "Error al crear el archivo secuencias_single_line.fasta"
    exit 1
fi

# Remove the original mafft fasta file
rm secuencias.mafft.fasta

# Rename the single line fasta file to secuencias.mafft.fasta
mv secuencias_single_line.fasta secuencias.mafft.fasta

# Python script path for fasta to txt conversion
P3=./fastaToTxt.py

# Run the Python script to convert fasta to txt
python $P3 secuencias.mafft.fasta

# Check if the txt file was created
if [ -f secuencias_converted.txt ]; then
    echo "Archivo secuencias_converted.txt creado exitosamente"
else
    echo "Error al crear el archivo secuencias_converted.txt"
    exit 1
fi

END_TIME=$(date +%s)
echo "Ejecución finalizada en: $(date)"
echo "Duración total: $(($END_TIME - $START_TIME)) segundos"
