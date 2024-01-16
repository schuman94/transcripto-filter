# Transcripto-filter: Flujo de trabajo de análisis de transcriptomas y filtrado de péptidos adaptado a un clúster de supercomputación

## Descripción
Esta herramienta bioinformática está diseñada para obtener alineamientos de péptidos a partir de reads. El proceso incluye varios pasos como la instalación y conexión con Bitvise SSH Client, preparación del directorio de trabajo, análisis de calidad con FastQC, ensamblaje con Trinity, entre otros.

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
8. **Filtrado de Alineamientos**: Filtra los alineamientos para obtener los más relevantes.

## Contribuciones
Las contribuciones a este proyecto son bienvenidas. Por favor, lee las guías de contribución para más información.

## Licencia
Este proyecto se distribuye bajo la licencia GPL-3.0

## Contacto
Para más información o soporte, contacta a Sergio en sergiochm94@gmail.com
