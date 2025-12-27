"""
Petrophysics Well Logger
A comprehensive well data logging and interpretation suite for petrophysical analysis.

Author: Petrophysical Software Engineer
Version: 1.0
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
import os
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')

# ============================================================================
# CONFIGURATION SECTION - Edit these parameters as needed
# ============================================================================

# Matrix Densities (g/cm³)
DENSITY_SANDSTONE = 2.65
DENSITY_SHALE = 2.733
DENSITY_FLUID = 1.1

# Sonic Constants (µs/ft)
ITT_MATRIX = 50
ITT_FLUID = 185

# Archie's Law Parameters
ARCHIE_A = 1.0      # Tortuosity factor
ARCHIE_RW = 0.2     # Brine resistivity (ohm.m)
ARCHIE_M = 2.0      # Cementation exponent
ARCHIE_N = 2.0      # Saturation exponent

# Neutron-Density Shale Reference Values
PHI_NEUTRON_SHALE = 0.40
PHI_DENSITY_SHALE = 0.05

# Color Preferences for Interpretation (Hex Codes)
COLOR_OIL = '#90EE90'      # Light Green
COLOR_GAS = '#FFD700'      # Gold
COLOR_WATER = '#87CEEB'    # Sky Blue
COLOR_SHALE = '#8B4513'    # Saddle Brown
COLOR_SANDSTONE = '#F4A460' # Sandy Brown
COLOR_LIMESTONE = '#D3D3D3' # Light Gray

# ============================================================================
# TEMPLATE GENERATOR CLASS
# ============================================================================

class TemplateGenerator:
    """Generates Excel template for well log data entry."""
    
    @staticmethod
    def generate_template(filename="well_log_template.xlsx"):
        """
        Create an Excel template with mandatory columns.
        
        Parameters:
        -----------
        filename : str
            Output filename for the template
        """
        # Define mandatory columns
        columns = [
            'Depth (ft)',
            'Gamma (GAPI)',
            'Resistivity Rt (OHM.M)',
            'Resistivity Rx (OHM.M)',
            'Neutron CNL (V/V)',
            'Density (G/CC)',
            'Sonic (µs/ft)'
        ]
        
        # Create empty DataFrame with columns
        df = pd.DataFrame(columns=columns)
        
        # Add sample rows to show format
        sample_data = {
            'Depth (ft)': [1000, 1005, 1010, 1015, 1020],
            'Gamma (GAPI)': [45, 50, 55, 60, 65],
            'Resistivity Rt (OHM.M)': [10, 12, 15, 18, 20],
            'Resistivity Rx (OHM.M)': [8, 10, 12, 14, 16],
            'Neutron CNL (V/V)': [20, 22, 24, 26, 28],
            'Density (G/CC)': [2.45, 2.50, 2.55, 2.60, 2.65],
            'Sonic (µs/ft)': [75, 70, 65, 60, 55]
        }
        
        sample_df = pd.DataFrame(sample_data)
        
        # Create Excel writer
        with pd.ExcelWriter(filename, engine='openpyxl') as writer:
            # Write main data sheet
            sample_df.to_excel(writer, sheet_name='Well Log Data', index=False)
            
            # Create instructions sheet
            instructions = {
                'Section': [
                    'Data Entry Guidelines',
                    '',
                    'Column Descriptions',
                    'Depth (ft)',
                    'Gamma (GAPI)',
                    'Resistivity Rt (OHM.M)',
                    'Resistivity Rx (OHM.M)',
                    'Neutron CNL (V/V)',
                    'Density (G/CC)',
                    'Sonic (µs/ft)',
                    '',
                    'Important Notes',
                    '1. Remove sample data',
                    '2. Ensure depths in order',
                    '3. Missing values handled',
                    '4. Save before loading'
                ],
                'Information': [
                    'Please fill all columns with your well log measurements',
                    '',
                    '',
                    'Measured depth in feet',
                    'Gamma Ray log in API units',
                    'True resistivity of formation in ohm-meters',
                    'Resistivity of flushed zone in ohm-meters',
                    'Compensated Neutron Log in volumetric fraction',
                    'Bulk density in grams per cubic centimeter',
                    'Sonic transit time in microseconds per foot',
                    '',
                    '',
                    'before entering your measurements',
                    '',
                    'by the application',
                    'into Petrophysics Well Logger'
                ]
            }
            
            inst_df = pd.DataFrame(instructions)
            inst_df.to_excel(writer, sheet_name='Instructions', index=False)
        
        print(f"✓ Template generated successfully: {filename}")
        print(f"  Please fill the 'Well Log Data' sheet with your measurements")
        return filename


# ============================================================================
# DATA LOADER CLASS
# ============================================================================

class DataLoader:
    """Handles Excel file loading and data validation."""
    
    def __init__(self, filepath):
        """Initialize DataLoader with file path."""
        self.filepath = filepath
        self.data = None
        self.stats = {}
        
    def load_excel(self):
        """Load Excel file into DataFrame."""
        try:
            self.data = pd.read_excel(self.filepath, sheet_name='Well Log Data')
            print(f"✓ Data loaded successfully from {self.filepath}")
            print(f"  Total depth points: {len(self.data)}")
            return True
        except Exception as e:
            print(f"✗ Error loading file: {str(e)}")
            return False
    
    def validate_data(self):
        """Check for required columns and data types."""
        required_columns = [
            'Depth (ft)',
            'Gamma (GAPI)',
            'Resistivity Rt (OHM.M)',
            'Resistivity Rx (OHM.M)',
            'Neutron CNL (V/V)',
            'Density (G/CC)',
            'Sonic (µs/ft)'
        ]
        
        missing_columns = [col for col in required_columns if col not in self.data.columns]
        
        if missing_columns:
            print(f"✗ Missing columns: {', '.join(missing_columns)}")
            return False
        
        print("✓ All required columns present")
        return True
    
    def handle_nulls(self):
        """Process missing values."""
        null_counts = self.data.isnull().sum()
        if null_counts.sum() > 0:
            print("⚠ Missing values detected:")
            for col in null_counts[null_counts > 0].index:
                print(f"  {col}: {null_counts[col]} missing values")
        
        # Forward fill then backward fill
        self.data = self.data.fillna(method='ffill').fillna(method='bfill')
        print("✓ Missing values handled")
    
    def get_statistics(self):
        """Calculate min/max statistics for logs."""
        if 'Gamma (GAPI)' in self.data.columns:
            self.stats['GR_MIN'] = self.data['Gamma (GAPI)'].min()
            self.stats['GR_MAX'] = self.data['Gamma (GAPI)'].max()
            print(f"✓ Statistics calculated:")
            print(f"  GR range: {self.stats['GR_MIN']:.2f} - {self.stats['GR_MAX']:.2f} GAPI")
        
        return self.stats


# ============================================================================
# PETROPHYSICS CALCULATOR CLASS
# ============================================================================

class PetrophysicsCalculator:
    """Performs all petrophysical calculations."""
    
    def __init__(self, config=None):
        """Initialize calculator with configuration parameters."""
        self.config = config or {}
        
    # -------------------- Shale Volume Calculations --------------------
    
    @staticmethod
    def calculate_IGR(gr_log, gr_min, gr_max):
        """
        Calculate Gamma Ray Index.
        
        IGR = (GR_log - GR_min) / (GR_max - GR_min)
        """
        igr = (gr_log - gr_min) / (gr_max - gr_min)
        return np.clip(igr, 0, 1)  # Clip to [0, 1] range
    
    @staticmethod
    def calculate_vsh_old(igr):
        """
        Calculate Shale Volume using Old formula.
        
        Vsh = 0.33 * (2^(2*IGR) - 1)
        """
        vsh = 0.33 * (np.power(2, 2 * igr) - 1)
        return np.clip(vsh, 0, 1)
    
    @staticmethod
    def calculate_vsh_new(igr):
        """
        Calculate Shale Volume using New formula.
        
        Vsh = 0.083 * (2^(3.7*IGR) - 1)
        """
        vsh = 0.083 * (np.power(2, 3.7 * igr) - 1)
        return np.clip(vsh, 0, 1)
    
    @staticmethod
    def classify_lithology_gr(vsh_new):
        """
        Classify lithology based on Vsh (New).
        
        If Vsh > 0.5: Shale
        Otherwise: Sandstone
        """
        return np.where(vsh_new > 0.5, 'Shale', 'Sandstone')
    
    @staticmethod
    def calculate_vsh_neutron_density(phi_n, phi_d, phi_n_shale=PHI_NEUTRON_SHALE, 
                                     phi_d_shale=PHI_DENSITY_SHALE):
        """
        Calculate Shale Volume from Neutron-Density crossover.
        
        Vsh = (phi_neutron - phi_density) / (phi_neutron_shale - phi_density_shale)
        """
        vsh = (phi_n - phi_d) / (phi_n_shale - phi_d_shale)
        return np.clip(vsh, 0, 1)
    
    # -------------------- Porosity Calculations --------------------
    
    @staticmethod
    def calculate_sonic_porosity(itt_log, itt_ma=ITT_MATRIX, itt_f=ITT_FLUID):
        """
        Calculate Sonic Porosity.
        
        φ_s = (ITT_log - ITT_ma) / (ITT_f - ITT_ma)
        """
        phi_s = (itt_log - itt_ma) / (itt_f - itt_ma)
        return np.clip(phi_s, 0, 0.5)
    
    @staticmethod
    def calculate_density_porosity(rho_bulk, lithology, rho_f=DENSITY_FLUID):
        """
        Calculate Density Porosity.
        
        φ_d = (ρ_ma - ρ_bulk) / (ρ_ma - ρ_f)
        
        Parameters:
        -----------
        rho_bulk : array
            Bulk density measurements
        lithology : array
            Lithology classification ('Sandstone' or 'Shale')
        """
        # Determine matrix density based on lithology
        rho_ma = np.where(lithology == 'Sandstone', DENSITY_SANDSTONE, DENSITY_SHALE)
        
        phi_d = (rho_ma - rho_bulk) / (rho_ma - rho_f)
        return np.clip(phi_d, 0, 0.5)
    
    @staticmethod
    def calculate_neutron_porosity(cnl_data):
        """
        Calculate Neutron Porosity.
        
        φ_n = CNL_data / 100
        """
        phi_n = cnl_data / 100
        return np.clip(phi_n, 0, 0.5)
    
    @staticmethod
    def calculate_average_porosity(phi_s, phi_d, phi_n):
        """
        Calculate Average Porosity.
        
        φ_avg = (φ_s + φ_d + φ_n) / 3
        """
        return (phi_s + phi_d + phi_n) / 3
    
    # -------------------- Fluid Saturation (Archie's Law) --------------------
    
    @staticmethod
    def calculate_sw(phi, rt, a=ARCHIE_A, rw=ARCHIE_RW, m=ARCHIE_M, n=ARCHIE_N):
        """
        Calculate Water Saturation using Archie's Law.
        
        Sw = ((a / φ^m) * (Rw / Rt))^(1/n)
        """
        # Avoid division by zero
        phi_safe = np.where(phi > 0.01, phi, 0.01)
        rt_safe = np.where(rt > 0.1, rt, 0.1)
        
        sw = np.power((a / np.power(phi_safe, m)) * (rw / rt_safe), 1/n)
        return np.clip(sw, 0, 1)
    
    @staticmethod
    def calculate_shc(sw):
        """
        Calculate Hydrocarbon Saturation.
        
        Shc = 1 - Sw
        """
        return 1 - sw


# ============================================================================
# LOG PLOTTER CLASS
# ============================================================================

class LogPlotter:
    """Creates professional multi-track well log visualizations."""
    
    def __init__(self, data, depth_col='Depth (ft)'):
        """Initialize plotter with data."""
        self.data = data
        self.depth_col = depth_col
        self.depth = data[depth_col].values
        self.fig = None
        self.axes = []
        
    def create_multitrack_plot(self, selected_logs, title="Well Log Analysis"):
        """
        Create multi-track plot based on selected logs.
        Enhanced with: x-axis on top, colored zones for HC, better height.
        
        Parameters:
        -----------
        selected_logs : dict
            Dictionary with log names as keys and boolean values
        title : str
            Plot title
        """
        # Determine number of tracks needed
        tracks = []
        
        if selected_logs.get('Gamma'):
            tracks.append('Gamma')
        
        if selected_logs.get('Resistivity'):
            tracks.append('Resistivity')
        
        if selected_logs.get('Neutron-Density'):
            tracks.append('Neutron-Density')
        elif selected_logs.get('Neutron') or selected_logs.get('Density'):
            tracks.append('Porosity Logs')
        
        if selected_logs.get('Sonic'):
            tracks.append('Sonic')
        
        if selected_logs.get('Porosity') or selected_logs.get('Average Porosity'):
            tracks.append('Porosity')
        
        if selected_logs.get('Archie'):
            tracks.append('Saturation')
        
        if selected_logs.get('IGR') or selected_logs.get('Vsh'):
            tracks.append('Shale Volume')
        
        # Create figure with appropriate number of subplots
        n_tracks = len(tracks)
        if n_tracks == 0:
            print("⚠ No logs selected for plotting")
            return None
        
        # Fixed width per track to prevent stretching when fewer logs selected
        track_width = 3.5  # inches per track
        total_width = track_width * n_tracks
        
        # Increased height for better visibility (0.15 inches per foot recommended)
        depth_range = self.depth.max() - self.depth.min()
        fig_height = max(12, depth_range * 0.15)  # At least 12 inches, scale with depth
        
        fig, axes = plt.subplots(1, n_tracks, figsize=(total_width, fig_height), sharey=True)
        
        if n_tracks == 1:
            axes = [axes]
        
        self.fig = fig
        self.axes = axes
        
        # Identify hydrocarbon zones for highlighting
        self.hc_zones = self._identify_hc_zones()
        
        # Plot each track
        for idx, track_name in enumerate(tracks):
            ax = axes[idx]
            
            if track_name == 'Gamma':
                self._plot_gamma(ax)
            elif track_name == 'Resistivity':
                self._plot_resistivity(ax)
            elif track_name == 'Neutron-Density':
                self._plot_neutron_density(ax)
            elif track_name == 'Porosity Logs':
                self._plot_porosity_logs(ax, selected_logs)
            elif track_name == 'Sonic':
                self._plot_sonic(ax)
            elif track_name == 'Porosity':
                self._plot_porosity(ax, selected_logs)
            elif track_name == 'Saturation':
                self._plot_saturation(ax)
            elif track_name == 'Shale Volume':
                self._plot_shale_volume(ax, selected_logs)
            
            # Add colored zones for all tracks (except skip first track to avoid clutter)
            if idx > 0 and self.hc_zones:
                self._add_zone_highlighting(ax)
        
        # Set common properties
        for idx, ax in enumerate(axes):
            ax.set_ylim(self.depth.max(), self.depth.min())  # Reverse y-axis
            ax.grid(True, alpha=0.3, linestyle='--', linewidth=0.5)
            
            # Move x-axis to top
            ax.xaxis.tick_top()
            ax.xaxis.set_label_position('top')
            
            # Only show depth label on first track
            if idx == 0:
                ax.set_ylabel('Depth (ft)', fontsize=11, fontweight='bold')
        
        # Adjust margins - give more space at top for titles
        plt.subplots_adjust(wspace=0.15, top=0.94, bottom=0.05, left=0.08, right=0.98)
        
        return fig
    
    def _identify_hc_zones(self):
        """Identify hydrocarbon zones for highlighting."""
        zones = []
        if 'Resistivity Rt (OHM.M)' not in self.data.columns:
            return zones
        
        rt = self.data['Resistivity Rt (OHM.M)'].values
        rx = self.data['Resistivity Rx (OHM.M)'].values
        depth = self.depth
        
        hc_indicator = rt > rx
        in_zone = False
        zone_start = None
        
        for i in range(len(hc_indicator)):
            if hc_indicator[i] and not in_zone:
                zone_start = depth[i]
                in_zone = True
            elif not hc_indicator[i] and in_zone:
                zones.append((zone_start, depth[i-1]))
                in_zone = False
        
        if in_zone:
            zones.append((zone_start, depth[-1]))
        
        return zones
    
    def _add_zone_highlighting(self, ax):
        """Add colored highlighting for hydrocarbon zones."""
        for zone_start, zone_end in self.hc_zones:
            ax.axhspan(zone_start, zone_end, alpha=0.15, color=COLOR_OIL, 
                      linewidth=0, zorder=0)
    
    def _plot_gamma(self, ax):
        """Plot Gamma Ray track."""
        gamma = self.data['Gamma (GAPI)'].values
        
        ax.plot(gamma, self.depth, 'g-', linewidth=1.8, label='Gamma Ray')
        ax.set_xlim(0, 150)
        ax.set_xlabel('')  # Remove x-axis label
        ax.set_title('Gamma Ray (GAPI)', fontsize=11, fontweight='bold', pad=10)
        
        # Add shading for shale indication
        ax.axvspan(100, 150, alpha=0.1, color='brown', label='Shale Zone')
        ax.legend(loc='lower right', fontsize=8, framealpha=0.9)
    
    def _plot_resistivity(self, ax):
        """Plot Resistivity track with logarithmic scale."""
        rt = self.data['Resistivity Rt (OHM.M)'].values
        rx = self.data['Resistivity Rx (OHM.M)'].values
        
        # Fill area where Rt > Rx (hydrocarbon indication) - more visible
        ax.fill_betweenx(self.depth, rt, rx, where=(rt >= rx), 
                         alpha=0.45, color='#FFD700', label='HC Indication', zorder=1)
        
        ax.plot(rt, self.depth, 'r-', linewidth=2.0, label='Rt', zorder=2)
        ax.plot(rx, self.depth, 'b--', linewidth=2.0, label='Rx', zorder=2)
        
        ax.set_xscale('log')
        ax.set_xlim(0.1, 1000)
        ax.set_xlabel('')  # Remove x-axis label
        ax.set_title('Resistivity (OHM.M)', fontsize=11, fontweight='bold', pad=10)
        ax.legend(loc='lower right', fontsize=8, framealpha=0.9)
    
    def _plot_neutron_density(self, ax):
        """Plot Neutron-Density crossover with fill."""
        neutron = self.data['Neutron CNL (V/V)'].values / 100  # Convert to fraction
        density_porosity = self.data['Porosity (Density)'].values
        
        ax.plot(neutron, self.depth, 'b-', linewidth=1.8, label='Neutron')
        ax.plot(density_porosity, self.depth, 'r-', linewidth=1.8, label='Density')
        
        # Fill between curves - gas effect
        ax.fill_betweenx(self.depth, neutron, density_porosity, 
                         where=(neutron >= density_porosity), 
                         color=COLOR_GAS, alpha=0.6, label='Gas Effect')
        
        ax.set_xlim(0, 0.45)
        ax.set_xlabel('')  # Remove x-axis label
        ax.set_title('Neutron-Density (V/V)', fontsize=11, fontweight='bold', pad=10)
        ax.legend(loc='lower right', fontsize=8, framealpha=0.9)
    
    def _plot_porosity_logs(self, ax, selected_logs):
        """Plot individual porosity logs."""
        if 'Porosity (Sonic)' in self.data.columns:
            ax.plot(self.data['Porosity (Sonic)'], self.depth, 'g-', 
                   linewidth=1.5, label='Sonic')
        
        if 'Porosity (Density)' in self.data.columns:
            ax.plot(self.data['Porosity (Density)'], self.depth, 'r-', 
                   linewidth=1.5, label='Density')
        
        if 'Porosity (Neutron)' in self.data.columns:
            ax.plot(self.data['Porosity (Neutron)'], self.depth, 'b-', 
                   linewidth=1.5, label='Neutron')
        
        ax.set_xlim(0, 0.45)
        ax.set_xlabel('Porosity (V/V)', fontsize=10)
        ax.set_title('Porosity Logs', fontsize=11, fontweight='bold')
        ax.legend(loc='upper right', fontsize=8)
    
    def _plot_sonic(self, ax):
        """Plot Sonic track."""
        sonic = self.data['Sonic (µs/ft)'].values
        
        ax.plot(sonic, self.depth, 'm-', linewidth=1.5, label='Sonic')
        ax.set_xlim(40, 240)
        ax.set_xlabel('')  # Remove x-axis label
        ax.set_title('Sonic (µs/ft)', fontsize=11, fontweight='bold', pad=10)
        ax.legend(loc='lower right', fontsize=8, framealpha=0.9)
    
    def _plot_porosity(self, ax, selected_logs):
        """Plot calculated porosity."""
        if 'Average Porosity' in self.data.columns:
            ax.plot(self.data['Average Porosity'], self.depth, 'k-', 
                   linewidth=2, label='Average Porosity')
        
        ax.set_xlim(0, 0.45)
        ax.set_xlabel('')  # Remove x-axis label
        ax.set_title('Average Porosity (V/V)', fontsize=11, fontweight='bold', pad=10)
        ax.legend(loc='lower right', fontsize=8, framealpha=0.9)
    
    def _plot_saturation(self, ax):
        """Plot fluid saturation from Archie's Law."""
        sw = self.data['Sw (Water Saturation)'].values
        shc = self.data['Shc (Hydrocarbon Saturation)'].values
        
        # Fill areas first with better colors
        ax.fill_betweenx(self.depth, 0, sw, color='#87CEEB', alpha=0.5, label='Water', zorder=1)
        ax.fill_betweenx(self.depth, sw, 1, color='#FFD700', alpha=0.5, label='Hydrocarbon', zorder=1)
        
        ax.plot(sw, self.depth, 'b-', linewidth=2.0, label='Sw', zorder=2)
        ax.plot(shc, self.depth, 'g-', linewidth=2.0, label='Shc', zorder=2)
        
        ax.set_xlim(0, 1)
        ax.set_xlabel('')  # Remove x-axis label
        ax.set_title('Fluid Saturation (Archie)', fontsize=11, fontweight='bold', pad=10)
        ax.legend(loc='lower right', fontsize=8, framealpha=0.9)
    
    def _plot_shale_volume(self, ax, selected_logs):
        """Plot shale volume indicators."""
        if 'IGR' in self.data.columns and selected_logs.get('IGR'):
            ax.plot(self.data['IGR'], self.depth, 'orange', 
                   linewidth=1.5, label='IGR')
        
        if 'Vsh (Old)' in self.data.columns and selected_logs.get('Vsh'):
            ax.plot(self.data['Vsh (Old)'], self.depth, 'brown', 
                   linewidth=1.5, linestyle='--', label='Vsh (Old)')
        
        if 'Vsh (New)' in self.data.columns and selected_logs.get('Vsh'):
            ax.plot(self.data['Vsh (New)'], self.depth, 'saddlebrown', 
                   linewidth=1.5, label='Vsh (New)')
        
        ax.set_xlim(0, 1)
        ax.set_xlabel('')  # Remove x-axis label
        ax.set_title('Shale Volume (V/V)', fontsize=11, fontweight='bold', pad=10)
        ax.legend(loc='lower right', fontsize=8, framealpha=0.9)
    
    def save_plot(self, filename, dpi=300):
        """Save plot to file."""
        if self.fig is None:
            print("✗ No plot to save")
            return False
        
        try:
            self.fig.savefig(filename, dpi=dpi, bbox_inches='tight')
            print(f"✓ Plot saved: {filename}")
            return True
        except Exception as e:
            print(f"✗ Error saving plot: {str(e)}")
            return False


