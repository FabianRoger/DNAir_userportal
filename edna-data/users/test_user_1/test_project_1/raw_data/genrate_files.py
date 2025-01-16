import pandas as pd
import random

# Generate OTU table
samples = [f"Station{i//15+1}_Day{(i%15)+1}" for i in range(45)]
otus = [f"OTU{i+1}" for i in range(50)]
otu_table = pd.DataFrame({otu: [random.randint(0, 100) for _ in samples] for otu in otus}, index=samples)
otu_table.to_csv("otu_table.txt", sep="\t")

# Generate metadata
metadata = pd.DataFrame({
    "SampleID": samples,
    "Latitude": [46.8182 + (i//15)*0.001 for i in range(45)],
    "Longitude": [8.2275 + (i//15)*0.001 for i in range(45)],
    "SamplingTime": [f"2023-01-{(i%15)+1:02d}" for i in range(45)],
    "Station": [f"Station{i//15+1}" for i in range(45)]
})
metadata.to_csv("metadata.txt", sep="\t", index=False)

# Generate sequences
with open("sequences.fasta", "w") as f:
    for i in range(50):
        f.write(f">OTU{i+1}\n")
        f.write("CGTAGGTGAACCTGCGGAAGGATCATTGTTGAGAAACTCAAACCTTTTGTTGATGGTCTTGGC\n")

# Generate tax table
taxa = [f"OTU{i+1}" for i in range(50)]
tax_table = pd.DataFrame({
    "OTU": taxa,
    "Kingdom": ["Plantae"]*50,
    "Phylum": ["Tracheophyta"]*50,
    "Class": ["Magnoliopsida"]*50,
    "Order": ["Asterales"]*50,
    "Family": ["Asteraceae"]*50,
    "Genus": [f"Genus{i+1}" for i in range(50)],
    "Species": [f"Species{i+1}" for i in range(50)]
})
tax_table.to_csv("tax_table.txt", sep="\t", index=False)

# Generate taxa metadata
taxa_metadata = pd.DataFrame({
    "Species": [f"Species{i+1}" for i in range(50)],
    "RedListStatus": ["LC"]*47 + ["VU", "EN", "CR"],  # 3 red-listed
    "InvasionStatus": ["Non-invasive"]*49 + ["Invasive"],  # 1 invasive
    "NativeStatus": ["Native"]*48 + ["Non-native"]*2  # 2 non-native
})
taxa_metadata.to_csv("taxa_metadata.txt", sep="\t", index=False)