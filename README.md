# Petrophysics Well Logger

A comprehensive Python-based well data logging and interpretation suite for petrophysical analysis. This application provides professional-grade tools for analyzing well log data, calculating petrophysical properties, and generating detailed interpretations with visualization.

## Features

### Core Capabilities

- **Excel Template Generation**: Automatic creation of standardized well log data templates
- **Data Ingestion & Validation**: Robust Excel file loading with column validation and missing value handling
- **Advanced Calculations**: 
  - Shale Volume (Vsh) using Gamma Ray and Neutron-Density methods
  - Porosity calculations (Sonic, Density, Neutron, Average)
  - Fluid Saturation using Archie's Law
  - Lithology classification
- **Professional Visualization**:
  - Multi-track well log plots
  - Logarithmic scaling for resistivity
  - Color-coded interpretation zones
  - Hydrocarbon zone highlighting
  - X-axis positioned at top with proper scale labels
- **Automated Interpretation**:
  - Zone-by-zone analysis with depth ranges
  - Hydrocarbon zone identification
  - Porosity quality assessment
  - Saturation analysis
  - Lithology interpretation by depth
  - Detailed log explanations
- **Comprehensive Export**:
  - Excel export with multiple sheets (data, statistics, interpretation)
  - High-resolution PNG plots (300 DPI)
  - Vector PDF for professional reports
  - Complete results package

### User Interface Options

**GUI Application (Recommended)**
- Modern dark-themed interface
- Scrollable control panel with organized sections
- Real-time visualization with scrollable canvas
- Color-coded interpretation display
- Interactive file dialogs

**Console Application**
- Menu-driven terminal interface
- Scriptable for automation
- Suitable for headless servers

## Installation

### Prerequisites

- Python 3.8 or higher
- pip package manager

### Setup

1. Clone or download this repository

2. Install dependencies:
```bash
pip install -r requirements.txt
```

Required packages:
- pandas
- openpyxl
- matplotlib
- numpy

## Quick Start

### GUI Application

1. Launch the application:
```bash
python well_logger_gui.py
```

2. Follow the workflow:
   - Click "Generate Excel Template" to create a template file
   - Fill the template with your well log measurements
   - Click "Load Well Data" and select your filled Excel file
   - Select the logs you want to analyze using checkboxes
   - Click "Generate Plots & Interpretation" to view results
   - Use export buttons to save results in various formats

### Console Application

For advanced users who prefer terminal interface:
```bash
python well_logger.py
```
Then follow the on-screen menu options.

## Excel Template Format

The application uses a standardized Excel format with the following mandatory columns:

| Column | Unit | Description |
|--------|------|-------------|
| Depth (ft) | feet | Measured depth |
| Gamma (GAPI) | API units | Gamma Ray log |
| Resistivity Rt (OHM.M) | ohm-meters | True resistivity |
| Resistivity Rx (OHM.M) | ohm-meters | Flushed zone resistivity |
| Neutron CNL (V/V) | volumetric fraction | Compensated Neutron Log |
| Density (G/CC) | g/cm³ | Bulk density |
| Sonic (µs/ft) | microseconds/foot | Sonic transit time |

## Available Logs for Analysis

### Primary Logs
- **Gamma Ray (GAPI)**: Formation radioactivity measurement
- **Resistivity (OHM.M)**: Rt (True) and Rx (Flushed Zone)
- **Neutron (V/V)**: Hydrogen content indicator
- **Density (G/CC)**: Bulk formation density
- **Sonic (µs/ft)**: Acoustic wave travel time

### Derived Logs
- **Average Porosity (V/V)**: Combined porosity from multiple methods
- **Archie Saturation**: Water and hydrocarbon saturation
- **IGR**: Gamma Ray Index
- **Vsh (Old & New)**: Shale volume calculations
- **Neutron-Density Crossover**: Gas indication analysis

## Configuration

All petrophysical constants are configurable in `well_logger.py`:

```python
# Matrix Densities (g/cm³)
DENSITY_SANDSTONE = 2.65
DENSITY_SHALE = 2.733
DENSITY_FLUID = 1.1

# Sonic Constants (µs/ft)
ITT_MATRIX = 50
ITT_FLUID = 185

# Archie's Law Parameters
ARCHIE_A = 1.0
ARCHIE_RW = 0.2
ARCHIE_M = 2.0
ARCHIE_N = 2.0

# Neutron-Density Shale Points
PHI_NEUTRON_SHALE = 0.33
PHI_DENSITY_SHALE = 0.07
```

## Petrophysical Formulas

### Shale Volume (Vsh)

**Gamma Ray Method:**
```
IGR = (GR_log - GR_min) / (GR_max - GR_min)
Vsh (Old) = 0.33 × (2^(2×IGR) - 1)
Vsh (New) = 0.083 × (2^(3.7×IGR) - 1)
```

**Neutron-Density Method:**
```
Vsh(N-D) = (φ_neutron - φ_density) / (φ_neutron_shale - φ_density_shale)
```