# ============================================================================
# WELL INTERPRETER CLASS
# ============================================================================

class WellInterpreter:
    """Provides automated interpretation of well log data."""
    
    def __init__(self, data):
        """Initialize interpreter with processed data."""
        self.data = data
        
    def analyze_resistivity(self):
        """
        Analyze resistivity for fluid presence.
        
        Rt < Rx: High Salinity Water
        Rt > Rx: Presence of Hydrocarbons
        """
        rt = self.data['Resistivity Rt (OHM.M)']
        rx = self.data['Resistivity Rx (OHM.M)']
        
        interpretation = []
        for i, (rt_val, rx_val) in enumerate(zip(rt, rx)):
            if rt_val < rx_val:
                interpretation.append('High Salinity Water')
            else:
                interpretation.append('Hydrocarbon Presence')
        
        return interpretation
    
    def interpret_density(self):
        """
        Interpret density readings.
        
        > 2.6: Dense formation (Limestone/Dolomite)
        2.2-2.6: Medium density (Porosity present)
        < 2.2: High porosity (Promising for HC)
        """
        density = self.data['Density (G/CC)']
        
        interpretation = []
        for d in density:
            if d > 2.6:
                interpretation.append('Dense Formation')
            elif d >= 2.2:
                interpretation.append('Medium Density')
            else:
                interpretation.append('High Porosity')
        
        return interpretation
    
    def interpret_sonic(self):
        """
        Interpret sonic log.
        
        Lower ITT: Dense/Elastic
        Higher ITT: Porous/Fractured
        """
        sonic = self.data['Sonic (µs/ft)']
        threshold = 100  # Arbitrary threshold for demonstration
        
        interpretation = []
        for s in sonic:
            if s < threshold:
                interpretation.append('Dense/Elastic')
            else:
                interpretation.append('Porous/Fractured')
        
        return interpretation
    
    def lithology_fingerprint(self):
        """
        Determine lithology from log combinations.
        
        High GR + Low Density + High Neutron = Shale
        Low GR + Low Density + High Neutron = Sandstone (Potential Pay)
        Low GR + High Density + Low Neutron = Limestone
        """
        gamma = self.data['Gamma (GAPI)']
        density = self.data['Density (G/CC)']
        neutron = self.data['Neutron CNL (V/V)']
        
        # Calculate statistics for classification
        gr_mean = gamma.mean()
        
        lithology = []
        for g, d, n in zip(gamma, density, neutron):
            if g > gr_mean and d < 2.5 and n > 25:
                lithology.append('Shale (Non-productive)')
            elif g < gr_mean and d < 2.5 and n > 25:
                lithology.append('Sandstone (Potential Pay)')
            elif g < gr_mean and d > 2.6 and n < 20:
                lithology.append('Limestone')
            else:
                lithology.append('Mixed Lithology')
        
        return lithology
    
    def identify_zones(self):
        """
        Identify continuous zones with specific characteristics.
        Returns list of (start_depth, end_depth, zone_type) tuples.
        """
        zones = []
        
        if 'Resistivity Rt (OHM.M)' not in self.data.columns:
            return zones
        
        rt = self.data['Resistivity Rt (OHM.M)'].values
        rx = self.data['Resistivity Rx (OHM.M)'].values
        depth = self.data['Depth (ft)'].values
        
        # Identify hydrocarbon zones (Rt > Rx)
        hc_indicator = rt > rx
        
        in_zone = False
        zone_start = None
        
        for i in range(len(hc_indicator)):
            if hc_indicator[i] and not in_zone:
                # Start of new zone
                zone_start = depth[i]
                in_zone = True
            elif not hc_indicator[i] and in_zone:
                # End of zone
                zones.append((zone_start, depth[i-1], 'Hydrocarbon Indication'))
                in_zone = False
        
        # Close final zone if still open
        if in_zone:
            zones.append((zone_start, depth[-1], 'Hydrocarbon Indication'))
        
        return zones
    
    def classify_porosity_quality(self, porosity):
        """Classify porosity quality."""
        if porosity < 0.05:
            return "Negligible", "Non-productive"
        elif porosity < 0.10:
            return "Poor", "Low productivity potential"
        elif porosity < 0.15:
            return "Fair", "Moderate reservoir quality"
        elif porosity < 0.25:
            return "Good", "Good reservoir quality"
        else:
            return "Excellent", "Excellent reservoir quality"
    
    def classify_saturation(self, sw, shc):
        """Classify saturation levels."""
        if shc < 0.3:
            return "Water-bearing", "High water saturation indicates water zone"
        elif shc < 0.5:
            return "Transition zone", "Mixed water-hydrocarbon zone"
        elif shc < 0.7:
            return "Hydrocarbon-bearing", "Significant hydrocarbon presence"
        else:
            return "High HC saturation", "Excellent hydrocarbon saturation"
    
    def explain_logs(self):
        """Generate explanations for each log type."""
        explanations = []
        explanations.append("=" * 70)
        explanations.append("LOG EXPLANATIONS")
        explanations.append("=" * 70)
        explanations.append("")
        
        if 'Gamma (GAPI)' in self.data.columns:
            explanations.append("GAMMA RAY (GR):")
            explanations.append("  Measures natural radioactivity of formations")
            explanations.append("  High GR (>75 GAPI): Shale/clay-rich formations")
            explanations.append("  Low GR (<75 GAPI): Clean sands or carbonates")
            explanations.append("  Used for lithology identification and correlation")
            explanations.append("")
        
        if 'Resistivity Rt (OHM.M)' in self.data.columns:
            explanations.append("RESISTIVITY:")
            explanations.append("  Rt (True Resistivity): Actual formation resistivity")
            explanations.append("  Rx (Flushed Zone): Resistivity near wellbore")
            explanations.append("  High resistivity: Hydrocarbon or tight formation")
            explanations.append("  Low resistivity: Conductive (water-bearing)")
            explanations.append("  Rt > Rx suggests hydrocarbon presence")
            explanations.append("")
        
        if 'Neutron CNL (V/V)' in self.data.columns:
            explanations.append("NEUTRON LOG:")
            explanations.append("  Responds to hydrogen content (water & hydrocarbons)")
            explanations.append("  High readings: High porosity or hydrogen-rich zones")
            explanations.append("  Used for porosity estimation")
            explanations.append("  Gas zones show characteristic separation from density")
            explanations.append("")
        
        if 'Density (G/CC)' in self.data.columns:
            explanations.append("DENSITY LOG:")
            explanations.append("  Measures bulk density of formation")
            explanations.append("  Low density (<2.2 g/cc): High porosity zones")
            explanations.append("  Medium (2.2-2.6 g/cc): Sandstone with porosity")
            explanations.append("  High (>2.6 g/cc): Dense carbonates or tight zones")
            explanations.append("")
        
        if 'Sonic (µs/ft)' in self.data.columns:
            explanations.append("SONIC LOG:")
            explanations.append("  Measures acoustic wave travel time")
            explanations.append("  High ITT (>100 µs/ft): Porous/fractured formations")
            explanations.append("  Low ITT (<100 µs/ft): Dense/compacted formations")
            explanations.append("  Used for porosity and mechanical properties")
            explanations.append("")
        
        return "\\n".join(explanations)
    
    def generate_summary(self):
        """Generate comprehensive interpretation summary with detailed zone analysis."""
        summary = []
        summary.append("=" * 80)
        summary.append("PETROPHYSICAL INTERPRETATION SUMMARY - DETAILED ANALYSIS")
        summary.append("=" * 80)
        summary.append("")
        
        # Depth range
        depth_min = self.data['Depth (ft)'].min()
        depth_max = self.data['Depth (ft)'].max()
        total_interval = depth_max - depth_min
        summary.append(f"WELL INTERVAL: {depth_min:.1f} - {depth_max:.1f} ft (Total: {total_interval:.1f} ft)")
        summary.append("")
        
        # ===== HYDROCARBON ZONES =====
        summary.append("=" * 80)
        summary.append("HYDROCARBON ZONE IDENTIFICATION")
        summary.append("=" * 80)
        summary.append("")
        
        zones = self.identify_zones()
        if zones:
            summary.append(f"Identified {len(zones)} potential hydrocarbon zone(s):")
            summary.append("")
            for i, (start, end, zone_type) in enumerate(zones, 1):
                thickness = end - start
                summary.append(f"  Zone {i}: {zone_type}")
                summary.append(f"    Depth Range: {start:.1f} - {end:.1f} ft")
                summary.append(f"    Thickness: {thickness:.1f} ft")
                
                # Get average properties in this zone
                zone_mask = (self.data['Depth (ft)'] >= start) & (self.data['Depth (ft)'] <= end)
                if 'Average Porosity' in self.data.columns:
                    avg_por_zone = self.data.loc[zone_mask, 'Average Porosity'].mean()
                    por_quality, por_desc = self.classify_porosity_quality(avg_por_zone)
                    summary.append(f"    Average Porosity: {avg_por_zone:.3f} ({por_quality})")
                
                if 'Shc (Hydrocarbon Saturation)' in self.data.columns:
                    avg_shc_zone = self.data.loc[zone_mask, 'Shc (Hydrocarbon Saturation)'].mean()
                    avg_sw_zone = self.data.loc[zone_mask, 'Sw (Water Saturation)'].mean()
                    sat_class, sat_desc = self.classify_saturation(avg_sw_zone, avg_shc_zone)
                    summary.append(f"    HC Saturation: {avg_shc_zone:.3f} ({sat_class})")
                    summary.append(f"    Interpretation: {sat_desc}")
                
                summary.append("")
        else:
            summary.append("  No significant hydrocarbon zones identified (Rt ≤ Rx throughout)")
            summary.append("  Formation appears water-bearing")
            summary.append("")
        
        # ===== POROSITY ANALYSIS =====
        summary.append("=" * 80)
        summary.append("POROSITY ANALYSIS - DETAILED")
        summary.append("=" * 80)
        summary.append("")
        
        if 'Average Porosity' in self.data.columns:
            avg_por = self.data['Average Porosity'].mean()
            max_por = self.data['Average Porosity'].max()
            min_por = self.data['Average Porosity'].min()
            
            overall_quality, overall_desc = self.classify_porosity_quality(avg_por)
            
            summary.append(f"  Average Porosity: {avg_por:.3f} ({avg_por*100:.1f}%)")
            summary.append(f"  Maximum Porosity: {max_por:.3f} ({max_por*100:.1f}%)")
            summary.append(f"  Minimum Porosity: {min_por:.3f} ({min_por*100:.1f}%)")
            summary.append(f"  Overall Quality: {overall_quality}")
            summary.append(f"  Assessment: {overall_desc}")
            summary.append("")
            
            # Porosity distribution
            excellent = (self.data['Average Porosity'] >= 0.25).sum()
            good = ((self.data['Average Porosity'] >= 0.15) & (self.data['Average Porosity'] < 0.25)).sum()
            fair = ((self.data['Average Porosity'] >= 0.10) & (self.data['Average Porosity'] < 0.15)).sum()
            poor = (self.data['Average Porosity'] < 0.10).sum()
            total_pts = len(self.data)
            
            summary.append("  Porosity Distribution:")
            summary.append(f"    Excellent (≥25%): {excellent} points ({excellent/total_pts*100:.1f}%)")
            summary.append(f"    Good (15-25%): {good} points ({good/total_pts*100:.1f}%)")
            summary.append(f"    Fair (10-15%): {fair} points ({fair/total_pts*100:.1f}%)")
            summary.append(f"    Poor (<10%): {poor} points ({poor/total_pts*100:.1f}%)")
            summary.append("")
        
        # ===== FLUID SATURATION ANALYSIS =====
        summary.append("=" * 80)
        summary.append("FLUID SATURATION ANALYSIS (Archie's Law)")
        summary.append("=" * 80)
        summary.append("")
        
        if 'Sw (Water Saturation)' in self.data.columns:
            avg_sw = self.data['Sw (Water Saturation)'].mean()
            avg_shc = self.data['Shc (Hydrocarbon Saturation)'].mean()
            
            sat_class, sat_desc = self.classify_saturation(avg_sw, avg_shc)
            
            summary.append(f"  Average Water Saturation (Sw): {avg_sw:.3f} ({avg_sw*100:.1f}%)")
            summary.append(f"  Average HC Saturation (Shc): {avg_shc:.3f} ({avg_shc*100:.1f}%)")
            summary.append(f"  Zone Classification: {sat_class}")
            summary.append(f"  Interpretation: {sat_desc}")
            summary.append("")
            
            # Saturation quality distribution
            hc_rich = (self.data['Shc (Hydrocarbon Saturation)'] >= 0.7).sum()
            hc_bearing = ((self.data['Shc (Hydrocarbon Saturation)'] >= 0.5) & (self.data['Shc (Hydrocarbon Saturation)'] < 0.7)).sum()
            transition = ((self.data['Shc (Hydrocarbon Saturation)'] >= 0.3) & (self.data['Shc (Hydrocarbon Saturation)'] < 0.5)).sum()
            water_bearing = (self.data['Shc (Hydrocarbon Saturation)'] < 0.3).sum()
            
            summary.append("  Saturation Distribution:")
            summary.append(f"    High HC (Shc ≥70%): {hc_rich} points ({hc_rich/total_pts*100:.1f}%)")
            summary.append(f"    HC-bearing (50-70%): {hc_bearing} points ({hc_bearing/total_pts*100:.1f}%)")
            summary.append(f"    Transition (30-50%): {transition} points ({transition/total_pts*100:.1f}%)")
            summary.append(f"    Water-bearing (<30%): {water_bearing} points ({water_bearing/total_pts*100:.1f}%)")
            summary.append("")
        
        # ===== LITHOLOGY BY DEPTH RANGES =====
        summary.append("=" * 80)
        summary.append("LITHOLOGY INTERPRETATION BY DEPTH")
        summary.append("=" * 80)
        summary.append("")
        
        if 'Lithology (GR)' in self.data.columns:
            litho_counts = self.data['Lithology (GR)'].value_counts()
            summary.append("  Overall Lithology Distribution:")
            for litho, count in litho_counts.items():
                percentage = (count / len(self.data)) * 100
                summary.append(f"    {litho}: {count} points ({percentage:.1f}%)")
            summary.append("")
            
            # Identify continuous lithology zones
            summary.append("  Lithology Zones:")
            litho_array = self.data['Lithology (GR)'].values
            depth_array = self.data['Depth (ft)'].values
            
            current_litho = litho_array[0]
            zone_start = depth_array[0]
            
            for i in range(1, len(litho_array)):
                if litho_array[i] != current_litho:
                    # Lithology changed, record previous zone
                    summary.append(f"    {zone_start:.1f} - {depth_array[i-1]:.1f} ft: {current_litho}")
                    current_litho = litho_array[i]
                    zone_start = depth_array[i]
            
            # Record final zone
            summary.append(f"    {zone_start:.1f} - {depth_array[-1]:.1f} ft: {current_litho}")
            summary.append("")
        
        # ===== RESISTIVITY ANALYSIS =====
        summary.append("=" * 80)
        summary.append("RESISTIVITY ANALYSIS")
        summary.append("=" * 80)
        summary.append("")
        
        if 'Resistivity Rt (OHM.M)' in self.data.columns:
            rt = self.data['Resistivity Rt (OHM.M)']
            rx = self.data['Resistivity Rx (OHM.M)']
            hc_zones_pts = (rt > rx).sum()
            water_zones_pts = (rt <= rx).sum()
            
            summary.append(f"  Average Rt (True Resistivity): {rt.mean():.2f} OHM.M")
            summary.append(f"  Average Rx (Flushed Zone): {rx.mean():.2f} OHM.M")
            summary.append(f"  Maximum Rt: {rt.max():.2f} OHM.M")
            summary.append("")
            summary.append(f"  Hydrocarbon indication points (Rt > Rx): {hc_zones_pts} ({hc_zones_pts/len(self.data)*100:.1f}%)")
            summary.append(f"  Water indication points (Rt ≤ Rx): {water_zones_pts} ({water_zones_pts/len(self.data)*100:.1f}%)")
            summary.append("")
        
        # ===== LOG EXPLANATIONS =====
        summary.append("")
        summary.append(self.explain_logs())
        
        # ===== RECOMMENDATIONS =====
        summary.append("=" * 80)
        summary.append("PETROPHYSICIST RECOMMENDATIONS")
        summary.append("=" * 80)
        summary.append("")
        
        if zones:
            summary.append("  ✓ POTENTIAL PAY ZONES IDENTIFIED")
            summary.append(f"    → Recommend detailed analysis of {len(zones)} zone(s)")
            if 'Average Porosity' in self.data.columns and avg_por >= 0.15:
                summary.append("    → Good reservoir quality present")
            if 'Shc (Hydrocarbon Saturation)' in self.data.columns and avg_shc >= 0.5:
                summary.append("    → Significant hydrocarbon saturation")
            summary.append("    → Consider core analysis and pressure testing")
        else:
            summary.append("  ! NO SIGNIFICANT PAY ZONES")
            summary.append("    → Formation appears predominantly water-bearing")
            summary.append("    → Review completion strategy")
        
        summary.append("")
        summary.append("=" * 80)
        
        return "\\n".join(summary)


