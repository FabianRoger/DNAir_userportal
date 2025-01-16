import os
import pandas as pd
from Bio import SeqIO

def validate_project_files(project_path):
    raw_data_path = os.path.join(project_path, "raw_data")
    errors = []
    
    # Check required files exist
    required_files = {
        'otu_table.txt': pd.read_csv,
        'metadata.txt': pd.read_csv,
        'tax_table.txt': pd.read_csv,
        'taxa_metadata.txt': pd.read_csv,
        'sequences.fasta': None  # Handle separately
    }
    
    for filename, reader_func in required_files.items():
        file_path = os.path.join(raw_data_path, filename)
        if not os.path.exists(file_path):
            errors.append(f"Missing file: {filename}")
            continue
            
        try:
            if filename.endswith('.fasta'):
                # Validate FASTA file
                with open(file_path) as f:
                    seqs = list(SeqIO.parse(f, 'fasta'))
                if len(seqs) == 0:
                    errors.append(f"Invalid FASTA file: {filename}")
            else:
                # Validate tab-separated text files
                df = reader_func(file_path, sep='\t')
                if len(df) == 0:
                    errors.append(f"Empty file: {filename}")
        except Exception as e:
            errors.append(f"Error reading {filename}: {str(e)}")
    
    if errors:
        print("Validation errors:")
        for error in errors:
            print(f"- {error}")
        return False
    
    print("All files validated successfully!")
    return True

if __name__ == "__main__":
    project_path = input("Enter project path: ")
    validate_project_files(project_path)