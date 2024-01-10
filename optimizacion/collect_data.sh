#!/bin/bash
#SBATCH --job-name=data_collection
#SBATCH --output=data_collection.out
#SBATCH --error=data_collection.err

# Cargar los módulos necesarios
module load Python/3.10.8-GCCcore-12.2.0

# Ruta al script de Python para recopilar datos
PYTHON_SCRIPT=python_scripts/collect_data.py

# Verificar si se ha proporcionado un directorio como argumento
if [ "$#" -ne 1 ]; then
    echo "Uso: $0 /path/to/directory"
    exit 1
fi

# El directorio raíz proporcionado como argumento
ROOT_DIR=$1 #Ejemplo TF36

# Ejecutar el script de Python
python3 $PYTHON_SCRIPT $ROOT_DIR

echo "Proceso de recopilación de datos completado."
