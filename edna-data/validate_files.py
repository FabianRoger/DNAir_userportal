#!/usr/bin/env python3
import os
import pandas as pd
from Bio import SeqIO
import argparse
from pathlib import Path

class ProjectValidator:
    def __init__(self, user_name: str, project_name: str):
        self.project_path = Path("users") / user_name / project_name
        self.raw_data_path = self.project_path / "raw_data"
        self.errors = []
        self.warnings = []

    def validate_file_exists(self, filename: str) -> bool:
        """Check if required file exists."""
        if not (self.raw_data_path / filename).exists():
            self.errors.append(f"Missing required file: {filename}")
            return False
        return True

    def validate_csv_file(self, filename: str, required_columns: list = None):
        """Validate CSV/TSV file format and content."""
        if not self.validate_file_exists(filename):
            return False
        
        try:
            df = pd.read_csv(self.raw_data_path / filename, sep='\t')
            if df.empty:
                self.errors.append(f"File is empty: {filename}")
                return False
            
            if required_columns:
                missing_cols = [col for col in required_columns if col not in df.columns]
                if missing_cols:
                    self.errors.append(f"Missing required columns in {filename}: {missing_cols}")
                    return False
            
            return True
        except Exception as e:
            self.errors.append(f"Error reading {filename}: {str(e)}")
            return False

    def validate_fasta_file(self, filename: str):
        """Validate FASTA file format and content."""
        if not self.validate_file_exists(filename):
            return False
        
        try:
            with open(self.raw_data_path / filename) as f:
                sequences = list(SeqIO.parse(f, 'fasta'))
                if not sequences:
                    self.errors.append(f"No valid sequences found in {filename}")
                    return False
                return True
        except Exception as e:
            self.errors.append(f"Error reading {filename}: {str(e)}")
            return False

    def validate_project(self):
        """Validate all project files and structure."""
        # Check project structure
        for directory in ["raw_data", "processed_data", "results"]:
            if not (self.project_path / directory).is_dir():
                self.errors.append(f"Missing required directory: {directory}")

        # Validate OTU table
        self.validate_csv_file('otu_table.txt')

        # Validate metadata
        self.validate_csv_file('metadata.txt', 
                             ['SampleID', 'Latitude', 'Longitude', 'SamplingTime'])

        # Validate taxonomy table
        self.validate_csv_file('tax_table.txt',
                             ['OTU', 'Kingdom', 'Phylum', 'Class', 'Order', 'Family', 'Genus', 'Species'])

        # Validate taxa metadata
        self.validate_csv_file('taxa_metadata.txt',
                             ['Species', 'RedListStatus', 'InvasionStatus'])

        # Validate sequences
        self.validate_fasta_file('sequences.fasta')

        return len(self.errors) == 0

def main():
    parser = argparse.ArgumentParser(description="Validate eDNA project files")
    parser.add_argument("--user", required=True, help="User name")
    parser.add_argument("--project", required=True, help="Project name")
    
    args = parser.parse_args()
    
    validator = ProjectValidator(args.user, args.project)
    is_valid = validator.validate_project()
    
    if validator.errors:
        print("\nValidation errors:")
        for error in validator.errors:
            print(f"❌ {error}")
    
    if validator.warnings:
        print("\nWarnings:")
        for warning in validator.warnings:
            print(f"⚠️ {warning}")
    
    if is_valid:
        print("\n✅ Project validation successful!")
    else:
        print("\n❌ Project validation failed!")
        exit(1)

if __name__ == "__main__":
    main()