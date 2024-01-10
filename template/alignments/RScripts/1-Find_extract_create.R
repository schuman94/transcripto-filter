library(seqinr)

find_extract_create <- function(initial_data, fasta_file, extracted_sequences, sequences_without_hit) {

        blast_csv <- read.csv(initial_data, header = F)
        sequences_with_hit <- as.character(unique(blast_csv[,1]))
        print(paste("There are ", length(blast_csv[,1]), " sequences, ",
                     length(sequences_with_hit), " different.", sep = ""))

        trinity_file <- read.fasta(fasta_file, as.string = TRUE)
        sequences_trinity <- names(trinity_file)
        loops <- 0
        vector_indices <- numeric()

        for(seq in sequences_with_hit){
                loops <- loops + 1
                percentage <- round((loops/length(sequences_with_hit) * 100), 3)
                completeness <- paste("More than ", as.character(percentage), "%",
                                      " of the comparisons have been completed. Just wait...", sep = "")
                A <- round((0.25*length(sequences_with_hit)), 0)
                B <- round((0.50*length(sequences_with_hit)), 0)
                C <- round((0.75*length(sequences_with_hit)), 0)
                D <- round((0.95*length(sequences_with_hit)), 0)
                if((loops==A)||(loops==B)||(loops==C)||(loops==D)){
                        print(completeness)
                }
                count <- 0
                for(sequence in sequences_trinity){
                        count <- count + 1
                        if(seq==sequence){
                                vector_indices <- c(vector_indices, count)
                        }
                }
        }

        print(paste(length(vector_indices), "sequences will be extracted.", sep=" "))

        extract_sequences <- trinity_file[vector_indices]
        no_hits_list <- trinity_file[-vector_indices]

        write.fasta(extract_sequences, names(extract_sequences), file.out = extracted_sequences, as.string = TRUE)
        write.fasta(no_hits_list, names(no_hits_list), file.out = sequences_without_hit, as.string = TRUE)

        print("The extraction has finished successfully. Enjoy your sequences!")
}

args <- commandArgs(trailingOnly = TRUE)

initial_data <- args[1]
fasta_file <- args[2]
extracted_sequences <- args[3]
sequences_without_hit <- args[4]

find_extract_create(initial_data, fasta_file, extracted_sequences, sequences_without_hit)
