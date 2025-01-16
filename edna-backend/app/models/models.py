# app/models/models.py
from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Text, JSON, UniqueConstraint
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime

Base = declarative_base()

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True)
    name = Column(String)
    projects = relationship("Project", back_populates="user")

class Project(Base):
    __tablename__ = "projects"
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'))
    name = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)
    storage_path = Column(String)  # Path in Cloud Storage
    
    user = relationship("User", back_populates="projects")
    samples = relationship("Sample", back_populates="project")
    otus = relationship("OTU", back_populates="project")

class Sample(Base):
    __tablename__ = "samples"
    id = Column(Integer, primary_key=True)
    project_id = Column(Integer, ForeignKey('projects.id'))
    name = Column(String)
    collection_date = Column(DateTime)
    latitude = Column(Float)
    longitude = Column(Float)
    environmental_data = Column(JSON)  # Store environmental conditions
    
    project = relationship("Project", back_populates="samples")
    otu_counts = relationship("OTUCount", back_populates="sample")

class OTU(Base):
    __tablename__ = "otus"
    id = Column(Integer, primary_key=True)
    project_id = Column(Integer, ForeignKey('projects.id'))
    sequence_id = Column(String)  # Remove unique=True
    sequence = Column(Text)
    
    project = relationship("Project", back_populates="otus")
    taxonomy = relationship("Taxonomy", back_populates="otu", uselist=False)
    counts = relationship("OTUCount", back_populates="otu")
    species_info = relationship("SpeciesMetadata", back_populates="otu", uselist=False)

    # Make sequence_id unique only within a project
    __table_args__ = (
        UniqueConstraint('project_id', 'sequence_id', name='_project_sequence_uc'),
    )

class OTUCount(Base):
    __tablename__ = "otu_counts"
    id = Column(Integer, primary_key=True)
    sample_id = Column(Integer, ForeignKey('samples.id'))
    otu_id = Column(Integer, ForeignKey('otus.id'))
    count = Column(Integer)
    
    sample = relationship("Sample", back_populates="otu_counts")
    otu = relationship("OTU", back_populates="counts")

class Taxonomy(Base):
    __tablename__ = "taxonomy"
    id = Column(Integer, primary_key=True)
    otu_id = Column(Integer, ForeignKey('otus.id'))
    kingdom = Column(String)
    phylum = Column(String)
    class_ = Column(String)
    order = Column(String)
    family = Column(String)
    genus = Column(String)
    species = Column(String)
    
    otu = relationship("OTU", back_populates="taxonomy")

class SpeciesMetadata(Base):
    __tablename__ = "species_metadata"
    id = Column(Integer, primary_key=True)
    otu_id = Column(Integer, ForeignKey('otus.id'))
    status = Column(String)  # 'common', 'invasive', 'protected'
    iucn_status = Column(String)
    habitat_type = Column(String)
    ecological_role = Column(String)
    additional_info = Column(JSON)
    
    otu = relationship("OTU", back_populates="species_info")