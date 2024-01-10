#!/bin/bash -x
#SBATCH --job-name=optimizacion
#SBATCH --output=optimizacion.out
#SBATCH --error=optimizacion.err

START_TIME=$(date +%s)
echo "Ejecución iniciada en: $(date)"

module load Python/3.10.8-GCCcore-12.2.0
module load Biopython/1.79-foss-2021a

# El directorio raíz de configuraciones y el directorio de alineamientos se pasan como argumentos
CONFIG_DIR_ROOT=$1 #Ejemplo: 1-400
ALIGNMENTS_ROOT_DIR=$2 #Ejemplo: TF36

# Verificar que se han proporcionado los directorios necesarios
if [ -z "$CONFIG_DIR_ROOT" ] || [ -z "$ALIGNMENTS_ROOT_DIR" ]; then
    echo "Error: No se especificaron los directorios necesarios."
    echo "Uso: sbatch run.sh /path/to/config_dir_root /path/to/alignments_root_dir"
    exit 1
fi

# Rutas de los scripts de Python
P1=./python_scripts/main.py
P2=./python_scripts/coincidencias.py

# Encontrar los subdirectorios requeridos
ALIGNMENTS_DIR=$(find $ALIGNMENTS_ROOT_DIR -type d -name "*_Alineamientos_reformat" | head -n 1)
ALIGNMENTS_SI=$(find $ALIGNMENTS_ROOT_DIR -type d -name "*_SI" | head -n 1)

if [ -z "$ALIGNMENTS_DIR" ] || [ -z "$ALIGNMENTS_SI" ]; then
    echo "Error: No se encontraron los subdirectorios requeridos dentro de $ALIGNMENTS_ROOT_DIR."
    exit 1
fi

echo "Usando el directorio de alineamientos: $ALIGNMENTS_DIR"
echo "Usando el directorio de alineamientos SI: $ALIGNMENTS_SI"

# Iterar sobre cada subdirectorio en el directorio raíz de configuraciones
for SUBDIR in $CONFIG_DIR_ROOT/*; do
    if [ -d "$SUBDIR" ] && [ -f "$SUBDIR/config.txt" ]; then
        echo "Ejecutando el script para la configuración en $SUBDIR..."

        # Directorios de salida para los alineamientos filtrados y las coincidencias
        ALIGNMENTS_FILTERED_DIR="$SUBDIR/filtered_alignments"
        COINCIDENCES_DIR="$SUBDIR/coincidencias"
        mkdir -p $COINCIDENCES_DIR

        # Ejecutar el script main.py
        python3 $P1 $ALIGNMENTS_DIR $ALIGNMENTS_FILTERED_DIR "$SUBDIR/config.txt" --no_report

        # Ejecutar el script coincidencias.py
        python3 $P2 $ALIGNMENTS_FILTERED_DIR $ALIGNMENTS_SI $ALIGNMENTS_DIR $COINCIDENCES_DIR
    fi
done

echo "Ejecución finalizada en: $(date)"
