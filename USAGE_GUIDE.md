# Installation and Usage Guide

## Installation Steps

1. **Verify Python Installation**:
   ```bash
   python --version
   ```
   (Should be Python 3.8 or higher)

2. **Install Dependencies**:
   ```bash
   python -m pip install -r requirements.txt
   ```

3. **Run the Application**:
   ```bash
   python well_logger.py
   ```

## Quick Usage Example

### Complete Workflow (Option 6)

1. Start the application:
   ```bash
   python well_logger.py
   ```

2. Select option **6** (Run Complete Workflow)

3. When prompted to generate template, select **y**

4. The template `well_log_template.xlsx` will be created

5. Open the Excel file and fill in your well log data:
   - Replace sample data with actual measurements
   - Ensure all depths are in ascending order
   - Keep column names unchanged

6. Save the Excel file

7. When prompted for file path, enter the Excel filename

8. Select logs to analyze (default selection includes all key logs)

9. View the multi-track plot and interpretation summary

10. Export results package when prompted

### Manual Workflow

**Step 1: Generate Template**
- Select option **1**
- Enter filename or press Enter for default
- Template will be created with instructions

**Step 2: Load Data**
- Fill template with your data
- Select option **2**
- Enter path to your Excel file
- Application will validate and process data

**Step 3: Select Logs**
- Select option **3**
- Enter numbers for desired logs (e.g., `1,2,6,8,11`)
  - 1: Gamma Ray
  - 2: Resistivity
  - 6: Porosity (individual)
  - 8: Archie Saturation
  - 11: Neutron-Density Crossover

**Step 4: Generate Plots**
- Select option **4**
- View professional multi-track visualization
- Read interpretation summary

**Step 5: Export Results**
- Select option **5**
- Choose export format:
  - Option 1: Excel only
  - Option 2: Plots only (PNG + PDF)
  - Option 3: Complete package (recommended)

## Troubleshooting

### Python not found
Install Python from python.org (version 3.8+)

### pip not recognized
Use: `python -m pip install -r requirements.txt`

### Excel file errors
- Ensure column names match exactly
- Check that all data is numeric
- Remove any extra sheets except "Well Log Data"

### Plot not displaying
If matplotlib doesn't show plots, ensure you're not running in headless mode.

## Sample Data Format

```
Depth (ft) | Gamma (GAPI) | Resistivity Rt | Resistivity Rx | Neutron CNL | Density | Sonic
1000       | 45           | 10             | 8              | 20          | 2.45    | 75
1005       | 50           | 12             | 10             | 22          | 2.50    | 70
1010       | 55           | 15             | 12             | 24          | 2.55    | 65
...
```

Depth intervals can be any spacing (1ft, 0.5ft, etc.)
