# COSMIC-Roadmap
Python code to generate potential roadmaps and development paths for self-sustained ISAM ecosystems.

## Setup Instructions

### Prerequisites
- Python 3.13 or higher (might work on lower version, but only tested on 3.13)
- Git

### Virtual Environment Setup

#### Windows (PowerShell)
```powershell
# Clone the repository
git clone https://github.com/Asteres-Technologies/COSMIC-Roadmap.git
cd COSMIC-Roadmap

# Create a virtual environment
python -m venv venv

# Activate the virtual environment
.\venv\Scripts\Activate.ps1

# Install dependencies
pip install -r requirements.txt
```

#### macOS/Linux (Bash/Zsh)
```bash
# Clone the repository
git clone https://github.com/Asteres-Technologies/COSMIC-Roadmap.git
cd COSMIC-Roadmap

# Create a virtual environment
python3 -m venv venv

# Activate the virtual environment
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### Deactivating the Virtual Environment
When you're done working on the project, you can deactivate the virtual environment:
```bash
deactivate
```

### Project Structure
```
COSMIC-Roadmap/
├── data/
│   ├── processed/      # Processed data files
│   └── raw/           # Raw input data files
├── src/
│   ├── data_processing/    # Data processing modules
│   ├── utils/             # Utility functions
│   └── visualization/     # Visualization modules
├── tests/             # Unit tests
├── requirements.txt   # Python dependencies
└── README.md         # This file
```

## Usage

### Data Processing
The main data processing functionality is in `src/data_processing/roadmap_combiner.py`. This module combines dependency and readiness data from CSV files:

```python
from src.data_processing.roadmap_combiner import create_combined_roadmap

# Combine roadmap data
roadmap_data = create_combined_roadmap('path/to/dependency.csv', 'path/to/readiness.csv')
```

### Input Data Format
Place your CSV files in the `data/raw/` directory:
- `Roadmap-dependency.csv` - Contains dependency data
- `Roadmap-readiness.csv` - Contains readiness data

Both files should have:
- Headers in the 3rd row (mission names)
- First column containing capability names
- Data values in the corresponding cells

## Development

### Running Tests
```bash
# Activate virtual environment first
pytest tests/
```
