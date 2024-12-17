#!/bin/bash -x
#SBATCH --job-name=T-filter
#SBATCH --output=t-filter.out
#SBATCH --error=t-filter.err
#SBATCH --cpus-per-task=40
#SBATCH --mem=200G
#SBATCH --time=14-00:00

# find . -type f -exec dos2unix {} \;

echo "$(date): Ejecución de Transcripto-filter iniciada"

# Inicializar variables
READ1=""
READ2=""
DB=""
TRINITY_FASTA=""
DB2="" # Base de datos de peptidos señal
DB3="" # Base de datos de virroconus
FASTQC=true # Por defecto, fastqc es true
BUSCO=true  # Por defecto, busco es true

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
        --db1)
            DB1=$(realpath "$2")
            shift
            ;;
        --trinity)
            TRINITY_FASTA=$(realpath "$2")
            shift
            ;;
        --db2)
            DB2=$(realpath "$2")
            shift
            ;;
        --db3)
            DB3=$(realpath "$2")
            shift
            ;;
        --fastqc)
            FASTQC=$2
            shift
            ;;
        --busco)
            BUSCO=$2
            shift
            ;;
        *)
            # Argumento desconocido
            echo "Argumento no reconocido: $key"
            exit 1
    esac
    shift # Pasar al siguiente argumento
done

# Verificar la presencia del argumento obligatorio --db1
if [[ -z $DB1 ]]; then
    echo "El argumento --db1 es obligatorio."
    exit 1
fi

# Comenzar desde BUSCO si se proporciona --trinity
if [[ -n $TRINITY_FASTA ]]; then
    # Saltar las secciones FASTQC y TRINITY
    echo "Fasta ensamblado proporcionado. Saltando FASTQC y TRINITY"

else
    # Verificar la presencia de --r1 y --r2
    if [[ -z $READ1 ]] || [[ -z $READ2 ]]; then
        echo "Los argumentos --r1 y --r2 son obligatorios si no se proporciona --trinity."
        exit 1
    fi

    # FASTQC
    # Ejecutar FASTQC solo si FASTQC es true
    if [[ $FASTQC == true ]]; then
        cd ./fastqc

        echo "$(date): Iniciando fastqc"

        mkdir -p ./output

        module load FastQC/0.11.9-Java-11
        fastqc $READ1 $READ2 -o ./output/

        echo "$(date): Ejecucion de fastqc finalizada"
        cd ..
    fi

    # TRINITY
    cd ./trinity

    echo "$(date): Iniciando Trinity"

    module load Trinity
    ulimit unlimited
    Trinity --trimmomatic --seqType fq --left $READ1 --right $READ2 --max_memory 200G --CPU 40 --no_version_check

    echo "$(date): Ejecucion de Trinity finalizada"

    TRINITY_FASTA=./trinity_out_dir.Trinity.fasta
    TRINITY_FASTA=$(realpath $TRINITY_FASTA)
    cd ..

    sleep 5

fi

# BUSCO
if [[ $BUSCO == true ]]; then
    cd ./busco
    BUSCO_DB=/LUSTRE/home/qin/u49047421/transcriptomica/data/BUSCO_DB/metazoa_odb10
    echo "$(date): Iniciando Busco"

    module load BUSCO
    busco --offline -m transcriptome -i $TRINITY_FASTA -o busco_output -c 10 -l $BUSCO_DB
    echo "$(date): Ejecucion de Busco finalizada"
    cd ..
    sleep 5
fi

# BLASTX
cd ./blastx

# Nombre del fichero de salida en formato csv
OUT=./blastx_out.csv

echo "$(date): Iniciando blastx"

module load BLAST+/2.13.0-gompi-2022a
blastx -query $TRINITY_FASTA -db $DB1 -evalue 1e-6 \
    -outfmt "10 qseqid sseqid pident length mismatch gapopen qstart qend sstart send evalue bitscore qframe" \
    -out $OUT -num_threads 4

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

echo "$(date): Ejecucion de blastx finalizada"
BLAST_CSV=$(realpath $OUT)
cd ..

sleep 5


# ALIGNMENTS
cd ./alignments

echo "$(date): Ejecución de alineamientos y mafft iniciada"

module load R/4.3.0

# R script paths
R1=./RScripts/1-Find_extract_create.R
R2=./RScripts/2-Create_sequences_groups_modified.R

# OUTPUT
EXTRACTED=./extracted_sequences.fasta
NO_HIT=./no_hit_sequences.fasta

