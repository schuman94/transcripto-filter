#!/bin/bash
#SBATCH --job-name=clean
#SBATCH --output=clean.out
#SBATCH --error=clean.err

# Directorio de trabajo
WORK_DIR="."

# Subdirectorios a limpiar
ALIGNMENTS_DIR="$WORK_DIR/alignments"
BLASTX_DIR="$WORK_DIR/blastx"
BUSCO_DIR="$WORK_DIR/busco"
CURATION_FILTER_DIR="$WORK_DIR/curation_filter"
FASTQC_DIR="$WORK_DIR/fastqc"
METIONINE_FILTER_DIR="$WORK_DIR/metionine_filter"
SUPERFAMILY_DIR="$WORK_DIR/superfamily"
TRINITY_DIR="$WORK_DIR/trinity"

# Variables para omitir limpieza en FASTQC, TRINITY y BUSCO
SKIP=true

# Procesar opciones de línea de comandos
while [[ "$#" -gt 0 ]]; do
    case $1 in
        --all) SKIP=false ;;
        *) echo "Opción desconocida: $1" ;;
    esac
    shift
done

# Función para limpiar un directorio, manteniendo solo los archivos .sh y opcionalmente un subdirectorio
clean_directory_except_sh_and_optional_subdir() {
    local dir=$1
    local subdir=$2
    echo "Limpiando $dir ..."
    if [ -z "$subdir" ]; then
        find "$dir" -mindepth 1 -maxdepth 1 ! -name '*.sh' -exec rm -rf {} +
    else
        find "$dir" -mindepth 1 -maxdepth 1 ! -name '*.sh' ! -name "$subdir" -exec rm -rf {} +
    fi
}

# Limpiar el directorio alignments, manteniendo archivos .sh y la carpeta RScripts
clean_directory_except_sh_and_optional_subdir "$ALIGNMENTS_DIR" "RScripts"

# Limpiar los otros directorios
clean_directory_except_sh_and_optional_subdir "$BLASTX_DIR"
if [ "$SKIP" = false ]; then
    clean_directory_except_sh_and_optional_subdir "$BUSCO_DIR"
    clean_directory_except_sh_and_optional_subdir "$FASTQC_DIR"
    clean_directory_except_sh_and_optional_subdir "$TRINITY_DIR"
else
    echo "Omitiendo limpieza de los directorios $BUSCO_DIR, $FASTQC_DIR y $TRINITY_DIR"
fi
clean_directory_except_sh_and_optional_subdir "$CURATION_FILTER_DIR" "python_scripts"
clean_directory_except_sh_and_optional_subdir "$METIONINE_FILTER_DIR" "python_scripts"
clean_directory_except_sh_and_optional_subdir "$SUPERFAMILY_DIR" "python_scripts"

# Eliminar archivos específicos en el directorio de trabajo
echo "Eliminando archivos t-filter.err y t-filter.out en el directorio de trabajo ..."
rm -f "$WORK_DIR/t-filter.err" "$WORK_DIR/t-filter.out"

echo "Limpieza completada."
