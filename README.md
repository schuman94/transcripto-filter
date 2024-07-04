# Transcripto-filter: Flujo de trabajo automatizado para el análisis de transcriptomas y filtrado de péptidos adaptado a un entorno de supercomputación con SLURM

## Descripción
Esta herramienta bioinformática está diseñada para obtener alineamientos de péptidos a partir de reads procedentes de la secuenciación de ARN. El proceso incluye varios pasos como el análisis de calidad con FastQC, ensamblaje con Trinity, detección de alineamientos frente a una base de datos con BLAST y filtrado de alineamientos mediante diferentes scripts.

La herramienta está optimizada para el análisis de péptidos procedentes cónidos (Conidae) y su clasificación por superfamilias de conotoxinas.

## Instalación
Antes de comenzar, asegúrate de tener instalado lo siguiente:
- Bitvise SSH Client
- FastQC
- Trinity
- BUSCO
- BLASTX

## Uso
1. **Conexión SSH**: Utiliza Bitvise SSH Client para conectarte al servidor.
2. **Preparación del Directorio**: Crea y configura tu directorio de trabajo en el clúster.
3. **Análisis de Calidad**: Usa FastQC para analizar la calidad de tus reads.
4. **Ensamblaje con Trinity**: Realiza el ensamblaje de secuencias para obtener un fichero fasta.
5. **Control de Calidad con BUSCO**: Verifica la calidad del ensamblaje con BUSCO.
6. **Uso de BLASTX**: Compara las secuencias con una base de datos de péptidos.
7. **Extracción de Alineamientos**: Extrae los alineamientos relevantes.
8. **Filtrado de Alineamientos**: Filtra los alineamientos para obtener los más relevantes. Este paso incluye los filtros: curation-filter y metionine-filter.
9. **Clasificación por superfamilias**: Clasifica las secuencias de péptidos en diferentes superfamilias atendiendo a una bases de datos personalizada.

## Licencia
Este proyecto se distribuye bajo la licencia GPL-3.0

## Contacto
Para más información o soporte, contacta a Sergio en sergiochm94@gmail.com
