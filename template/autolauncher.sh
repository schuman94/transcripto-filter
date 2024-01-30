#!/bin/bash

# Verificar si se proporcionaron tres argumentos
if [ "$#" -ne 3 ]; then
    echo "Uso: $0 <Read1> <Read2> <DB>"
    exit 1
fi

# Asignar los argumentos a variables para mayor claridad
READ1=$(realpath $1)
READ2=$(realpath $2)
DB=$(realpath $3)

# Función para verificar si el ID del trabajo es un número
is_number() {
    [[ $1 =~ ^[0-9]+$ ]]
}

# Lanzar los trabajos y verificar que se obtenga un ID de trabajo válido
launch_job() {
    JOB=$(sbatch "$@" | awk '{print $4}')
    if is_number $JOB; then
        echo "Job ID: $JOB"
    else
        echo "Error: no se pudo obtener el ID del trabajo."
        exit 1
    fi
}

# FASTQC
cd ./fastqc
launch_job fastqc.sh "$READ1" "$READ2"
cd ..

# TRINITY
cd ./trinity
launch_job trinity.sh "$READ1" "$READ2" --dependency=afterok:$JOB
cd ..

# BUSCO
cd ./busco
TRINITY_FASTA=../trinity/trinity_out_dir.Trinity.fasta
launch_job busco.sh "TRINITY_FASTA" --dependency=afterok:$JOB
cd ..

# BLASTX
cd ./blastx
launch_job blastx.sh "$DB" --dependency=afterok:$JOB
cd ..

# ALIGNMENTS
cd ./alignments
BLAST_CSV=../blastx/blastx_out.csv
TRINITY_FASTA=../trinity/trinity_out_dir.Trinity.fasta
launch_job alignments.sh "$BLAST_CSV" "$TRINITY_FASTA" "$DB" --dependency=afterok:$JOB
cd ..

# CURATION FILTER
cd ./curation_filter
launch_job filter.sh --dependency=afterok:$JOB
cd ..

# METIONINE FILTER
cd ./metionine_filter
launch_job filter.sh --dependency=afterok:$JOB
cd ..
