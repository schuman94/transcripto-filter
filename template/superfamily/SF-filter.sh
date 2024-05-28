#!/bin/bash

#SBATCH --job-name=SF-filter
#SBATCH --output=SF-filter.out
#SBATCH --error=SF-filter.err
#SBATCH --cpus-per-task=4

echo "Ejecución de SF filter iniciada en: $(date)"

module load Python/3.10.8-GCCcore-12.2.0
module load Biopython/1.79-foss-2021a


# Python script path
P1=./python_scripts/alineamientosToCsv.py
P2=./python_scripts/csvToFasta.py
P3=./python_scripts/procesarCsvBlastSignal.py
P4=./python_scripts/csvSignalToFasta.py
P5=./python_scripts/procesarCsvBlastFinal.py
P6=./python_scripts/noMatch.py
P7=./python_scripts/extraerSeqsBlast.py
P8=./python_scripts/procesar_csv_revision_manual.py
P9=./python_scripts/description.py

PERFECTOS_DIR=../metionine_filter/resultados/Alineamientos_Perfectos
MPREVIA_DIR=../metionine_filter/resultados/Alineamientos_M_Previa
REVISION_DIR=../metionine_filter/resultados/Alineamientos_Revision_Manual

echo "Construyendo csv de secuencias"

CSV_ini=./csv_n-id-seq
FASTA_ini=./fasta-preBlast_signal

python3 $P1 $PERFECTOS_DIR $CSV_ini/perfectos.csv True
python3 $P1 $MPREVIA_DIR $CSV_ini/mprevia.csv True
python3 $P1 $REVISION_DIR $CSV_ini/revision_manual.csv False

echo "Construyendo fasta de secuencias"
python3 $P2 $CSV_ini/perfectos.csv $FASTA_ini/perfectos.fasta
python3 $P2 $CSV_ini/mprevia.csv $FASTA_ini/mprevia.fasta
python3 $P2 $CSV_ini/revision_manual.csv $FASTA_ini/revision_manual.fasta

# Carga el módulo BLAST+ si es necesario
module load BLAST+/2.13.0-gompi-2022a

# Directorio de salida para los archivos CSV
SIGNAL_OUT=./blast_signal_out

# Base de datos de péptidos señales
DB=$1

# Crea el directorio de salida si no existe
mkdir -p $SIGNAL_OUT

# Ejecuta el primer blastp
echo "iniciando primer blastp"
if [ -s $FASTA_ini/perfectos.fasta ]; then
    blastp -query $FASTA_ini/perfectos.fasta -db $DB -evalue 1e-6 -outfmt 10 -out $SIGNAL_OUT/perfectos.csv -num_threads 4
else
    echo "$FASTA_ini/perfectos.fasta está vacío. Creando archivo de salida vacío."
    touch $SIGNAL_OUT/perfectos.csv
fi

if [ -s $FASTA_ini/mprevia.fasta ]; then
    blastp -query $FASTA_ini/mprevia.fasta -db $DB -evalue 1e-6 -outfmt 10 -out $SIGNAL_OUT/mprevia.csv -num_threads 4
else
    echo "$FASTA_ini/mprevia.fasta está vacío. Creando archivo de salida vacío."
    touch $SIGNAL_OUT/mprevia.csv
fi

echo "Resultados guardados en $SIGNAL_OUT"

# Procesar resultado blast
echo "procesando resultados de blast"

python3 $P3 $SIGNAL_OUT/perfectos.csv $CSV_ini/perfectos.csv $SIGNAL_OUT
python3 $P3 $SIGNAL_OUT/mprevia.csv $CSV_ini/mprevia.csv $SIGNAL_OUT

echo "creando nuevos ficheros fasta para el segundo blast"

FASTA_post=./fasta-postBlast_signal

python3 $P4 $SIGNAL_OUT/perfectos_SF.csv $CSV_ini/perfectos.csv $FASTA_post
python3 $P4 $SIGNAL_OUT/perfectos_NoSF.csv $CSV_ini/perfectos.csv $FASTA_post

python3 $P4 $SIGNAL_OUT/mprevia_SF.csv $CSV_ini/mprevia.csv $FASTA_post
python3 $P4 $SIGNAL_OUT/mprevia_NoSF.csv $CSV_ini/mprevia.csv $FASTA_post

echo "nuevos ficheros fasta creados para el segundo blast"

BLAST_OUT=./blast_out
mkdir -p $BLAST_OUT

DB2=$2

# Ejecuta segundo blastp
echo "iniciando segundo blastp"
# Verificar y ejecutar blastp solo si el archivo no está vacío
if [ -s $FASTA_post/perfectos_SF.fasta ]; then
    blastp -query $FASTA_post/perfectos_SF.fasta -db $DB2 -evalue 1e-6 -outfmt 10 -out $BLAST_OUT/perfectos_SF.csv -num_threads 4
else
    echo "$FASTA_post/perfectos_SF.fasta está vacío. Creando archivo de salida vacío."
    touch $BLAST_OUT/perfectos_SF.csv
fi

if [ -s $FASTA_post/perfectos_NoSF.fasta ]; then
    blastp -query $FASTA_post/perfectos_NoSF.fasta -db $DB2 -evalue 1e-6 -outfmt 10 -out $BLAST_OUT/perfectos_NoSF.csv -num_threads 4
