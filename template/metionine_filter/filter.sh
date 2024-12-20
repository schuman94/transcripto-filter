#!/bin/bash -x
#SBATCH --job-name=M-filter
#SBATCH --output=M-filter.out
#SBATCH --error=M-filter.err

START_TIME=$(date +%s)
echo "Ejecución iniciada en: $(date)"

module load Python/3.10.8-GCCcore-12.2.0
module load Biopython/1.79-foss-2021a

# Creación de directorios
mkdir -p ./mafft
mkdir -p ./mafft/Alineamientos_mafft
mkdir -p ./mafft/Alineamientos_pre_mafft
mkdir -p ./resultados
mkdir -p ./resultados/Alineamientos_M_Previa
mkdir -p ./resultados/Alineamientos_Multiframe
mkdir -p ./resultados/Alineamientos_Perfectos
mkdir -p ./resultados/Alineamientos_Revision_Manual
mkdir -p ./resultados/Alineamientos_Multiframe_Filtrados

# Generar los ficheros fasta
cd ./python_scripts
python3 generarFastas.py

echo "Ficheros fasta generados"

# MAFFT
cd ../mafft
module load MAFFT

for f in ./Alineamientos_pre_mafft/*.fasta
do
    base=$(basename $f)
    mafft --anysymbol $f > "./Alineamientos_mafft/${base%.fasta}".mafft.fasta
done

# Remove newline characters within each sequence
for f in ./Alineamientos_mafft/*.fasta
do
    awk 'BEGIN{p=0} /^>/ {if(p){printf("\n%s\n",$0);next;}else{p=1;printf("%s\n",$0);next;}} {printf("%s",$0);} END{printf("\n");}' $f > temp && mv temp $f
done

echo "MAFFT finished"

cd ../python_scripts
python3 filterM.py
python3 summary.py

echo "Ficheros clasificados"

echo "Filtrando alineamientos multiframe"
python3 ./filtrarMultiframe.py ../resultados/Alineamientos_Multiframe ../resultados/Alineamientos_Multiframe_Filtrados ../../blastx/blastx_out.csv

echo "Ejecución finalizada en: $(date)"
