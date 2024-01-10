library(seqinr)

# file <- blast csv file.
# sequences <- fasta file with the contigs.
# proteins_db <- database in fasta format.
# directory <- name of the folder where you are going to save the fasta files.

create_sequences_groups <- function(file, sequences, proteins_db, directory){
# Read the csv file and create a vector with the sequences' and proteins' names.
print("Step 1/6. Reading the csv blast file to store the names of all contigs and proteins.")
data <- read.csv(file, header = F)
seqs_with_blast <- data[,1]
seqs_unique_with_blast <- unique(seqs_with_blast)
proteins_names <- as.character(data[,2])

# Create the vector with the names for the list.
print("Step 2/6. Creating a list of vectors.")
seqs_final <- c()
for(i in 1:length(seqs_unique_with_blast)){
        group <- paste("seq_", i, sep="")
        seqs_final <- c(seqs_final, group)
}

# Create a list, as long as the number of unique sequences, with the previous names.
my_list <- vector("list", length(seqs_final))
names(my_list) <- seqs_final

# Create a group of sequences' names with the contig-query and the similar proteins.
print("Step 3/6. Storing, in each vector of the list, one contig and its reference proteins.")
for(seqs_uniq in seqs_unique_with_blast){
        count <- 0
        proteins_indices <- c()
        x <- match(c(seqs_uniq), seqs_unique_with_blast)
        my_list[[x]] <- c(seqs_uniq)

        for(seqs_total in seqs_with_blast){
                count <- count + 1
                if(seqs_uniq==seqs_total){
                        proteins_indices <- c(proteins_indices, count)
                }
        }
        my_list[[x]] <- c(my_list[[x]], proteins_names[proteins_indices])
}

# Read the fasta files containing the contigs and the reference proteins.
print("Step 4/6. Reading the fasta files containing the contigs and the proteins sequences.")
contigs <- read.fasta(sequences, as.string = TRUE)
contigs_names <- names(contigs)

proteins <- read.fasta(proteins_db, as.string = TRUE)
proteins_names <- names(proteins)

my_proteins <- vector("list", length(seqs_final))
names(my_proteins) <- seqs_final

# Find all the sequences in the fasta files.
print("Step 5/6. Saving, in each vector, the contig sequences and their reference protein sequences.")
# Find contigs and add them to each group.
print("     First the contigs.")
print("          Translating...")
for(seqs in 1:length(contigs_names)){
        #print(seqs)
        x1 <- getTrans(contigs[seqs], sens="F", ambiguous = TRUE, frame = 0, numcode = 1)
        xx1 <- paste(x1[[1]], sep="", collapse="")
        names(xx1) <- c(paste(names(contigs[seqs]), "_", "Frame_F1", sep=""))
        #print(xx1)
        x2 <- getTrans(contigs[seqs], sens="F", ambiguous = TRUE, frame = 1, numcode = 1)
        xx2 <- paste(x2[[1]], sep="", collapse="")
        names(xx2) <- c(paste(names(contigs[seqs]), "_", "Frame_F2", sep=""))
        #print(xx2)
        x3 <- getTrans(contigs[seqs], sens="F", ambiguous = TRUE, frame = 2, numcode = 1)
        xx3 <- paste(x3[[1]], sep="", collapse="")
        names(xx3) <- c(paste(names(contigs[seqs]), "_", "Frame_F3", sep=""))
        #print(xx3)
        x4 <- getTrans(contigs[seqs], sens="R", ambiguous = TRUE, frame = 0, numcode = 1)
        xx4 <- paste(x4[[1]], sep="", collapse="")
        names(xx4) <- c(paste(names(contigs[seqs]), "_", "Frame_R1", sep=""))
        #print(xx4)
        x5 <- getTrans(contigs[seqs], sens="R", ambiguous = TRUE, frame = 1, numcode = 1)
        xx5 <- paste(x5[[1]], sep="", collapse="")
        names(xx5) <- c(paste(names(contigs[seqs]), "_", "Frame_R2", sep=""))
        #print(xx5)
        x6 <- getTrans(contigs[seqs], sens="R", ambiguous = TRUE, frame = 2, numcode = 1)
        xx6 <- paste(x6[[1]], sep="", collapse="")
        names(xx6) <- c(paste(names(contigs[seqs]), "_", "Frame_R3", sep=""))
        #print(xx6)

        my_proteins[[seqs]] <- c(my_proteins[[seqs]], contigs[seqs], xx1, xx2, xx3, xx4, xx5, xx6)
        #print(my_proteins[[seqs]])
        #print("--------------------------")
}

# Find proteins and add them to their respectives groups-
print("     Now the proteins.")
count2 <- 0
for(protein_groups in my_list){
        count2 <- count2 + 1
        for(seq in protein_groups){
                count_2 <- 0
                prot_indices <- c()
                for(prot in proteins_names){
                        count_2 <- count_2 + 1
                        if(prot==seq){
                                prot_indices <- c(prot_indices, count_2)
                                my_proteins[[count2]] <- c(my_proteins[[count2]], proteins[prot_indices])
                        }
                }
        }
}

# Create a fasta file for each of the groups in the list in the directory folder.
print("Step 6/6. Saving a fasta file for each one of the sequences groups in the directory folder.")
path <- getwd()

setwd(paste(path, "/", directory, sep=""))
count <- 0
for(groups in my_proteins){
        count <- count + 1
        write.fasta(groups, names(groups), file.out = paste(seqs_final[count], ".fasta", sep=""))
}
setwd(path)
print("The job has finished successfully. The fasta files have been created.")
}

# Get command line arguments
args <- commandArgs(trailingOnly = TRUE)

file <- args[1]
sequences <- args[2]
proteins_db <- args[3]
directory <- args[4]

# Run function
create_sequences_groups(file, sequences, proteins_db, directory)
