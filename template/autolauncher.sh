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

# Lanzar los trabajos y devolver el ID de trabajo válido
launch_job() {
    local JOB_ID=$(sbatch "$@" | awk '{print $4}')
    if is_number $JOB_ID; then
        echo "Job ID: $JOB_ID"
        echo $JOB_ID
    else
        echo "Error: no se pudo obtener el ID del trabajo."
        exit 1
    fi
}

# FASTQC
cd ./fastqc
JOB_FASTQC=$(launch_job fastqc.sh "$READ1" "$READ2")
cd ..

# TRINITY
cd ./trinity
JOB_TRINITY=$(launch_job trinity.sh "$READ1" "$READ2" --dependency=afterok:$JOB_FASTQC)
cd ..

# BUSCO
cd ./busco
TRINITY_FASTA=../trinity/trinity_out_dir.Trinity.fasta
JOB_BUSCO=$(launch_job busco.sh "$TRINITY_FASTA" --dependency=afterok:$JOB_TRINITY)
cd ..

# BLASTX
cd ./blastx
JOB_BLASTX=$(launch_job blastx.sh "$DB" --dependency=afterok:$JOB_BUSCO)
cd ..

# ALIGNMENTS
cd ./alignments
BLAST_CSV=../blastx/blastx_out.csv
JOB_ALIGNMENTS=$(launch_job alignments.sh "$BLAST_CSV" "$TRINITY_FASTA" "$DB" --dependency=afterok:$JOB_BLASTX)
cd ..

# CURATION FILTER
cd ./curation_filter
JOB_CUR_FILTER=$(launch_job filter.sh --dependency=afterok:$JOB_ALIGNMENTS)
cd ..

# METIONINE FILTER
cd ./metionine_filter
JOB_MET_FILTER=$(launch_job filter.sh --dependency=afterok:$JOB_CUR_FILTER)
cd ..
