# app/main.py
from fastapi import FastAPI, Depends, HTTPException, File, UploadFile
from sqlalchemy.orm import Session
from pydantic import BaseModel
from app.db.database import get_db
from app.models import models
from app.utils.storage import StorageService
from app.utils.processor import DataProcessor
from fastapi.middleware.cors import CORSMiddleware
from typing import List, Dict, Any

app = FastAPI()
storage = StorageService()

# Add CORS middleware configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://dnair-frontend-demo.web.app",
        "https://dnair-frontend-demo.firebaseapp.com",
        "http://localhost:3000",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Pydantic models
class UserCreate(BaseModel):
    name: str

class UserResponse(BaseModel):
    id: int
    name: str
    
    class Config:
        from_attributes = True

# API endpoints
@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy"}

@app.get("/users/", response_model=List[UserResponse])
async def get_users(db: Session = Depends(get_db)):
    """Get all users"""
    users = db.query(models.User).all()
    return users

@app.post("/users/", response_model=UserResponse)
async def create_user(user: UserCreate, db: Session = Depends(get_db)):
    """Create a new user"""
    # Check if the user already exists
    existing_user = db.query(models.User).filter(models.User.name == user.name).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="User already exists")
    
    # Create the user
    db_user = models.User(name=user.name)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

@app.get("/projects/{user_id}", response_model=List[Dict[str, Any]])
async def get_user_projects(user_id: int, db: Session = Depends(get_db)):
    """Get all projects for a user"""
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    projects = db.query(models.Project).filter(models.Project.user_id == user_id).all()
    return [{"id": p.id, "name": p.name, "created_at": p.created_at} for p in projects]

@app.post("/projects/{user_id}")
async def create_project(
    user_id: int,
    project_name: str,
    db: Session = Depends(get_db)
):
    """Create a new project for a user"""
    # Check if the user exists
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Create project in database
    project = models.Project(
        user_id=user_id,
        name=project_name
    )
    db.add(project)
    db.commit()
    db.refresh(project)
    return project

@app.get("/projects/{project_id}/data")
async def get_project_data(project_id: int, db: Session = Depends(get_db)):
    """Get project data including metrics and findings"""
    project = db.query(models.Project).filter(models.Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    # Get OTU data with taxonomy and metadata
    otus = db.query(models.OTU).filter(models.OTU.project_id == project_id).all()
    
    # Calculate metrics
    species_count = len(otus)
    invasive_species = db.query(models.SpeciesMetadata).join(models.OTU).filter(
        models.OTU.project_id == project_id,
        models.SpeciesMetadata.status == 'invasive'
    ).count()
    
    protected_species = db.query(models.SpeciesMetadata).join(models.OTU).filter(
        models.OTU.project_id == project_id,
        models.SpeciesMetadata.iucn_status.in_(['VU', 'EN', 'CR'])
    ).count()
    
    # Get recent findings (invasive or protected species)
    recent_findings = []
    for otu in otus:
        if otu.species_info and (
            otu.species_info.status == 'invasive' or 
            otu.species_info.iucn_status in ['VU', 'EN', 'CR']
        ):
            finding = {
                "type": "invasive" if otu.species_info.status == 'invasive' else "protected",
                "species": otu.taxonomy.species if otu.taxonomy else "Unknown species",
                "date": project.created_at.strftime("%Y-%m-%d")
            }
            recent_findings.append(finding)
    
    return {
        "metrics": {
            "speciesRichness": species_count,
            "phylogeneticDiversity": 0,  # Placeholder - implement actual calculation
            "invasiveSpecies": invasive_species,
            "protectedSpecies": protected_species
        },
        "recentFindings": recent_findings[:5],  # Only return most recent 5 findings
        "timeSeriesData": [],  # Placeholder for time series data
        "locationData": [],    # Placeholder for location data
        "otuData": []         # Placeholder for OTU table data
    }

@app.post("/projects/{project_id}/upload")
async def upload_project_data(
    project_id: int,
    otu_table: UploadFile = File(...),
    metadata: UploadFile = File(...),
    sequences: UploadFile = File(...),
    tax_table: UploadFile = File(...),
    taxa_metadata: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    """Upload and process project data files"""
    try:
        # Validate project
        project = db.query(models.Project).filter(models.Project.id == project_id).first()
        if not project:
            raise HTTPException(status_code=404, detail="Project not found")
        
        # Upload files to storage
        storage_paths = {}
        required_files = {
            'otu_table.txt': otu_table,
            'metadata.txt': metadata,
            'sequences.fasta': sequences,
            'tax_table.txt': tax_table,
            'taxa_metadata.txt': taxa_metadata
        }
        
        for filename, file_obj in required_files.items():
            path = f"projects/{project_id}/{filename}"
            await storage.upload_file(file_obj, path)
            storage_paths[filename] = path
        
        # Process the uploaded data
        processor = DataProcessor(db, storage)
        await processor.process_project_data(project_id, storage_paths)
        
        return {
            "message": "Data uploaded and processed successfully",
            "storage_paths": storage_paths
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))