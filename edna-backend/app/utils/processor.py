# app/utils/processor.py

import pandas as pd
import io
from app.models import models
from sqlalchemy.orm import Session
from typing import Dict
from datetime import datetime
from Bio import SeqIO
import logging

class DataProcessor:
    def __init__(self, db: Session, storage):
        self.db = db
        self.storage = storage
        logging.basicConfig(level=logging.DEBUG)

    async def clean_project_data(self, project_id: int):
        """Remove existing data for a project."""
        try:
            logging.debug(f"Cleaning existing data for project {project_id}")
            
            # Delete in the correct order to respect foreign key constraints
            self.db.query(models.SpeciesMetadata).join(models.OTU).filter(
                models.OTU.project_id == project_id
            ).delete(synchronize_session=False)
            
            self.db.query(models.OTUCount).join(models.OTU).filter(
                models.OTU.project_id == project_id
            ).delete(synchronize_session=False)
            
            self.db.query(models.Taxonomy).join(models.OTU).filter(
                models.OTU.project_id == project_id
            ).delete(synchronize_session=False)
            
            self.db.query(models.Sample).filter_by(project_id=project_id).delete()
            self.db.query(models.OTU).filter_by(project_id=project_id).delete()
            
            self.db.commit()
            logging.debug("Successfully cleaned existing project data")
            
        except Exception as e:
            logging.error(f"Error cleaning project data: {str(e)}")
            self.db.rollback()
            raise

    async def process_project_data(
        self,
        project_id: int,
        file_paths: Dict[str, str],
        force: bool = False
    ):
        """Process all project data files and store in database."""
        try:
            if force:
                logging.debug("Force flag set, cleaning existing data...")
                await self.clean_project_data(project_id)
            else:
                # Check if project has data
                has_data = self.db.query(models.OTU).filter_by(project_id=project_id).first() is not None
                if has_data:
                    raise ValueError("Project already has data. Use force=True to overwrite.")
            
            # Read files from Storage
            logging.debug("Reading files from storage...")
            
            # Read OTU table
            otu_content = await self.storage.read_file(file_paths['otu_table.txt'])
            otu_df = pd.read_csv(io.StringIO(otu_content.decode('utf-8')), sep='\t', index_col=0)
            logging.debug(f"OTU table shape: {otu_df.shape}")

            # Read metadata
            metadata_content = await self.storage.read_file(file_paths['metadata.txt'])
            metadata_df = pd.read_csv(io.StringIO(metadata_content.decode('utf-8')), sep='\t')
            logging.debug(f"Metadata shape: {metadata_df.shape}")

            # Read taxonomy table
            tax_content = await self.storage.read_file(file_paths['tax_table.txt'])
            tax_df = pd.read_csv(io.StringIO(tax_content.decode('utf-8')), sep='\t')
            logging.debug(f"Taxonomy table shape: {tax_df.shape}")

            # Read taxa metadata
            taxa_metadata_content = await self.storage.read_file(file_paths['taxa_metadata.txt'])
            taxa_metadata_df = pd.read_csv(io.StringIO(taxa_metadata_content.decode('utf-8')), sep='\t')
            logging.debug(f"Taxa metadata shape: {taxa_metadata_df.shape}")

            # Read sequences
            sequences_content = await self.storage.read_file(file_paths['sequences.fasta'])
            sequences = list(SeqIO.parse(io.StringIO(sequences_content.decode('utf-8')), 'fasta'))
            logging.debug(f"Number of sequences: {len(sequences)}")

            # Process each component
            logging.debug("Processing samples and metadata...")
            await self._process_samples(project_id, metadata_df)
            
            logging.debug("Processing OTUs and sequences...")
            await self._process_otus(project_id, sequences)
            
            logging.debug("Processing taxonomy...")
            await self._process_taxonomy(project_id, tax_df)
            
            logging.debug("Processing OTU counts...")
            await self._process_otu_counts(project_id, otu_df)
            
            logging.debug("Processing species metadata...")
            await self._process_species_metadata(project_id, taxa_metadata_df)

            logging.debug("All data processed successfully")

        except Exception as e:
            logging.error(f"Error processing data: {str(e)}")
            raise

    async def _process_samples(self, project_id: int, metadata_df: pd.DataFrame):
        """Process sample metadata and store in database."""
        try:
            for _, row in metadata_df.iterrows():
                sample = models.Sample(
                    project_id=project_id,
                    name=row['SampleID'],
                    collection_date=datetime.strptime(row['SamplingTime'], '%Y-%m-%d'),
                    latitude=float(row['Latitude']),
                    longitude=float(row['Longitude']),
                    environmental_data={
                        k: v for k, v in row.items() 
                        if k not in ['SampleID', 'SamplingTime', 'Latitude', 'Longitude']
                    }
                )
                self.db.add(sample)
            self.db.commit()
            logging.debug("Sample processing completed successfully")
        except Exception as e:
            logging.error(f"Error processing samples: {str(e)}")
            self.db.rollback()
            raise

    async def _process_otus(self, project_id: int, sequences: list):
        """Process OTU sequences and store in database."""
        try:
            logging.debug(f"Processing {len(sequences)} OTU sequences")
            for seq_record in sequences:
                sequence_id = seq_record.id
                logging.debug(f"Processing sequence: {sequence_id}")
                
                otu = models.OTU(
                    project_id=project_id,
                    sequence_id=sequence_id,
                    sequence=str(seq_record.seq)
                )
                self.db.add(otu)
            self.db.commit()
            logging.debug("OTU processing completed successfully")
        except Exception as e:
            logging.error(f"Error processing OTUs: {str(e)}")
            self.db.rollback()
            raise

    async def _process_taxonomy(self, project_id: int, tax_df: pd.DataFrame):
        """Process taxonomy data and store in database."""
        try:
            # Get OTU mapping
            otus = {
                o.sequence_id: o.id for o in 
                self.db.query(models.OTU).filter_by(project_id=project_id).all()
            }
            
            logging.debug(f"Processing taxonomy for {len(tax_df)} entries")
            logging.debug(f"Available OTUs: {list(otus.keys())}")
            logging.debug(f"Tax table OTUs: {tax_df['OTU'].tolist()}")
            
            for _, row in tax_df.iterrows():
                otu_id = otus.get(row['OTU'])
                if otu_id is None:
                    logging.warning(f"No matching OTU found for {row['OTU']}")
                    continue
                    
                taxonomy = models.Taxonomy(
                    otu_id=otu_id,
                    kingdom=row['Kingdom'],
                    phylum=row['Phylum'],
                    class_=row['Class'],
                    order=row['Order'],
                    family=row['Family'],
                    genus=row['Genus'],
                    species=row['Species']
                )
                self.db.add(taxonomy)
                
            self.db.commit()
            logging.debug("Taxonomy processing completed successfully")
            
        except Exception as e:
            logging.error(f"Error processing taxonomy: {str(e)}")
            logging.error(f"Available columns: {tax_df.columns.tolist()}")
            self.db.rollback()
            raise

    async def _process_otu_counts(self, project_id: int, otu_df: pd.DataFrame):
        """Process OTU counts and store in database."""
        try:
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
            
            logging.debug(f"Processing OTU counts. Samples: {len(samples)}, OTUs: {len(otus)}")
            logging.debug(f"OTU table index: {otu_df.index.tolist()}")
            
            for otu_id in otu_df.index:
                for sample_name in otu_df.columns:
                    count = otu_df.loc[otu_id, sample_name]
                    if count > 0:  # Only store non-zero counts
                        if otu_id not in otus:
                            logging.warning(f"OTU {otu_id} not found in database")
                            continue
                        if sample_name not in samples:
                            logging.warning(f"Sample {sample_name} not found in database")
                            continue
                            
                        otu_count = models.OTUCount(
                            sample_id=samples[sample_name],
                            otu_id=otus[otu_id],
                            count=int(count)
                        )
                        self.db.add(otu_count)
            self.db.commit()
            logging.debug("OTU counts processing completed successfully")
        except Exception as e:
            logging.error(f"Error processing OTU counts: {str(e)}")
            self.db.rollback()
            raise

    async def _process_species_metadata(self, project_id: int, metadata_df: pd.DataFrame):
        """Process species metadata and store in database."""
        try:
            # Get OTUs with their taxonomy for this project
            otu_taxa = self.db.query(models.OTU, models.Taxonomy).join(
                models.Taxonomy
            ).filter(
                models.OTU.project_id == project_id
            ).all()
            
            # Create mapping from species names to OTU IDs
            species_to_otu = {tax.species: otu.id for otu, tax in otu_taxa}
            
            logging.debug(f"Found {len(species_to_otu)} OTU-species mappings")
            logging.debug(f"Species to OTU mapping: {species_to_otu}")
            logging.debug(f"Available species in metadata: {metadata_df['Species'].tolist()}")
            
            # Process each species in the metadata
            for _, row in metadata_df.iterrows():
                species_name = row['Species']
                otu_id = species_to_otu.get(species_name)
                
                if otu_id is None:
                    logging.warning(f"No OTU found for species: {species_name}")
                    continue
                
                logging.debug(f"Processing metadata for species {species_name} (OTU ID: {otu_id})")
                
                metadata = models.SpeciesMetadata(
                    otu_id=otu_id,
                    status=row['InvasionStatus'],
                    iucn_status=row['RedListStatus'],
                    habitat_type=row['NativeStatus'],
                    additional_info={}
                )
                self.db.add(metadata)
                
            self.db.commit()
            logging.debug("Successfully processed all species metadata")
            
        except Exception as e:
            logging.error(f"Error processing species metadata: {str(e)}")
            self.db.rollback()
            raise