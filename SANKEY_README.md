# COSMIC Roadmap Sankey Diagrams

## Overview

Sankey diagrams are flow diagrams that visualize the flow relationships between different entities in your roadmap data. They are particularly useful for understanding:

- How use_cases depend on different capabilities
- The relationship between capability requirements and technology readiness
- Flow patterns and bottlenecks in your roadmap
- Resource allocation and priority analysis

## Sankey Diagram Types

### 1. Use Case → Capability Flow (`use_case_to_capability`)
**Purpose**: Shows which capabilities each use_case requires and their dependency levels.

**Best for**:
- Understanding use_case-critical capabilities
- Identifying shared capabilities across use_cases
- Analyzing capability demand

**Flow**: Use Cases → Capabilities (weighted by dependency level)

### 2. Capability → Readiness Flow (`capability_to_readiness`)
**Purpose**: Shows the current readiness distribution for each capability.

**Best for**:
- Identifying readiness gaps
- Understanding technology maturity
- Planning development priorities

**Flow**: Capabilities → Readiness Levels (weighted by count)

### 3. Use Case → Capability → Readiness Flow (`use_case_to_readiness`)
**Purpose**: Shows the complete flow from use_cases through capabilities to readiness levels.

**Best for**:
- Comprehensive analysis
- End-to-end flow understanding
- Strategic planning

**Flow**: Use Cases → Capabilities → Readiness Levels

### 4. Dependency → Capability → Readiness Flow (`dependency_flow`)
**Purpose**: Shows how different dependency levels flow through capabilities to readiness.

**Best for**:
- Risk analysis
- Understanding criticality patterns
- Prioritization planning

**Flow**: Dependency Levels → Capabilities → Readiness Levels

## Usage Examples

### Command Line Interface

```bash
# Basic use_case-to-capability flow
python roadmap.py --dependency data/raw/Roadmap-dependency.csv \
                  --readiness data/raw/Roadmap-readiness.csv \
                  --sankey --sankey-type use_case_to_capability

# Complete flow analysis
python roadmap.py --dependency data/raw/Roadmap-dependency.csv \
                  --readiness data/raw/Roadmap-readiness.csv \
                  --sankey --sankey-type use_case_to_readiness

# Generate all Sankey types
python roadmap.py --dependency data/raw/Roadmap-dependency.csv \
                  --readiness data/raw/Roadmap-readiness.csv \
                  --sankey --sankey-type all
```

### Programmatic Usage

```python
from me_roadmap.data_processing.combine import create_combined_roadmap
from me_roadmap.visualization.sankey import plot_sankey, plot_all_sankey_types

# Load data
roadmap_data = create_combined_roadmap('dependency.csv', 'readiness.csv')

# Create a specific Sankey diagram
plot_sankey(
    roadmap_data,
    flow_type="use_case_to_capability",
    min_dependency_level=0.5,  # Filter for meaningful relationships
    max_use_cases=10,           # Limit for readability
    title="Custom Use Case Analysis"
)

# Create all Sankey types
saved_files = plot_all_sankey_types(
    roadmap_data,
    max_use_cases=8,
    min_dependency_level=0.5
)
```

## Customization Options

### Parameters

- `flow_type`: Type of Sankey flow to visualize
- `min_dependency_level`: Filter out low-dependency relationships
- `max_use_cases`: Limit number of use_cases for clarity
- `title`: Custom title for the diagram
- `output_dir`: Directory to save HTML files
- `show_plot`: Whether to open in browser

### Filtering

Use `min_dependency_level` to focus on the most important relationships:
- `0.0`: Show all relationships
- `0.5`: Show medium and high dependencies
- `0.8`: Show only high dependencies
- `1.0`: Show only use_case-critical dependencies

### Use Case Limiting

Use `max_use_cases` to prevent overcrowded diagrams:
- For overview analysis: 15-20 use_cases
- For detailed analysis: 8-12 use_cases
- For focused analysis: 4-6 use_cases

## Output Files

Sankey diagrams are saved as interactive HTML files in:
```
data/processed/sankey/
├── roadmap_sankey_use_case_to_capability.html
├── roadmap_sankey_capability_to_readiness.html
├── roadmap_sankey_use_case_to_readiness.html
└── roadmap_sankey_dependency_flow.html
```

## Interactive Features

The generated HTML files include:
- **Hover information**: Detailed flow values and relationships
- **Zoom and pan**: Navigate large diagrams
- **Node highlighting**: Click nodes to highlight connected flows
- **Responsive design**: Works on different screen sizes

## Demo Script

Run the demo to see Sankey diagrams with sample data:

```bash
python demo_sankey.py
```

This will create example diagrams showing:
- Sample use_case and capability relationships
- Different flow types and their use cases
- Best practices for data visualization

## Best Practices

### 1. Data Preparation
- Ensure consistent naming in your CSV files
- Clean dependency and readiness values
- Use meaningful use_case and capability names

### 2. Visualization Strategy
- Start with use_case_to_capability for overview
- Use filters to focus on critical relationships
- Limit use_cases for complex datasets
- Create multiple views for different audiences

### 3. Analysis Workflow
1. **Overview**: `use_case_to_capability` to understand demand
2. **Readiness**: `capability_to_readiness` to identify gaps
3. **Complete**: `use_case_to_readiness` for end-to-end analysis
4. **Risk**: `dependency_flow` for criticality analysis

### 4. Presentation Tips
- Use `max_use_cases=8-10` for stakeholder presentations
- Apply `min_dependency_level=0.7` to highlight priorities
- Include custom titles for context
- Save multiple versions for different audiences

## Troubleshooting

### Common Issues

**No data displayed**: Check that your CSV files have proper headers and data
```python
# Verify data structure
roadmap_data = create_combined_roadmap('dep.csv', 'read.csv')
print(f"Use Cases: {roadmap_data.get_use_case_count()}")
print(f"Capabilities: {len(roadmap_data.get_all_capabilities())}")
```

**Overcrowded diagram**: Reduce use_cases or increase filtering
```python
plot_sankey(roadmap_data, max_use_cases=6, min_dependency_level=0.8)
```

**Missing flows**: Check dependency and readiness value formats
```python
# Debug specific use_case
use_case = roadmap_data.use_cases["Your Use Case Name"]
for cap, entry in use_case.capabilities.items():
    print(f"{cap}: dep={entry.dependency_level}, read={entry.readiness_level}")
```

## Integration with Other Visualizations

Sankey diagrams complement other COSMIC visualizations:

- **Heatmaps**: Show intensity patterns
- **Radar charts**: Show capability profiles
- **Sankey**: Show flow relationships
- **Text reports**: Provide detailed analysis

Use together for comprehensive analysis:
```bash
# Create complete visualization suite
python roadmap.py --dependency data.csv --readiness data.csv --heatmap
python roadmap.py --dependency data.csv --readiness data.csv --radar  
python roadmap.py --dependency data.csv --readiness data.csv --sankey --sankey-type all
```