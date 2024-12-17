#!/bin/bash

#SBATCH --job-name=samCreate
#SBATCH --output=sam.out
#SBATCH --error=sam.err
#SBATCH --cpus-per-task=4

# Mostrar ayuda
show_help() {
    echo "Previamente debes ejecutar: bowtie2-build trinity_out_dir.Trinity.fasta trinity_index"
    echo "Uso: sbatch sam.sh [opciones]"
    echo ""
    echo "Opciones:"
    echo "  --r1         Ruta al archivo de lecturas Read 1 (obligatorio)"
    echo "  --r2         Ruta al archivo de lecturas Read 2 (obligatorio)"
    echo "  -h|--help    Mostrar esta ayuda"
    exit 0
}

# Inicializar variables
R1=""
R2=""

# Procesar opciones
while [[ "$#" -gt 0 ]]; do
    case $1 in
        --r1) R1="$2"; shift 2;;
        --r2) R2="$2"; shift 2;;
        -h|--help) show_help;;
        *) echo "Opción desconocida: $1"; show_help;;
    esac
done

# Verificar que las variables obligatorias no estén vacías
if [[ -z "$R1" || -z "$R2" ]]; then
    echo "Error: Las opciones --r1 y --r2 son obligatorias."
    show_help
fi

# Comprobar si existe al menos un archivo que comience con "trinity_index"
if ! ls trinity_index* 1> /dev/null 2>&1; then
    echo "Primero debes ejecutar: bowtie2-build trinity_out_dir.Trinity.fasta trinity_index"
    exit 1
fi

# Cargar módulo de Bowtie2
module load Bowtie2/2.3.5.1-GCC-8.3.0

# Ejecutar Bowtie2 para el alineamiento
echo "Ejecutando Bowtie2 para alinear $R1 y $R2 en $(date)"
bowtie2 -x trinity_index -1 "$R1" -2 "$R2" -S output.sam
if [[ $? -ne 0 ]]; then
    echo "Error en el alineamiento de Bowtie2."
    exit 1
fi

echo "El archivo output.sam ha sido creado exitosamente en $(date)"
