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
    import math
    from sqlalchemy import func
    from collections import defaultdict
    
    # Verify project exists
    project = db.query(models.Project).filter(models.Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    try:
        # Get basic OTU data
        otus = db.query(models.OTU).filter(models.OTU.project_id == project_id).all()
        
        # Calculate metrics
        species_count = len(otus)
        
        # Count invasive species
        invasive_species = db.query(models.SpeciesMetadata).join(models.OTU).filter(
            models.OTU.project_id == project_id,
            models.SpeciesMetadata.status == 'invasive'
        ).count()
        
        # Count protected species (VU, EN, CR status)
        protected_species = db.query(models.SpeciesMetadata).join(models.OTU).filter(
            models.OTU.project_id == project_id,
            models.SpeciesMetadata.iucn_status.in_(['VU', 'EN', 'CR'])
        ).count()

        # Get samples and group by station
        samples = db.query(models.Sample).filter(
            models.Sample.project_id == project_id
        ).all()

        # Group samples by station
        station_groups = defaultdict(list)
        for sample in samples:
            station = sample.environmental_data.get('Station')
            if station:
                station_groups[station].append(sample)

        # Process location data by station
        location_data = []
        for station, station_samples in station_groups.items():
            # Use the first sample for lat/long since they're the same for each station
            first_sample = station_samples[0]
            
            # Count total OTUs for this station
            station_otu_count = db.query(models.OTUCount).filter(
                models.OTUCount.sample_id.in_([s.id for s in station_samples])
            ).count()
            
            location_data.append({
                "name": station,
                "latitude": first_sample.latitude,
                "longitude": first_sample.longitude,
                "samples": len(station_samples),  # Number of time points sampled
                "total_observations": station_otu_count,
                "first_date": min(s.collection_date for s in station_samples).strftime("%Y-%m-%d"),
                "last_date": max(s.collection_date for s in station_samples).strftime("%Y-%m-%d")
            })

        # Get OTU data with taxonomy and abundance
        otu_data = []
        for otu in otus:
            # Calculate total abundance across all samples
            total_abundance = db.query(func.sum(models.OTUCount.count)).filter(
                models.OTUCount.otu_id == otu.id
            ).scalar() or 0

            # Determine status
            status = "normal"
            if otu.species_info:
                if otu.species_info.status == "invasive":
                    status = "invasive"
                elif otu.species_info.iucn_status in ["VU", "EN", "CR"]:
                    status = "protected"

            # Get all sample locations for this OTU
            sample_locations = db.query(models.Sample.name).join(
                models.OTUCount
            ).filter(
                models.OTUCount.otu_id == otu.id
            ).distinct().all()
            
            otu_data.append({
                "species": otu.taxonomy.species if otu.taxonomy else "Unknown",
                "status": status,
                "abundance": total_abundance,
                "location": ", ".join(loc[0] for loc in sample_locations)
            })

        # Generate time series data
        time_series = defaultdict(lambda: {"speciesCount": 0, "diversity": 0})
        
        # Order samples by date
        samples = db.query(models.Sample).filter(
            models.Sample.project_id == project_id
        ).order_by(models.Sample.collection_date).all()

        for sample in samples:
            date = sample.collection_date.strftime("%Y-%m-%d")
            
            # Count unique species in this sample
            species_in_sample = db.query(models.OTU).join(
                models.OTUCount
            ).filter(
                models.OTUCount.sample_id == sample.id
            ).distinct().count()
            
            time_series[date]["speciesCount"] = species_in_sample
            
            # Calculate Shannon diversity index
            otu_counts = db.query(models.OTUCount).filter(
                models.OTUCount.sample_id == sample.id
            ).all()
            
            total_counts = sum(count.count for count in otu_counts)
            if total_counts > 0:
                proportions = [count.count/total_counts for count in otu_counts]
                shannon = sum(
                    -p * math.log(p) for p in proportions if p > 0
                )
                time_series[date]["diversity"] = round(shannon, 3)

        time_series_data = [
            {"date": date, **data}
            for date, data in sorted(time_series.items())
        ]

        # Get recent findings (invasive or protected species)
        recent_findings = []
        for otu in otus:
            if otu.species_info and (
                otu.species_info.status == 'invasive' or 
                otu.species_info.iucn_status in ['VU', 'EN', 'CR']
            ):
                # Get most recent detection
                latest_detection = db.query(models.Sample.collection_date).join(
                    models.OTUCount
                ).filter(
                    models.OTUCount.otu_id == otu.id
                ).order_by(
                    models.Sample.collection_date.desc()
                ).first()

                if latest_detection:
                    finding = {
                        "type": "invasive" if otu.species_info.status == 'invasive' else "protected",
                        "species": otu.taxonomy.species if otu.taxonomy else "Unknown species",
                        "date": latest_detection[0].strftime("%Y-%m-%d")
                    }
                    recent_findings.append(finding)

        # Sort findings by date (most recent first) and limit to 5
        recent_findings.sort(key=lambda x: x["date"], reverse=True)
        recent_findings = recent_findings[:5]

        return {
            "metrics": {
                "speciesRichness": species_count,
                "invasiveSpecies": invasive_species,
                "protectedSpecies": protected_species
            },
            "recentFindings": recent_findings,
            "timeSeriesData": time_series_data,
            "locationData": location_data,
            "otuData": otu_data
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing project data: {str(e)}")

@app.post("/projects/{project_id}/upload")
async def upload_project_data(
    project_id: int,
    force: bool = False,  # Add force parameter
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
        
        # Check if project has data and force flag is not set
        has_data = db.query(models.OTU).filter(models.OTU.project_id == project_id).first() is not None
        if has_data and not force:
            raise HTTPException(
                status_code=400, 
                detail="Project already has data. Use force=true to overwrite."
            )
        
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
        await processor.process_project_data(project_id, storage_paths, force=force)
        
        return {
            "message": "Data uploaded and processed successfully",
            "storage_paths": storage_paths
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))