# ============================================================================
# RESULTS EXPORTER CLASS
# ============================================================================

class ResultsExporter:
    """Handles exporting results to Excel and image files."""
    
    @staticmethod
    def export_to_excel(data, filepath, summary_text=""):
        """
        Export all data and calculations to Excel.
        
        Parameters:
        -----------
        data : DataFrame
            Complete dataset with all calculations
        filepath : str
            Output file path
        summary_text : str
            Interpretation summary to include
        """
        try:
            with pd.ExcelWriter(filepath, engine='openpyxl') as writer:
                # Main data sheet
                data.to_excel(writer, sheet_name='Well Log Data', index=False)
                
                # Summary statistics
                stats = data.describe()
                stats.to_excel(writer, sheet_name='Statistics')
                
                # Interpretation summary
                if summary_text:
                    summary_lines = summary_text.split('\n')
                    summary_df = pd.DataFrame({'Interpretation Summary': summary_lines})
                    summary_df.to_excel(writer, sheet_name='Interpretation', index=False)
            
            print(f"✓ Data exported to Excel: {filepath}")
            return True
        except Exception as e:
            print(f"✗ Error exporting to Excel: {str(e)}")
            return False
    
    @staticmethod
    def export_plots(figure, filepath_png, filepath_pdf=None, dpi=300):
        """
        Export plots to PNG and optionally PDF.
        
        Parameters:
        -----------
        figure : matplotlib.figure.Figure
            Figure to export
        filepath_png : str
            PNG output path
        filepath_pdf : str, optional
            PDF output path
        dpi : int
            Resolution for PNG
        """
        try:
            # Save PNG
            figure.savefig(filepath_png, dpi=dpi, bbox_inches='tight')
            print(f"✓ Plot saved as PNG: {filepath_png}")
            
            # Save PDF if requested
            if filepath_pdf:
                figure.savefig(filepath_pdf, format='pdf', bbox_inches='tight')
                print(f"✓ Plot saved as PDF: {filepath_pdf}")
            
            return True
        except Exception as e:
            print(f"✗ Error exporting plots: {str(e)}")
            return False
    
    @staticmethod
    def create_results_package(data, figure, interpretation_summary, base_name="well_analysis"):
        """
        Create a complete results package with all outputs.
        
        Parameters:
        -----------
        data : DataFrame
            Complete dataset
        figure : matplotlib.figure.Figure
            Log plot figure
        interpretation_summary : str
            Text summary of interpretation
        base_name : str
            Base name for output files
        """
        # Create timestamped folder
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        folder_name = f"{base_name}_{timestamp}"
        os.makedirs(folder_name, exist_ok=True)
        
        print(f"\n{'='*70}")
        print(f"Creating results package: {folder_name}")
        print(f"{'='*70}\n")
        
        # Export Excel
        excel_path = os.path.join(folder_name, f"{base_name}_data.xlsx")
        ResultsExporter.export_to_excel(data, excel_path, interpretation_summary)
        
        # Export plots
        png_path = os.path.join(folder_name, f"{base_name}_plot.png")
        pdf_path = os.path.join(folder_name, f"{base_name}_plot.pdf")
        ResultsExporter.export_plots(figure, png_path, pdf_path)
        
        # Export interpretation summary as text file
        summary_path = os.path.join(folder_name, f"{base_name}_summary.txt")
        with open(summary_path, 'w') as f:
            f.write(interpretation_summary)
        print(f"✓ Summary saved: {summary_path}")
        
        print(f"\n{'='*70}")
        print(f"✓ Results package created successfully!")
        print(f"  Location: {os.path.abspath(folder_name)}")
        print(f"{'='*70}\n")
        
        return folder_name