### Porosity Calculations

**Sonic Porosity:**
```
φ_sonic = (ITT_log - ITT_ma) / (ITT_f - ITT_ma)
```

**Density Porosity:**
```
φ_density = (ρ_ma - ρ_bulk) / (ρ_ma - ρ_f)
```

**Neutron Porosity:**
```
φ_neutron = CNL_data / 100
```

**Average Porosity:**
```
φ_avg = (φ_sonic + φ_density + φ_neutron) / 3
```

### Fluid Saturation (Archie's Law)

```
Sw = ((a / φ^m) × (Rw / Rt))^(1/n)
Shc = 1 - Sw
```

Where:
- Sw = Water saturation
- Shc = Hydrocarbon saturation
- a = Tortuosity factor (default: 1.0)
- φ = Porosity
- m = Cementation exponent (default: 2.0)
- Rw = Formation water resistivity (default: 0.2 ohm-m)
- Rt = True formation resistivity
- n = Saturation exponent (default: 2.0)

## Interpretation Guidelines

### Resistivity Analysis
- **Rt < Rx**: High salinity water indication
- **Rt > Rx**: Hydrocarbon presence indication
- Higher resistivity generally indicates hydrocarbons or tight formations

### Density Interpretation
- **> 2.6 g/cc**: Dense formations (Limestone/Dolomite)
- **2.2-2.6 g/cc**: Medium density (Sandstone with porosity)
- **< 2.2 g/cc**: High porosity zones (potential hydrocarbon reservoir)

### Lithology Fingerprinting
- **High GR + Low Density + High Neutron**: Shale/clay-rich formations
- **Low GR + Low Density + High Neutron**: Sandstone (potential pay zone)
- **Low GR + High Density + Low Neutron**: Limestone/carbonate formations

### Porosity Quality Classification
- **Excellent**: ≥ 25%
- **Good**: 15-25%
- **Fair**: 10-15%
- **Poor**: < 10%

### Saturation Classification
- **High HC**: Shc ≥ 70%
- **HC-bearing**: 50-70%
- **Transition**: 30-50%
- **Water-bearing**: < 30%

## Output Files

The application generates the following output files:

### Excel Export
- **Data Sheet**: All original and calculated logs
- **Statistics Sheet**: Summary statistics for all measurements
- **Interpretation Sheet**: Automated analysis results

### Plot Export
- **PNG**: High-resolution raster image (300 DPI)
- **PDF**: Vector graphics for professional reports

### Complete Package
Creates a timestamped folder containing:
- Excel file with all data
- PNG plot
- PDF plot
- Text file with interpretation summary

## Project Structure

```
Well logger/
├── well_logger.py          # Core application (console version)
├── well_logger_gui.py      # GUI application (recommended)
├── requirements.txt        # Python dependencies
├── README.md              # This file
├── USAGE_GUIDE.md         # Detailed usage instructions
└── GUI_FEATURES.md        # GUI feature documentation
```

## Dependencies

- **pandas**: Data manipulation and analysis
- **openpyxl**: Excel file reading/writing
- **matplotlib**: Plotting and visualization
- **numpy**: Numerical computations

## Technical Details

### Architecture
- Modular class-based design
- Separation of concerns (data loading, calculation, plotting, interpretation)
- PEP8 compliant code
- Comprehensive documentation and comments

### Key Classes
- `TemplateGenerator`: Excel template creation
- `DataLoader`: Data ingestion and validation
- `PetrophysicsCalculator`: Petrophysical calculations
- `LogPlotter`: Multi-track visualization
- `WellInterpreter`: Automated interpretation
- `ResultsExporter`: Export functionality
- `PetrophysicsWellLoggerGUI`: GUI interface

## Features Highlights

### Visualization Enhancements
- X-axis positioned at top for standard well log appearance
- Fixed track width (3.5 inches) prevents stretching
- Colored zone highlighting for hydrocarbon intervals
- Scrollable canvas for large datasets
- Professional formatting with proper units in titles

### Interpretation Features
- Continuous zone identification with depth ranges
- Thickness calculations for each zone
- Average properties per zone
- Distribution statistics
- Recommendations for further analysis

### Export Capabilities
- Multiple format support (XLSX, PNG, PDF)
- Timestamped output files
- Complete data preservation
- Professional report-ready outputs

## System Requirements

- **Operating System**: Windows, macOS, or Linux
- **Python**: 3.8 or higher
- **Memory**: 2GB RAM minimum (4GB recommended)
- **Display**: 1400x900 or higher resolution recommended for GUI

## License

This software is provided as-is for educational and professional use in petrophysical analysis.

## Support

For issues, questions, or contributions, please refer to the project documentation:
- `USAGE_GUIDE.md` - Detailed usage instructions
- `GUI_FEATURES.md` - GUI-specific features and tips

## Version

Current Version: 2.0 (GUI Edition with Enhanced Interpretation)

## Acknowledgments

Built with industry-standard petrophysical formulas and best practices in well log analysis.