else
    echo "$FASTA_post/perfectos_NoSF.fasta está vacío. Creando archivo de salida vacío."
    touch $BLAST_OUT/perfectos_NoSF.csv
fi

if [ -s $FASTA_post/mprevia_SF.fasta ]; then
    blastp -query $FASTA_post/mprevia_SF.fasta -db $DB2 -evalue 1e-6 -outfmt 10 -out $BLAST_OUT/mprevia_SF.csv -num_threads 4
else
    echo "$FASTA_post/mprevia_SF.fasta está vacío. Creando archivo de salida vacío."
    touch $BLAST_OUT/mprevia_SF.csv
fi

if [ -s $FASTA_post/mprevia_NoSF.fasta ]; then
    blastp -query $FASTA_post/mprevia_NoSF.fasta -db $DB2 -evalue 1e-6 -outfmt 10 -out $BLAST_OUT/mprevia_NoSF.csv -num_threads 4
else
    echo "$FASTA_post/mprevia_NoSF.fasta está vacío. Creando archivo de salida vacío."
    touch $BLAST_OUT/mprevia_NoSF.csv
fi

if [ -s $FASTA_ini/revision_manual.fasta ]; then
    blastp -query $FASTA_ini/revision_manual.fasta -db $DB2 -evalue 1e-6 -outfmt 10 -out $BLAST_OUT/revision_manual.csv -num_threads 4
else
    echo "$FASTA_ini/revision_manual.fasta está vacío. Creando archivo de salida vacío."
    touch $BLAST_OUT/revision_manual.csv
fi

echo "Todos los blast han finalizado, iniciando procesamiento de los resultados"

RESULTADOS=./resultados
mkdir -p $RESULTADOS

python3 $P5 $BLAST_OUT/perfectos_SF.csv $SIGNAL_OUT/perfectos_SF.csv $DB2 $CSV_ini/perfectos.csv $RESULTADOS/perfectos_SF.csv
python3 $P5 $BLAST_OUT/perfectos_NoSF.csv $SIGNAL_OUT/perfectos_NoSF.csv $DB2 $CSV_ini/perfectos.csv $RESULTADOS/perfectos_NoSF.csv

python3 $P5 $BLAST_OUT/mprevia_SF.csv $SIGNAL_OUT/mprevia_SF.csv $DB2 $CSV_ini/mprevia.csv $RESULTADOS/mprevia_SF.csv
python3 $P5 $BLAST_OUT/mprevia_NoSF.csv $SIGNAL_OUT/mprevia_NoSF.csv $DB2 $CSV_ini/mprevia.csv $RESULTADOS/mprevia_NoSF.csv

python3 $P6 $RESULTADOS/perfectos_SF.csv $RESULTADOS/perfectos_NoSF.csv $CSV_ini/perfectos.csv $RESULTADOS/perfectos_noMatch.csv
python3 $P6 $RESULTADOS/mprevia_SF.csv $RESULTADOS/mprevia_NoSF.csv $CSV_ini/mprevia.csv $RESULTADOS/mprevia_noMatch.csv

echo "Resultados en csv obtenidos"

echo "Iniciando la construccion de ficheros fasta de las secuencias NoSF"


mkdir -p alineamientos_NoSF/perfectos/preMafft
mkdir -p alineamientos_NoSF/perfectos/mafft
mkdir -p alineamientos_NoSF/mprevia/preMafft
mkdir -p alineamientos_NoSF/mprevia/mafft
mkdir -p alineamientos_NoSF/revision_manual/preMafft
mkdir -p alineamientos_NoSF/revision_manual/mafft

python3 $P7 $BLAST_OUT/perfectos_NoSF.csv $CSV_ini/perfectos.csv $DB2 alineamientos_NoSF/perfectos/preMafft
python3 $P7 $BLAST_OUT/mprevia_NoSF.csv $CSV_ini/mprevia.csv $DB2 alineamientos_NoSF/mprevia/preMafft
python3 $P7 $BLAST_OUT/revision_manual.csv $CSV_ini/revision_manual.csv $DB2 alineamientos_NoSF/revision_manual/preMafft

echo "Ficheros fasta creados creados"

echo "Iniciando alineamientos mafft"

module load MAFFT

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


for f in ./alineamientos_NoSF/revision_manual/mafft/*.fasta
do
    awk 'BEGIN{p=0} /^>/ {if(p){printf("\n%s\n",$0);next;}else{p=1;printf("%s\n",$0);next;}} {printf("%s",$0);} END{printf("\n");}' $f > temp && mv temp $f
done

echo "MAFFT finished"

python3 $P8 $BLAST_OUT/revision_manual.csv $CSV_ini/revision_manual.csv $RESULTADOS/revision_manual_Match.csv $RESULTADOS/revision_manual_NoMatch.csv


echo "Todos los ficheros csv movidos a $RESULTADOS"
echo "Alineamientos disponibles en alineamientos_NoSF"

echo "Paso extra: Recuperando descripción de alineamientos antiguos en Metionine Filter"

DB3=$3

python3 $P9 ../metionine_filter/resultados/Alineamientos_Perfectos $DB3
python3 $P9 ../metionine_filter/resultados/Alineamientos_M_Previa $DB3
python3 $P9 ../metionine_filter/resultados/Alineamientos_Revision_Manual $DB3
python3 $P9 ../metionine_filter/resultados/Alineamientos_Multiframe $DB3

echo "Ejecución de SF filter finalizada en: $(date)"