# ============================================================================
# USER INTERFACE CLASS
# ============================================================================

class WellLoggerUI:
    """Main user interface for the Petrophysics Well Logger application."""
    
    def __init__(self):
        """Initialize the application."""
        self.data = None
        self.processed_data = None
        self.calculator = PetrophysicsCalculator()
        self.selected_logs = {}
        
    def display_banner(self):
        """Display application banner."""
        print("\n" + "="*70)
        print(" " * 15 + "PETROPHYSICS WELL LOGGER")
        print(" " * 10 + "Well Data Logging and Interpretation Suite")
        print("="*70 + "\n")
    
    def main_menu(self):
        """Display main menu and get user selection."""
        print("\nMAIN MENU:")
        print("1. Generate Excel Template")
        print("2. Load and Process Well Data")
        print("3. Select Logs for Analysis")
        print("4. Generate Plots and Interpretation")
        print("5. Export Results")
        print("6. Run Complete Workflow")
        print("0. Exit")
        
        choice = input("\nEnter your choice (0-6): ").strip()
        return choice
    
    def generate_template_workflow(self):
        """Workflow for generating Excel template."""
        print("\n" + "-"*70)
        print("GENERATE EXCEL TEMPLATE")
        print("-"*70)
        
        filename = input("Enter template filename (default: well_log_template.xlsx): ").strip()
        if not filename:
            filename = "well_log_template.xlsx"
        
        if not filename.endswith('.xlsx'):
            filename += '.xlsx'
        
        TemplateGenerator.generate_template(filename)
        input("\nPress Enter to continue...")
    
    def load_data_workflow(self):
        """Workflow for loading and processing data."""
        print("\n" + "-"*70)
        print("LOAD AND PROCESS WELL DATA")
        print("-"*70)
        
        filepath = input("Enter Excel file path: ").strip()
        
        if not os.path.exists(filepath):
            print(f"✗ File not found: {filepath}")
            input("\nPress Enter to continue...")
            return
        
        # Load data
        loader = DataLoader(filepath)
        if not loader.load_excel():
            input("\nPress Enter to continue...")
            return
        
        if not loader.validate_data():
            input("\nPress Enter to continue...")
            return
        
        loader.handle_nulls()
        stats = loader.get_statistics()
        
        self.data = loader.data
        
        # Calculate all derived logs
        print("\nCalculating derived logs...")
        self._calculate_all_logs(stats)
        
        print("\n✓ Data processing complete!")
        input("\nPress Enter to continue...")
    
    def _calculate_all_logs(self, stats):
        """Calculate all petrophysical logs."""
        calc = self.calculator
        
        # Gamma Ray derived calculations
        if 'Gamma (GAPI)' in self.data.columns:
            gr_min = stats.get('GR_MIN', self.data['Gamma (GAPI)'].min())
            gr_max = stats.get('GR_MAX', self.data['Gamma (GAPI)'].max())
            
            self.data['IGR'] = calc.calculate_IGR(
                self.data['Gamma (GAPI)'], gr_min, gr_max
            )
            self.data['Vsh (Old)'] = calc.calculate_vsh_old(self.data['IGR'])
            self.data['Vsh (New)'] = calc.calculate_vsh_new(self.data['IGR'])
            self.data['Lithology (GR)'] = calc.classify_lithology_gr(self.data['Vsh (New)'])
            print("  ✓ Shale volume calculations complete")
        
        # Porosity calculations
        if 'Sonic (µs/ft)' in self.data.columns:
            self.data['Porosity (Sonic)'] = calc.calculate_sonic_porosity(
                self.data['Sonic (µs/ft)']
            )
            print("  ✓ Sonic porosity calculated")
        
        if 'Density (G/CC)' in self.data.columns and 'Lithology (GR)' in self.data.columns:
            self.data['Porosity (Density)'] = calc.calculate_density_porosity(
                self.data['Density (G/CC)'],
                self.data['Lithology (GR)']
            )
            print("  ✓ Density porosity calculated")
        
        if 'Neutron CNL (V/V)' in self.data.columns:
            self.data['Porosity (Neutron)'] = calc.calculate_neutron_porosity(
                self.data['Neutron CNL (V/V)']
            )
            print("  ✓ Neutron porosity calculated")
        
        # Average porosity
        if all(col in self.data.columns for col in ['Porosity (Sonic)', 'Porosity (Density)', 'Porosity (Neutron)']):
            self.data['Average Porosity'] = calc.calculate_average_porosity(
                self.data['Porosity (Sonic)'],
                self.data['Porosity (Density)'],
                self.data['Porosity (Neutron)']
            )
            print("  ✓ Average porosity calculated")
        
        # Neutron-Density Vsh
        if 'Porosity (Neutron)' in self.data.columns and 'Porosity (Density)' in self.data.columns:
            self.data['Vsh (N-D)'] = calc.calculate_vsh_neutron_density(
                self.data['Porosity (Neutron)'],
                self.data['Porosity (Density)']
            )
            print("  ✓ Neutron-Density Vsh calculated")
        
        # Archie saturation
        if 'Average Porosity' in self.data.columns and 'Resistivity Rt (OHM.M)' in self.data.columns:
            self.data['Sw (Water Saturation)'] = calc.calculate_sw(
                self.data['Average Porosity'],
                self.data['Resistivity Rt (OHM.M)']
            )
            self.data['Shc (Hydrocarbon Saturation)'] = calc.calculate_shc(
                self.data['Sw (Water Saturation)']
            )
            print("  ✓ Archie fluid saturation calculated")
        
        self.processed_data = self.data.copy()
    
    def select_logs_workflow(self):
        """Workflow for selecting logs to display."""
        if self.processed_data is None:
            print("\n✗ Please load and process data first!")
            input("\nPress Enter to continue...")
            return
        
        print("\n" + "-"*70)
        print("SELECT LOGS FOR ANALYSIS")
        print("-"*70)
        print("\nAvailable logs:")
        print("1. Gamma Ray")
        print("2. Resistivity (Rt and Rx)")
        print("3. Neutron")
        print("4. Density")
        print("5. Sonic")
        print("6. Porosity (individual: Sonic, Neutron, Density)")
        print("7. Average Porosity")
        print("8. Archie Fluid Saturation (Sw and Shc)")
        print("9. IGR (Gamma Ray Index)")
        print("10. Vsh (Old and New formulas)")
        print("11. Neutron-Density Crossover")
        
        print("\nEnter log numbers separated by commas (e.g., 1,2,6,8):")
        selection = input("Selection: ").strip()
        
        # Parse selection
        selected = [s.strip() for s in selection.split(',')]
        
        self.selected_logs = {
            'Gamma': '1' in selected,
            'Resistivity': '2' in selected,
            'Neutron': '3' in selected,
            'Density': '4' in selected,
            'Sonic': '5' in selected,
            'Porosity': '6' in selected,
            'Average Porosity': '7' in selected,
            'Archie': '8' in selected,
            'IGR': '9' in selected,
            'Vsh': '10' in selected,
            'Neutron-Density': '11' in selected
        }
        
        print("\n✓ Log selection saved!")
        input("\nPress Enter to continue...")
    
    def generate_plots_workflow(self):
        """Workflow for generating plots and interpretation."""
        if self.processed_data is None:
            print("\n✗ Please load and process data first!")
            input("\nPress Enter to continue...")
            return
        
        if not any(self.selected_logs.values()):
            print("\n✗ Please select logs first!")
            input("\nPress Enter to continue...")
            return
        
        print("\n" + "-"*70)
        print("GENERATING PLOTS AND INTERPRETATION")
        print("-"*70)
        
        # Create plots
        plotter = LogPlotter(self.processed_data)
        fig = plotter.create_multitrack_plot(self.selected_logs)
        
        if fig is None:
            input("\nPress Enter to continue...")
            return
        
        # Generate interpretation
        interpreter = WellInterpreter(self.processed_data)
        summary = interpreter.generate_summary()
        
        print("\n" + summary)
        
        # Display plot
        plt.show()
        
        # Store for export
        self.current_figure = fig
        self.current_summary = summary
        
        input("\nPress Enter to continue...")
    
    def export_results_workflow(self):
        """Workflow for exporting results."""
        if self.processed_data is None:
            print("\n✗ No data to export!")
            input("\nPress Enter to continue...")
            return
        
        print("\n" + "-"*70)
        print("EXPORT RESULTS")
        print("-"*70)
        print("\n1. Export Data to Excel only")
        print("2. Export Plots only (PNG + PDF)")
        print("3. Create Complete Results Package")
        
        choice = input("\nEnter choice (1-3): ").strip()
        
        if choice == '1':
            filename = input("Enter Excel filename (default: well_data_export.xlsx): ").strip()
            if not filename:
                filename = "well_data_export.xlsx"
            if not filename.endswith('.xlsx'):
                filename += '.xlsx'
            
            summary = getattr(self, 'current_summary', '')
            ResultsExporter.export_to_excel(self.processed_data, filename, summary)
        
        elif choice == '2':
            if not hasattr(self, 'current_figure'):
                print("\n✗ Please generate plots first!")
                input("\nPress Enter to continue...")
                return
            
            base_name = input("Enter base filename (default: well_plot): ").strip()
            if not base_name:
                base_name = "well_plot"
            
            png_path = f"{base_name}.png"
            pdf_path = f"{base_name}.pdf"
            
            ResultsExporter.export_plots(self.current_figure, png_path, pdf_path)
        
        elif choice == '3':
            if not hasattr(self, 'current_figure'):
                print("\n✗ Please generate plots first!")
                input("\nPress Enter to continue...")
                return
            
            base_name = input("Enter project name (default: well_analysis): ").strip()
            if not base_name:
                base_name = "well_analysis"
            
            ResultsExporter.create_results_package(
                self.processed_data,
                self.current_figure,
                self.current_summary,
                base_name
            )
        
        input("\nPress Enter to continue...")
    
    def run_complete_workflow(self):
        """Run the complete analysis workflow."""
        print("\n" + "="*70)
        print("COMPLETE WORKFLOW")
        print("="*70)
        
        # Step 1: Generate template
        print("\nStep 1: Generate Template")
        generate = input("Generate new template? (y/n): ").strip().lower()
        if generate == 'y':
            self.generate_template_workflow()
        
        # Step 2: Load data
        print("\nStep 2: Load Data")
        self.load_data_workflow()
        
        if self.processed_data is None:
            return
        
        # Step 3: Select all logs by default
        print("\nStep 3: Selecting all available logs...")
        self.selected_logs = {
            'Gamma': True,
            'Resistivity': True,
            'Neutron': False,
            'Density': False,
            'Sonic': True,
            'Porosity': True,
            'Average Porosity': True,
            'Archie': True,
            'IGR': False,
            'Vsh': True,
            'Neutron-Density': True
        }
        print("✓ Default log selection applied")
        
        # Step 4: Generate plots
        print("\nStep 4: Generating Plots and Interpretation...")
        self.generate_plots_workflow()
        
        # Step 5: Export
        print("\nStep 5: Export Results")
        export = input("Create complete results package? (y/n): ").strip().lower()
        if export == 'y':
            base_name = input("Enter project name (default: well_analysis): ").strip()
            if not base_name:
                base_name = "well_analysis"
            
            ResultsExporter.create_results_package(
                self.processed_data,
                self.current_figure,
                self.current_summary,
                base_name
            )
        
        input("\nWorkflow complete! Press Enter to return to main menu...")
    
    def run(self):
        """Main application loop."""
        self.display_banner()
        
        while True:
            choice = self.main_menu()
            
            if choice == '0':
                print("\nThank you for using Petrophysics Well Logger!")
                break
            elif choice == '1':
                self.generate_template_workflow()
            elif choice == '2':
                self.load_data_workflow()
            elif choice == '3':
                self.select_logs_workflow()
            elif choice == '4':
                self.generate_plots_workflow()
            elif choice == '5':
                self.export_results_workflow()
            elif choice == '6':
                self.run_complete_workflow()
            else:
                print("\n✗ Invalid choice. Please try again.")
                input("\nPress Enter to continue...")


# ============================================================================
# MAIN ENTRY POINT
# ============================================================================

if __name__ == "__main__":
    app = WellLoggerUI()
    app.run()
