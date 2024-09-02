#!/bin/bash
#SBATCH --job-name=combine
#SBATCH --output=combine.out
#SBATCH --error=combine.err

# Procesar argumentos
while [[ $# -gt 0 ]]; do
    key="$1"

    case $key in
        --r1a)
            R1A=$(realpath "$2")
            shift
            ;;
        --r1b)
            R1B=$(realpath "$2")
            shift
            ;;
        --r2a)
            R2A=$(realpath "$2")
            shift
            ;;
        --r2b)
            R2B=$(realpath "$2")
            shift
            ;;
        *)
            echo "Argumento no reconocido: $key"
            exit 1
    esac
    shift
done

# Verificar que todos los argumentos hayan sido proporcionados
if [ -z "$R1A" ] || [ -z "$R1B" ] || [ -z "$R2A" ] || [ -z "$R2B" ]; then
    echo "Faltan argumentos. Uso: sbatch combine.sh --r1a /path/read1a --r1b /path/read1b --r2a /path/read2a --r2b /path/read2b"
    exit 1
fi

# Fusionar los archivos forward (lecturas 1)
zcat "$R1A" "$R1B" > combined_read1.fq

# Fusionar los archivos reverse (lecturas 2)
zcat "$R2A" "$R2B" > combined_read2.fq

# Comprimir los archivos fusionados
gzip combined_read1.fq
gzip combined_read2.fq

# Eliminar los archivos intermedios
rm combined_read1.fq
rm combined_read2.fq

echo "Los reads han sido combinados correctamente"
