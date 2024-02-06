#!/bin/bash -x
#SBATCH --job-name=T-filter
#SBATCH --output=t-filter.out
#SBATCH --error=t-filter.err
#SBATCH --cpus-per-task=40
#SBATCH --mem=200G

# Inicializar variables
READ1=""
READ2=""
DB=""
TRINITY_FASTA=""

# Procesar argumentos
while [[ $# -gt 0 ]]; do
    key="$1"

    case $key in
        --r1)
            READ1=$(realpath "$2")
            shift # Pasar al siguiente argumento
            ;;
        --r2)
            READ2=$(realpath "$2")
            shift
            ;;
        --db)
            DB=$(realpath "$2")
            shift
            ;;
        --trinity)
            TRINITY_FASTA=$(realpath "$2")
            shift
            ;;
        *)
            # Argumento desconocido
            echo "Argumento no reconocido: $key"
            exit 1
    esac
    shift # Pasar al siguiente argumento
done

# Verificar la presencia del argumento obligatorio --db
if [[ -z $DB ]]; then
    echo "El argumento --db es obligatorio."
    exit 1
fi

# Comenzar desde BUSCO si se proporciona --trinity
if [[ -n $TRINITY_FASTA ]]; then
    # Saltar las secciones FASTQC y TRINITY
    echo "Saltando FASTQC y TRINITY, comenzando desde BUSCO"

else
    # Verificar la presencia de --r1 y --r2
    if [[ -z $READ1 ]] || [[ -z $READ2 ]]; then
        echo "Los argumentos --r1 y --r2 son obligatorios si no se proporciona --trinity."
        exit 1
    fi

    # FASTQC
    cd ./fastqc

    echo "Iniciando el fastqc en: $(date)"

    mkdir -p ./output

    module load FastQC/0.11.9-Java-11
    fastqc $READ1 $READ2 -o ./output/

    echo "Ejecucion de fastqc finalizada en: $(date)"
    cd ..

    # TRINITY
    cd ./trinity

    echo "Iniciando trinity en: $(date)"

    module load Trinity
    ulimit unlimited
    Trinity --trimmomatic --seqType fq --left $READ1 --right $READ2 --max_memory 200G --CPU 40 --no_version_check

    echo "Ejecucion de trinity finalizada en: $(date)"

    TRINITY_FASTA=./trinity_out_dir.Trinity.fasta
    TRINITY_FASTA=$(realpath $TRINITY_FASTA)
    cd ..

    sleep 5

fi

# BUSCO
cd ./busco

BUSCO_DB=/LUSTRE/home/qin/u49047421/transcriptomica/data/BUSCO_DB/metazoa_odb10

echo "Iniciando busco en: $(date)"

module load BUSCO
busco --offline -m transcriptome -i $TRINITY_FASTA -o busco_output -c 10 -l $BUSCO_DB

echo "Ejecucion de busco finalizada en $(date)"
cd ..

sleep 5


# BLASTX
cd ./blastx

# Nombre del fichero de salida en formato csv
OUT=./blastx_out.csv

echo "Iniciando blastx en $(date)"

module load BLAST+/2.13.0-gompi-2022a
blastx -query $TRINITY_FASTA -db $DB -evalue 1e-6 -outfmt 10 -out $OUT -num_threads 4

echo "Ejecucion de blastx finalizada en $(date)"
BLAST_CSV=$(realpath $OUT)
cd ..

sleep 5


# ALIGNMENTS
cd ./alignments

echo "Ejecución de alineamientos y mafft iniciada en: $(date)"

module load R

# R script paths
R1=./RScripts/1-Find_extract_create.R
R2=./RScripts/2-Create_sequences_groups_modified.R

# OUTPUT
EXTRACTED=./extracted_sequences.fasta
NO_HIT=./no_hit_sequences.fasta

# Ejecucion del script 1
echo "Executing the first R script: find_extract_create"
Rscript $R1 $BLAST_CSV $TRINITY_FASTA $EXTRACTED $NO_HIT

sleep 5

#PARAMETROS2
ALINEAMIENTOS=Alineamientos

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
echo "Ejecución de alineamientos y mafft finalizada en: $(date)"

cd ..

sleep 5


# CURATION FILTER
cd ./curation_filter

echo "Ejecución de curation filter iniciada en: $(date)"

module load Python/3.10.8-GCCcore-12.2.0
module load Biopython/1.79-foss-2021a


# Python script path
P1=./python_scripts/main.py

# Config file
CONFIG=./python_scripts/config.txt

# Directorios de alineamientos por defecto en el workflow
ALIGNMENTS_DIR=../alignments/Alineamientos_mafft
ALIGNMENTS_FILTERED_DIR=./Alineamientos_filtrados

# Ejecucion del script
python3 $P1 $ALIGNMENTS_DIR $ALIGNMENTS_FILTERED_DIR $CONFIG

echo "Ejecución de curation filter finalizada en: $(date)"

cd ..

sleep 5


# METIONINE FILTER
cd ./metionine_filter

echo "Ejecución de metionine filter iniciada en: $(date)"

module load Python/3.10.8-GCCcore-12.2.0
module load Biopython/1.79-foss-2021a

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

echo "Ejecución finalizada en: $(date)"
