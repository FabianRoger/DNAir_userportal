from app.models import models
from sqlalchemy.orm import Session
import pandas as pd
from typing import Dict, List
from datetime import datetime
from Bio import SeqIO
from io import StringIO

class DataProcessor:
    def __init__(self, db: Session, storage):
        self.db = db
        self.storage = storage

    async def process_project_data(
        self,
        project_id: int,
        file_paths: Dict[str, str]
    ):
        """Process all project data files and store in database."""
        # Read files from Cloud Storage
        otu_df = await self.storage.read_file(file_paths['otu_table.txt'])
        metadata_df = await self.storage.read_file(file_paths['metadata.txt'])
        tax_df = await self.storage.read_file(file_paths['tax_table.txt'])
        taxa_metadata_df = await self.storage.read_file(file_paths['taxa_metadata.txt'])
        sequences = await self.storage.read_file(file_paths['sequences.fasta'], 'fasta')

        # Process samples and metadata
        await self._process_samples(project_id, metadata_df)
        
        # Process OTUs and sequences
        await self._process_otus(project_id, sequences)
        
        # Process OTU counts
        await self._process_otu_counts(project_id, otu_df)
        
        # Process taxonomy
        await self._process_taxonomy(project_id, tax_df)
        
        # Process species metadata
        await self._process_species_metadata(project_id, taxa_metadata_df)

    async def _process_samples(self, project_id: int, metadata_df: pd.DataFrame):
        """Process sample metadata and store in database."""
        for _, row in metadata_df.iterrows():
            sample = models.Sample(
                project_id=project_id,
                name=row['sample_id'],
                collection_date=datetime.strptime(row['date'], '%Y-%m-%d'),
                latitude=row.get('latitude'),
                longitude=row.get('longitude'),
                environmental_data={
                    k: v for k, v in row.items() 
                    if k not in ['sample_id', 'date', 'latitude', 'longitude']
                }
            )
            self.db.add(sample)
        self.db.commit()

    async def _process_otus(self, project_id: int, sequences: List):
        """Process OTU sequences and store in database."""
        for seq_record in sequences:
            otu = models.OTU(
                project_id=project_id,
                sequence_id=seq_record.id,
                sequence=str(seq_record.seq)
            )
            self.db.add(otu)
        self.db.commit()

    async def _process_otu_counts(self, project_id: int, otu_df: pd.DataFrame):
        """Process OTU counts and store in database."""
        # Get sample mapping
        samples = {
            s.name: s.id for s in 
            self.db.query(models.Sample).filter_by(project_id=project_id).all()
        }
        
        # Get OTU mapping
        otus = {
            o.sequence_id: o.id for o in 
            self.db.query(models.OTU).filter_by(project_id=project_id).all()
        }
        
        for otu_id in otu_df.index:
            for sample_name in otu_df.columns:
                count = otu_df.loc[otu_id, sample_name]
                if count > 0:  # Only store non-zero counts
                    otu_count = models.OTUCount(
                        sample_id=samples[sample_name],
                        otu_id=otus[otu_id],
                        count=count
                    )
                    self.db.add(otu_count)
        self.db.commit()

    async def _process_taxonomy(self, project_id: int, tax_df: pd.DataFrame):
        """Process taxonomy data and store in database."""
        otus = {
            o.sequence_id: o.id for o in 
            self.db.query(models.OTU).filter_by(project_id=project_id).all()
        }
        
        for seq_id, row in tax_df.iterrows():
            taxonomy = models.Taxonomy(
                otu_id=otus[seq_id],
                kingdom=row.get('kingdom'),
                phylum=row.get('phylum'),
                class_=row.get('class'),
                order=row.get('order'),
                family=row.get('family'),
                genus=row.get('genus'),
                species=row.get('species')
            )
            self.db.add(taxonomy)
        self.db.commit()

    async def _process_species_metadata(self, project_id: int, metadata_df: pd.DataFrame):
        """Process species metadata and store in database."""
        otus = {
            o.sequence_id: o.id for o in 
            self.db.query(models.OTU).filter_by(project_id=project_id).all()
        }
        
        for seq_id, row in metadata_df.iterrows():
            metadata = models.SpeciesMetadata(
                otu_id=otus[seq_id],
                status=row.get('status'),
                iucn_status=row.get('iucn_status'),
                habitat_type=row.get('habitat_type'),
                ecological_role=row.get('ecological_role'),
                additional_info={
                    k: v for k, v in row.items() 
                    if k not in ['status', 'iucn_status', 'habitat_type', 'ecological_role']
                }
            )
            self.db.add(metadata)
        self.db.commit()