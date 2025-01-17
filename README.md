# DNAir User Portal

A full-stack application for managing and analyzing environmental DNA (eDNA) data. The system consists of three main components: a data management module, a backend API, and a frontend web application.

## Repository Structure

```
github_repo_igm5tr4v/
├── edna-data/            # Data management and validation module
├── edna-backend/         # FastAPI backend service
└── edna-frontend/        # React frontend application
```

## Components

### Data Management Module (`edna-data/`)

Handles data validation and project structure management.

Key files:
- `init_project.py`: Creates new project directory structures
- `validate_files.py`: Validates eDNA data files
- `requirements.txt`: Python dependencies for data management
- `file_requirements.txt`: Specifies required data files and formats

Project Structure Template:
```
users/
└── {user_name}/
    └── {project_name}/
        ├── raw_data/
        │   ├── metadata.txt
        │   ├── taxa_metadata.txt
        │   ├── tax_table.txt
        │   ├── sequences.fasta
        │   └── otu_table.txt
        ├── processed_data/
        └── results/
```

### Backend Service (`edna-backend/`)

FastAPI-based REST API service with PostgreSQL database.

Key components:
- `app/`: Main application directory
  - `main.py`: FastAPI application and endpoints
  - `models/`: Database models and schemas
  - `utils/`: Utility functions for data processing
  - `db/`: Database configuration
- `config/`: Configuration files
- `requirements.txt`: Python dependencies
- `Dockerfile`: Container configuration
- `init_db.py`: Database initialization script
- `populate_database.py`: Data population utility

API Features:
- User and project management
- File upload and validation
- Data processing and analysis
- Sample metadata management
- Taxonomic classification

### Frontend Application (`edna-frontend/`)

React-based web interface with Tailwind CSS styling.

Key components:
- `src/`: Source code directory
  - `components/`: React components
  - `styles/`: CSS and styling files
  - `App.js`: Main application component
- `public/`: Static assets
- `package.json`: NPM dependencies
- `tailwind.config.js`: Tailwind CSS configuration

Features:
- Project dashboard
- Interactive data visualization
- Sample location mapping
- Species diversity analysis
- Real-time data updates

## Setup and Deployment

### Prerequisites
- Python 3.11+
- Node.js 16+
- PostgreSQL 14+
- Google Cloud Platform account

### Local Development

1. Backend Setup:
```bash
cd edna-backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

2. Frontend Setup:
```bash
cd edna-frontend
npm install
npm start
```

3. Database Setup:
```bash
# Initialize database
python init_db.py

# Populate with test data
python populate_database.py --user "test_user" --project "test_project"
```

### Cloud Deployment

1. Backend (Cloud Run):
```bash
cd edna-backend
docker build -t edna-backend .
docker tag edna-backend gcr.io/dnair-database/edna-backend
docker push gcr.io/dnair-database/edna-backend
```

2. Frontend (Firebase):
```bash
cd edna-frontend
npm run build
firebase deploy
```

## Environment Variables

### Backend (.env)
```
ENVIRONMENT=cloud
DATABASE_URL=postgresql://user:password@host/database
GOOGLE_CLOUD_PROJECT=project-id
BUCKET_NAME=bucket-name
```

### Frontend (.env)
```
REACT_APP_API_URL=backend-url
REACT_APP_STORAGE_BUCKET=storage-bucket
```

## Data File Requirements

1. `metadata.txt`: Sample metadata (tab-separated)
   - Required columns: SampleID, Latitude, Longitude, SamplingTime

2. `otu_table.txt`: OTU abundance matrix (tab-separated)
   - Rows: Samples
   - Columns: OTUs
   - Values: Read counts

3. `sequences.fasta`: Reference sequences
   - FASTA format
   - Headers should match OTU IDs

4. `tax_table.txt`: Taxonomic assignments (tab-separated)
   - Required columns: OTU, Kingdom, Phylum, Class, Order, Family, Genus, Species

5. `taxa_metadata.txt`: Species metadata (tab-separated)
   - Required columns: Species, RedListStatus, InvasionStatus

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit changes
4. Push to the branch
5. Create a Pull Request

## License

Copyright and License
© 2025 Fabian Roger, DNAir. All rights reserved.
This is a private repository. No part of this software may be reproduced, distributed, or transmitted in any form or by any means without the prior written permission of the Dan Nüst Group, University of Münster.
For permission requests, please contact:
Fabian Roger
fabian.roger@dnair.ch