# Ejecucion del script 1
echo "$(date): Executing the first R script: find_extract_create"
Rscript $R1 $BLAST_CSV $TRINITY_FASTA $EXTRACTED $NO_HIT

sleep 5

#PARAMETROS2
ALINEAMIENTOS=Alineamientos

mkdir -p $ALINEAMIENTOS

# Ejecucion del script 2
echo "$(date): Executing the second R script: create_sequences_groups"
Rscript $R2 $BLAST_CSV $EXTRACTED $DB1 $ALINEAMIENTOS

echo "$(date): R scripts finished"

# Clean and MAFFT
module load MAFFT/7.490-gompi-2021b-with-extensions

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

echo "$(date): Clean and MAFFT finished"
echo "$(date): Ejecución de alineamientos y mafft finalizada)"

cd ..

sleep 5


# CURATION FILTER
cd ./curation_filter

echo "$(date): Ejecución de curation filter iniciada en: $(date)"

module load Python/3.10.8-GCCcore-12.2.0
module load Biopython/1.79-foss-2021a

# Python script path
P1=./python_scripts/main.py

# Config file
CONFIG=./python_scripts/config.txt

# Directorios de alineamientos por defecto en el workflow
ALIGNMENTS_DIR=../alignments/Alineamientos_mafft
ALIGNMENTS_FILTERED_DIR=./Alineamientos_filtrados
ALIGNMENTS_DISCARDED_DIR=./Alineamientos_descartados
mkdir -p $ALIGNMENTS_FILTERED_DIR
mkdir -p $ALIGNMENTS_DISCARDED_DIR

# Ejecucion del script
python3 $P1 $ALIGNMENTS_DIR $ALIGNMENTS_FILTERED_DIR $CONFIG

