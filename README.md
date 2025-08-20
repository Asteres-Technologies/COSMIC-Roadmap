# COSMIC-Roadmap
Python code to generate potential roadmaps and development paths for self-sustained ISAM (In-Space Assembly and Manufacturing) ecosystems.

## 🎯 Purpose

The COSMIC-Roadmap tool analyzes the relationship between mission requirements and technological capabilities for space-based manufacturing and assembly operations. It combines dependency analysis (how critical each capability is for a mission) with readiness assessment (how mature each technology is) to provide insights for strategic planning.

### Key Features:
- **Mission-Capability Analysis**: Maps capabilities to missions with dependency levels
- **Technology Readiness Assessment**: Tracks maturity levels for each capability
- **Multiple Visualization Formats**: Clean, readable outputs for different use cases
- **Data Integration**: Combines multiple CSV data sources into unified analysis

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

## 📁 Project Structure
```
COSMIC-Roadmap/
├── data/
│   ├── processed/      # Processed data files
│   └── raw/           # Raw input data files (CSV files go here)
├── src/
│   ├── data_processing/    # Data processing modules
│   ├── utils/             # Utility functions
│   └── visualization/     # Visualization modules
├── tests/             # Unit tests
├── requirements.txt   # Python dependencies
├── roadmap.py        # Main application script
└── README.md         # This file
```

## 🚀 Usage

### Input Data Format
Place your CSV files in the `data/raw/` directory:
- `Roadmap-dependency.csv` - Contains dependency data (how critical each capability is)
- `Roadmap-readiness.csv` - Contains readiness data (technology maturity levels)

Both files should have:
- **Headers in the 3rd row** (mission names)
- **First column** containing capability names
- **Data values** in the corresponding cells

### Command Line Interface

The tool provides multiple output formats to suit different analysis needs:

#### 1. Sample View (Default)
```bash
python roadmap.py
```
**Purpose**: Quick overview of first mission for verification
**Example Output**:
```
================================================================================
📊 COSMIC ROADMAP DATA - SAMPLE
================================================================================

🎯 Mission: Delivery of satellite from launch vehicle upper stage to final intended orbit
--------------------------------------------------------------------------------

🔧 Inspection and Metrology
   └─ Dependency:  1.0 - Mission Critical
   └─ Readiness:   13 - Sustainable System

🔧 Relocation
   └─ Dependency:  1.0 - Mission Critical
   └─ Readiness:   7 - System Demonstration
```

#### 2. Complete Analysis
```bash
python roadmap.py --full
```
**Purpose**: View all missions and capabilities with detailed formatting
**Example Output**:
```
====================================================================================================
📊 COSMIC ROADMAP DATA - COMPLETE ANALYSIS
====================================================================================================

🎯 Mission 1: Delivery of satellite from launch vehicle upper stage to final intended orbit
----------------------------------------------------------------------------------------------------

  🔧 Inspection and Metrology
     └─ Dependency:  1.0 - Mission Critical
     └─ Readiness:   13 - Sustainable System

  🔧 Relocation
     └─ Dependency:  1.0 - Mission Critical
     └─ Readiness:   7 - System Demonstration

────────────────────────────────────────────────────────────────────────────────────────────────

🎯 Mission 2: Manufacturing of Spare Parts
----------------------------------------------------------------------------------------------------
...
```

#### 3. Table Format
```bash
python roadmap.py --table
```
**Purpose**: Structured table view for easy data scanning
**Example Output**:
```
========================================================================================================================
📊 ROADMAP TABLE: Delivery of satellite from launch vehicle upper stage to final intended orbit
========================================================================================================================
CAPABILITY                                   DEPENDENCY                          READINESS                          
------------------------------------------------------------------------------------------------------------------------
Inspection and Metrology                     1.0 - Mission Critical             13 - Sustainable System           
Relocation                                   1.0 - Mission Critical             7 - System Demonstration          
```

#### 4. Summary Overview
```bash
python roadmap.py --summary
```
**Purpose**: High-level statistics and mission list
**Example Output**:
```
================================================================================
📈 COSMIC ROADMAP SUMMARY
================================================================================

📊 Overview:
   └─ Total Missions: 24
   └─ Total Capabilities: 264
   └─ Avg Capabilities per Mission: 11.0

🎯 Missions:
    1. Delivery of satellite from launch vehicle upper stage to final intended orbit
       └─ 11 capabilities
    2. Manufacturing of Spare Parts
       └─ 11 capabilities
```

#### 5. Capabilities Analysis
```bash
python roadmap.py --capabilities
```
**Purpose**: Analysis of all capabilities across missions
**Example Output**:
```
====================================================================================================
🔧 CAPABILITIES ANALYSIS
====================================================================================================

📊 Total Unique Capabilities: 11

🔧 All Capabilities:
    1. Inspection and Metrology
       └─ Used in 24 mission(s)
    2. Parts and Good Manufacture
       └─ Used in 24 mission(s)
```

### Custom File Paths
```bash
python roadmap.py --dependency path/to/custom-dependency.csv --readiness path/to/custom-readiness.csv
```

### Data Processing Module
For programmatic use:

```python
from src.data_processing.combine import create_combined_roadmap

# Combine roadmap data
roadmap_data = create_combined_roadmap('path/to/dependency.csv', 'path/to/readiness.csv')

# Access data structure: {mission: {capability: (dependency, readiness)}}
for mission, capabilities in roadmap_data.items():
    for capability, (dependency, readiness) in capabilities.items():
        print(f"{mission}: {capability} -> {dependency}, {readiness}")
```

## 📊 Data Structure

The tool creates a nested dictionary structure:
```python
{
    "Mission Name": {
        "Capability Name": (dependency_value, readiness_value),
        ...
    },
    ...
}
```

- **dependency_value**: String indicating criticality (e.g., "1.0 - Mission Critical")
- **readiness_value**: String indicating maturity (e.g., "13 - Sustainable System")

## Development

### Running Tests
```bash
# Activate virtual environment first
pytest tests/
```