# Copiar alineamientos descartados en ALIGNMENTS_DISCARDED_DIR
for file in $ALIGNMENTS_DIR/*.mafft.fasta; do
    filename=$(basename "$file")
    if [ ! -f "$ALIGNMENTS_FILTERED_DIR/$filename" ]; then
        cp "$file" "$ALIGNMENTS_DISCARDED_DIR/"
    fi
done

echo "$(date): Ejecución de curation filter finalizada"

cd ..

sleep 5


# METIONINE FILTER
cd ./metionine_filter

echo "$(date): Ejecución de metionine filter iniciada"

# Creacion de directorios
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

echo "$(date): Ficheros fasta generados"

# MAFFT
cd ../mafft

# module load MAFFT/7.490-gompi-2021b-with-extensions

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

echo "$(date): MAFFT finished"

cd ../python_scripts
python3 filterM.py
python3 summary.py

echo "$(date): Ficheros clasificados"

echo "$(date): Filtrando alineamientos multiframe"
python3 ./filtrarMultiframe.py ../resultados/Alineamientos_Multiframe ../resultados/Alineamientos_Multiframe_Filtrados $BLAST_CSV

echo "$(date): Paso extra: Recuperando descripción de alineamientos antiguos en Metionine Filter"

PDESCRIPTION=../../superfamily/python_scripts/description.py

python3 $PDESCRIPTION ../resultados/Alineamientos_Perfectos $DB1
python3 $PDESCRIPTION ../resultados/Alineamientos_M_Previa $DB1
python3 $PDESCRIPTION ../resultados/Alineamientos_Revision_Manual $DB1
python3 $PDESCRIPTION ../resultados/Alineamientos_Multiframe $DB1

cd ../../

# SUPERFAMILY
# Antes de ejecutar la sección de SF filter, verifica si DB2 y DB3 están configuradas
if [[ -n $DB2 ]] && [[ -n $DB3 ]]; then

    echo "$(date): Ejecución de SF filter iniciada"
    cd ./superfamily

    # Python script path
    SFP1=./python_scripts/alineamientosToCsv.py
    SFP2=./python_scripts/csvToFasta.py
    SFP3=./python_scripts/procesarCsvBlastSignal.py
    SFP4=./python_scripts/csvSignalToFasta.py
    SFP5=./python_scripts/procesarCsvBlastFinal.py
    SFP6=./python_scripts/noMatch.py
    SFP7=./python_scripts/extraerSeqsBlast.py
    SFP8=./python_scripts/procesar_csv_revision_manual.py

    PERFECTOS_DIR=../metionine_filter/resultados/Alineamientos_Perfectos
    MPREVIA_DIR=../metionine_filter/resultados/Alineamientos_M_Previa
    REVISION_DIR=../metionine_filter/resultados/Alineamientos_Revision_Manual
    MULTIFRAME_DIR=../metionine_filter/resultados/Alineamientos_Multiframe_Filtrados

    echo "$(date): Construyendo csv de secuencias"

    CSV_ini=./csv_n-id-seq
    FASTA_ini=./fasta-preBlast_signal
    mkdir -p $CSV_ini
    mkdir -p $FASTA_ini

    python3 $SFP1 $PERFECTOS_DIR $CSV_ini/perfectos.csv True
    python3 $SFP1 $MPREVIA_DIR $CSV_ini/mprevia.csv True
    python3 $SFP1 $MULTIFRAME_DIR $CSV_ini/multiframe.csv False
    python3 $SFP1 $REVISION_DIR $CSV_ini/revision_manual.csv False

    echo "$(date): Construyendo fasta de secuencias"
    python3 $SFP2 $CSV_ini/perfectos.csv $FASTA_ini/perfectos.fasta
    python3 $SFP2 $CSV_ini/mprevia.csv $FASTA_ini/mprevia.fasta
    python3 $SFP2 $CSV_ini/multiframe.csv $FASTA_ini/multiframe.fasta
    python3 $SFP2 $CSV_ini/revision_manual.csv $FASTA_ini/revision_manual.fasta

    # Carga el módulo BLAST+ si es necesario
    # module load BLAST+/2.13.0-gompi-2022a

    # Directorio de salida para los archivos CSV
    SIGNAL_OUT=./blast_signal_out

    # Crea el directorio de salida si no existe
    mkdir -p $SIGNAL_OUT


    # Ejecuta el primer blastp
    echo "$(date): iniciando primer blastp"
    if [ -s $FASTA_ini/perfectos.fasta ]; then
        blastp -query $FASTA_ini/perfectos.fasta -db $DB2 -evalue 1e-6 -outfmt 10 -out $SIGNAL_OUT/perfectos.csv -num_threads 4
    else
        echo "$FASTA_ini/perfectos.fasta está vacío. Creando archivo de salida vacío."
        touch $SIGNAL_OUT/perfectos.csv
    fi

    if [ -s $FASTA_ini/mprevia.fasta ]; then
        blastp -query $FASTA_ini/mprevia.fasta -db $DB2 -evalue 1e-6 -outfmt 10 -out $SIGNAL_OUT/mprevia.csv -num_threads 4
    else
        echo "$FASTA_ini/mprevia.fasta está vacío. Creando archivo de salida vacío."
        touch $SIGNAL_OUT/mprevia.csv
    fi

    if [ -s $FASTA_ini/multiframe.fasta ]; then
        blastp -query $FASTA_ini/multiframe.fasta -db $DB2 -evalue 1e-6 -outfmt 10 -out $SIGNAL_OUT/multiframe.csv -num_threads 4
    else
        echo "$FASTA_ini/multiframe.fasta está vacío. Creando archivo de salida vacío."
        touch $SIGNAL_OUT/multiframe.csv
    fi

    echo "$(date): Resultados guardados en $SIGNAL_OUT"


    # Procesar resultado blast
    echo "$(date): procesando resultados de blast"

    python3 $SFP3 $SIGNAL_OUT/perfectos.csv $CSV_ini/perfectos.csv $SIGNAL_OUT
    python3 $SFP3 $SIGNAL_OUT/mprevia.csv $CSV_ini/mprevia.csv $SIGNAL_OUT
    python3 $SFP3 $SIGNAL_OUT/multiframe.csv $CSV_ini/multiframe.csv $SIGNAL_OUT

    echo "$(date): creando nuevos ficheros fasta para el segundo blast"

    FASTA_post=./fasta-postBlast_signal
    mkdir -p $FASTA_post

    python3 $SFP4 $SIGNAL_OUT/perfectos_SF.csv $CSV_ini/perfectos.csv $FASTA_post
    python3 $SFP4 $SIGNAL_OUT/perfectos_NoSF.csv $CSV_ini/perfectos.csv $FASTA_post

    python3 $SFP4 $SIGNAL_OUT/mprevia_SF.csv $CSV_ini/mprevia.csv $FASTA_post
    python3 $SFP4 $SIGNAL_OUT/mprevia_NoSF.csv $CSV_ini/mprevia.csv $FASTA_post

    python3 $SFP4 $SIGNAL_OUT/multiframe_SF.csv $CSV_ini/multiframe.csv $FASTA_post
    python3 $SFP4 $SIGNAL_OUT/multiframe_NoSF.csv $CSV_ini/multiframe.csv $FASTA_post

    echo "$(date): nuevos ficheros fasta creados para el segundo blast"

    BLAST_OUT=./blast_out
    mkdir -p $BLAST_OUT


    # Ejecuta segundo blastp
    echo "$(date): iniciando segundo blastp"
    # Verificar y ejecutar blastp solo si el archivo no está vacío
    if [ -s $FASTA_post/perfectos_SF.fasta ]; then
        blastp -query $FASTA_post/perfectos_SF.fasta -db $DB3 -evalue 1e-6 -outfmt 10 -out $BLAST_OUT/perfectos_SF.csv -num_threads 4
    else
        echo "$FASTA_post/perfectos_SF.fasta está vacío. Creando archivo de salida vacío."
        touch $BLAST_OUT/perfectos_SF.csv
    fi

    if [ -s $FASTA_post/perfectos_NoSF.fasta ]; then
        blastp -query $FASTA_post/perfectos_NoSF.fasta -db $DB3 -evalue 1e-6 -outfmt 10 -out $BLAST_OUT/perfectos_NoSF.csv -num_threads 4
    else
        echo "$FASTA_post/perfectos_NoSF.fasta está vacío. Creando archivo de salida vacío."
        touch $BLAST_OUT/perfectos_NoSF.csv
    fi

    if [ -s $FASTA_post/mprevia_SF.fasta ]; then
        blastp -query $FASTA_post/mprevia_SF.fasta -db $DB3 -evalue 1e-6 -outfmt 10 -out $BLAST_OUT/mprevia_SF.csv -num_threads 4
    else
        echo "$FASTA_post/mprevia_SF.fasta está vacío. Creando archivo de salida vacío."
        touch $BLAST_OUT/mprevia_SF.csv
    fi

    if [ -s $FASTA_post/mprevia_NoSF.fasta ]; then
        blastp -query $FASTA_post/mprevia_NoSF.fasta -db $DB3 -evalue 1e-6 -outfmt 10 -out $BLAST_OUT/mprevia_NoSF.csv -num_threads 4
    else
        echo "$FASTA_post/mprevia_NoSF.fasta está vacío. Creando archivo de salida vacío."
        touch $BLAST_OUT/mprevia_NoSF.csv
    fi

    if [ -s $FASTA_post/multiframe_SF.fasta ]; then
        blastp -query $FASTA_post/multiframe_SF.fasta -db $DB3 -evalue 1e-6 -outfmt 10 -out $BLAST_OUT/multiframe_SF.csv -num_threads 4
    else
        echo "$FASTA_post/multiframe_SF.fasta está vacío. Creando archivo de salida vacío."
        touch $BLAST_OUT/multiframe_SF.csv
    fi

    if [ -s $FASTA_post/multiframe_NoSF.fasta ]; then
        blastp -query $FASTA_post/multiframe_NoSF.fasta -db $DB3 -evalue 1e-6 -outfmt 10 -out $BLAST_OUT/multiframe_NoSF.csv -num_threads 4
    else
        echo "$FASTA_post/multiframe_NoSF.fasta está vacío. Creando archivo de salida vacío."
        touch $BLAST_OUT/multiframe_NoSF.csv
    fi

    if [ -s $FASTA_ini/revision_manual.fasta ]; then
        blastp -query $FASTA_ini/revision_manual.fasta -db $DB3 -evalue 1e-6 -outfmt 10 -out $BLAST_OUT/revision_manual.csv -num_threads 4
    else
        echo "$FASTA_ini/revision_manual.fasta está vacío. Creando archivo de salida vacío."
        touch $BLAST_OUT/revision_manual.csv
    fi

    echo "$(date): Todos los blast han finalizado, iniciando procesamiento de los resultados"


    RESULTADOS=./resultados
    mkdir -p $RESULTADOS

    python3 $SFP5 $BLAST_OUT/perfectos_SF.csv $SIGNAL_OUT/perfectos_SF.csv $DB3 $CSV_ini/perfectos.csv $RESULTADOS/perfectos_SF.csv
    python3 $SFP5 $BLAST_OUT/perfectos_NoSF.csv $SIGNAL_OUT/perfectos_NoSF.csv $DB3 $CSV_ini/perfectos.csv $RESULTADOS/perfectos_NoSF.csv

    python3 $SFP5 $BLAST_OUT/mprevia_SF.csv $SIGNAL_OUT/mprevia_SF.csv $DB3 $CSV_ini/mprevia.csv $RESULTADOS/mprevia_SF.csv
    python3 $SFP5 $BLAST_OUT/mprevia_NoSF.csv $SIGNAL_OUT/mprevia_NoSF.csv $DB3 $CSV_ini/mprevia.csv $RESULTADOS/mprevia_NoSF.csv

    python3 $SFP5 $BLAST_OUT/multiframe_SF.csv $SIGNAL_OUT/multiframe_SF.csv $DB3 $CSV_ini/multiframe.csv $RESULTADOS/multiframe_SF.csv
    python3 $SFP5 $BLAST_OUT/multiframe_NoSF.csv $SIGNAL_OUT/multiframe_NoSF.csv $DB3 $CSV_ini/multiframe.csv $RESULTADOS/multiframe_NoSF.csv


    python3 $SFP6 $RESULTADOS/perfectos_SF.csv $RESULTADOS/perfectos_NoSF.csv $CSV_ini/perfectos.csv $RESULTADOS/perfectos_noMatch.csv
    python3 $SFP6 $RESULTADOS/mprevia_SF.csv $RESULTADOS/mprevia_NoSF.csv $CSV_ini/mprevia.csv $RESULTADOS/mprevia_noMatch.csv
    python3 $SFP6 $RESULTADOS/multiframe_SF.csv $RESULTADOS/multiframe_NoSF.csv $CSV_ini/multiframe.csv $RESULTADOS/multiframe_noMatch.csv

    echo "$(date): Resultados en csv obtenidos"

    echo "$(date): Iniciando la construccion de ficheros fasta de las secuencias NoSF"


    mkdir -p alineamientos_NoSF/perfectos/preMafft
    mkdir -p alineamientos_NoSF/perfectos/mafft
    mkdir -p alineamientos_NoSF/mprevia/preMafft
    mkdir -p alineamientos_NoSF/mprevia/mafft
    mkdir -p alineamientos_NoSF/multiframe/preMafft
    mkdir -p alineamientos_NoSF/multiframe/mafft
    mkdir -p alineamientos_NoSF/revision_manual/preMafft
    mkdir -p alineamientos_NoSF/revision_manual/mafft

    python3 $SFP7 $BLAST_OUT/perfectos_NoSF.csv $CSV_ini/perfectos.csv $DB3 alineamientos_NoSF/perfectos/preMafft
    python3 $SFP7 $BLAST_OUT/mprevia_NoSF.csv $CSV_ini/mprevia.csv $DB3 alineamientos_NoSF/mprevia/preMafft
    python3 $SFP7 $BLAST_OUT/multiframe_NoSF.csv $CSV_ini/multiframe.csv $DB3 alineamientos_NoSF/multiframe/preMafft
    python3 $SFP7 $BLAST_OUT/revision_manual.csv $CSV_ini/revision_manual.csv $DB3 alineamientos_NoSF/revision_manual/preMafft

    echo "$(date): Ficheros fasta creados creados"

    echo "$(date): Iniciando alineamientos mafft"

    # module load MAFFT

    for f in ./alineamientos_NoSF/perfectos/preMafft/*.fasta
    do
        base=$(basename $f)
        mafft --anysymbol $f > "./alineamientos_NoSF/perfectos/mafft/${base%.fasta}".mafft.fasta
    done


    for f in ./alineamientos_NoSF/mprevia/preMafft/*.fasta
    do
        base=$(basename $f)
        mafft --anysymbol $f > "./alineamientos_NoSF/mprevia/mafft/${base%.fasta}".mafft.fasta
    done

    for f in ./alineamientos_NoSF/multiframe/preMafft/*.fasta
    do
        base=$(basename $f)
        mafft --anysymbol $f > "./alineamientos_NoSF/multiframe/mafft/${base%.fasta}".mafft.fasta
    done

    for f in ./alineamientos_NoSF/revision_manual/preMafft/*.fasta
    do
        base=$(basename $f)
        mafft --anysymbol $f > "./alineamientos_NoSF/revision_manual/mafft/${base%.fasta}".mafft.fasta
    done

    # Remove newline characters within each sequence
    for f in ./alineamientos_NoSF/perfectos/mafft/*.fasta
    do
        awk 'BEGIN{p=0} /^>/ {if(p){printf("\n%s\n",$0);next;}else{p=1;printf("%s\n",$0);next;}} {printf("%s",$0);} END{printf("\n");}' $f > temp && mv temp $f
    done


    for f in ./alineamientos_NoSF/mprevia/mafft/*.fasta
    do
        awk 'BEGIN{p=0} /^>/ {if(p){printf("\n%s\n",$0);next;}else{p=1;printf("%s\n",$0);next;}} {printf("%s",$0);} END{printf("\n");}' $f > temp && mv temp $f
    done

    for f in ./alineamientos_NoSF/multiframe/mafft/*.fasta
    do
        awk 'BEGIN{p=0} /^>/ {if(p){printf("\n%s\n",$0);next;}else{p=1;printf("%s\n",$0);next;}} {printf("%s",$0);} END{printf("\n");}' $f > temp && mv temp $f
    done

    for f in ./alineamientos_NoSF/revision_manual/mafft/*.fasta
    do
        awk 'BEGIN{p=0} /^>/ {if(p){printf("\n%s\n",$0);next;}else{p=1;printf("%s\n",$0);next;}} {printf("%s",$0);} END{printf("\n");}' $f > temp && mv temp $f
    done

    echo "$(date): MAFFT finished"

    python3 $SFP8 $BLAST_OUT/revision_manual.csv $CSV_ini/revision_manual.csv $RESULTADOS/revision_manual_Match.csv $RESULTADOS/revision_manual_NoMatch.csv


    echo "$(date): Todos los ficheros csv movidos a $RESULTADOS"
    echo "Alineamientos disponibles en alineamientos_NoSF"

    # BUSCANDO ALINEAMIENTOS PARA LOS NO MATCH
    echo "$(date): Buscando alineamientos para los NoMATCH y Revision Manual MATCH en metionine filter"
    cd ./buscar_alineamientos_en_mfilter

    # Configuración de rutas
    FASTA_BASE_DIR="../../metionine_filter/resultados/" # Base de los subdirectorios de FASTA
    OUTPUT_DIR="./output/" # Directorio de salida
    PYTHON_SCRIPT="buscar_alineamientos.py" # Ruta al script Python
    MAX_SEQUENCES=8 # Número máximo de secuencias

    # Crear el directorio de salida si no existe
    mkdir -p "$OUTPUT_DIR"

    #module load Python/3.10.8-GCCcore-12.2.0
    #module load Biopython/1.79-foss-2021a

    # Procesar cada archivo CSV que contenga "Match.csv" en su nombre
    for csv_file in ../resultados/*Match.csv; do
        if [[ -f "$csv_file" ]]; then
            echo "Procesando $csv_file..."
            python3 "$PYTHON_SCRIPT" --csv "$csv_file" \
                                    --fasta_base_dir "$FASTA_BASE_DIR" \
                                    --output_dir "$OUTPUT_DIR" \
                                    --max_sequences "$MAX_SEQUENCES"
        fi
    done

    echo "$(date): Procesamiento completado. Resultados en $OUTPUT_DIR."

    echo "$(date): Ejecución de SF filter finalizada"

    cd ../..

    # QUANTIFICATION
    # Antes de ejecutar la sección de quantification, verifica si READ1 y READ2 están configurados
    if [[ -n $READ1 ]] && [[ -n $READ2 ]]; then

        echo "$(date): Ejecución de quantification iniciada"
        cd ./quantification

        QUANT_DIR="../trinity/trinity_out_dir/salmon_outdir"
        RESULTS_DIR="resultados"

        # Crear el directorio "resultados" si no existe
        if [ ! -d "$RESULTS_DIR" ]; then
            mkdir -p "$RESULTS_DIR"
            echo "Directorio de resultados $RESULTS_DIR creado."
        fi

        echo "$(date): Iniciando el procesamiento de CSVs con Python"

        # Llamar al script Python para procesar los CSVs y añadir el TPM
        #module purge
        #module load Python/3.10.8-GCCcore-12.2.0
        python3 ./python_scripts/tpm.py --quant_file "$QUANT_DIR/quant.sf" --results_dir "$RESULTS_DIR" --csv_dir "../superfamily/resultados"

        echo "$(date): Proceso completado. CSVs actualizados en quantification/resultados"

    else
        echo "Los READS no han sido proporcionados, no se puede realizar el cálculo de los niveles de expresión"
    fi

else
    echo "DB2 o DB3 no proporcionados, saltando la ejecución de SF filter y quantification."
fi

echo "$(date): Ejecución de Transcripto-filter finalizada"
