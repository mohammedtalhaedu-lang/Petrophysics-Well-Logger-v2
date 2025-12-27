"""
Petrophysics Well Logger - GUI Application
A comprehensive well data logging and interpretation suite with modern graphical interface.

Author: Petrophysical Software Engineer
Version: 2.0 (GUI Edition)
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
import os
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')

# Import calculation modules from well_logger.py
from well_logger import (
    TemplateGenerator, DataLoader, PetrophysicsCalculator,
    LogPlotter, WellInterpreter, ResultsExporter,
    DENSITY_SANDSTONE, DENSITY_SHALE, DENSITY_FLUID,
    ITT_MATRIX, ITT_FLUID,
    ARCHIE_A, ARCHIE_RW, ARCHIE_M, ARCHIE_N,
    PHI_NEUTRON_SHALE, PHI_DENSITY_SHALE,
    COLOR_OIL, COLOR_GAS, COLOR_WATER
)

# ============================================================================
# MODERN GUI APPLICATION
# ============================================================================

class PetrophysicsWellLoggerGUI:
    """Modern GUI application for well log analysis."""
    
    def __init__(self, root):
        """Initialize the GUI application."""
        self.root = root
        self.root.title("Petrophysics Well Logger")
        self.root.geometry("1400x900")
        self.root.configure(bg='#2b2b2b')
        
        # Data storage
        self.data = None
        self.processed_data = None
        self.calculator = PetrophysicsCalculator()
        self.current_figure = None
        self.current_summary = ""
        self.selected_logs = {}
        
        # Create UI
        self.create_widgets()
        
    def create_widgets(self):
        """Create all GUI widgets."""
        # ===== HEADER =====
        header_frame = tk.Frame(self.root, bg='#1e3a5f', height=80)
        header_frame.pack(fill=tk.X, pady=(0, 10))
        header_frame.pack_propagate(False)
        
        title_label = tk.Label(
            header_frame,
            text="PETROPHYSICS WELL LOGGER",
            font=('Arial', 24, 'bold'),
            bg='#1e3a5f',
            fg='white'
        )
        title_label.pack(pady=20)
        
        subtitle_label = tk.Label(
            header_frame,
            text="Well Data Logging and Interpretation Suite",
            font=('Arial', 12),
            bg='#1e3a5f',
            fg='#a0c4ff'
        )
        subtitle_label.pack()
        
        # ===== MAIN CONTAINER =====
        main_container = tk.Frame(self.root, bg='#2b2b2b')
        main_container.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Left Panel - Controls
        left_panel = tk.Frame(main_container, bg='#383838', width=400)
        left_panel.pack(side=tk.LEFT, fill=tk.BOTH, padx=(0, 10))
        left_panel.pack_propagate(False)
        
        # Right Panel - Visualization
        right_panel = tk.Frame(main_container, bg='#383838')
        right_panel.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        
        # ===== LEFT PANEL CONTENT =====
        self.create_left_panel(left_panel)
        
        # ===== RIGHT PANEL CONTENT =====
        self.create_right_panel(right_panel)
        
    def create_left_panel(self, parent):
        """Create left control panel with scrollable canvas."""
        # Create canvas and scrollbar
        canvas = tk.Canvas(parent, bg='#383838', highlightthickness=0)
        scrollbar = ttk.Scrollbar(parent, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg='#383838')
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # Pack scrollbar and canvas
        scrollbar.pack(side="right", fill="y")
        canvas.pack(side="left", fill="both", expand=True)
        
        # Enable mousewheel scrolling
        def _on_mousewheel(event):
            canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        canvas.bind_all("<MouseWheel>", _on_mousewheel)
        
        # Title
        control_title = tk.Label(
            scrollable_frame,
            text="Control Panel",
            font=('Arial', 16, 'bold'),
            bg='#383838',
            fg='white'
        )
        control_title.pack(pady=15)
        
        # Section 1: Template Generation
        self.create_section(scrollable_frame, "1. Template Generation",
                          [("Generate Excel Template", self.generate_template)])
        
        # Section 2: Data Loading
        self.create_section(scrollable_frame, "2. Data Loading",
                          [("Load Well Data", self.load_data)])
        
        # Data status
        self.data_status_label = tk.Label(
            scrollable_frame,
            text="No data loaded",
            font=('Arial', 9),
            bg='#383838',
            fg='#ff6b6b'
        )
        self.data_status_label.pack(pady=5)
        
        # Section 3: Log Selection
        log_section_frame = tk.LabelFrame(
            scrollable_frame,
            text="3. Select Logs to Analyze",
            font=('Arial', 11, 'bold'),
            bg='#4a4a4a',
            fg='white',
            padx=10,
            pady=10
        )
        log_section_frame.pack(fill=tk.X, padx=15, pady=10)
        
        # Create checkboxes for log selection
        self.log_vars = {}
        logs = [
            ('Gamma', 'Gamma Ray'),
            ('Resistivity', 'Resistivity (Rt & Rx)'),
            ('Neutron', 'Neutron'),
            ('Density', 'Density'),
            ('Sonic', 'Sonic'),
            ('Average Porosity', 'Average Porosity'),
            ('Archie', 'Archie Saturation'),
            ('IGR', 'IGR'),
            ('Vsh', 'Vsh (Old & New)'),
            ('Neutron-Density', 'Neutron-Density Crossover')
        ]
        
        for key, label in logs:
            var = tk.BooleanVar(value=False)
            self.log_vars[key] = var
            cb = tk.Checkbutton(
                log_section_frame,
                text=label,
                variable=var,
                font=('Arial', 9),
                bg='#4a4a4a',
                fg='white',
                selectcolor='#2b2b2b',
                activebackground='#4a4a4a',
                activeforeground='white'
            )
            cb.pack(anchor=tk.W, pady=2)
        
        # Section 4: Analysis
        self.create_section(scrollable_frame, "4. Generate Analysis",
                          [("Generate Plots & Interpretation", self.generate_analysis)])
        
        # Section 5: Export
        export_section_frame = tk.LabelFrame(
            scrollable_frame,
            text="5. Export Results",
            font=('Arial', 11, 'bold'),
            bg='#4a4a4a',
            fg='white',
            padx=10,
            pady=10
        )
        export_section_frame.pack(fill=tk.X, padx=15, pady=10)
        
        export_btn1 = self.create_button(export_section_frame, "Export Excel Data", self.export_excel)
        export_btn1.pack(fill=tk.X, pady=5)
        
        export_btn2 = self.create_button(export_section_frame, "Export Plots (PNG/PDF)", self.export_plots)
        export_btn2.pack(fill=tk.X, pady=5)
        
        export_btn3 = self.create_button(export_section_frame, "Export Complete Package", self.export_all, bg='#28a745')
        export_btn3.pack(fill=tk.X, pady=5)
        
    def create_right_panel(self, parent):
        """Create right visualization panel."""
        # Notebook for tabs
        self.notebook = ttk.Notebook(parent)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Tab 1: Visualization
        viz_frame = tk.Frame(self.notebook, bg='#383838')
        self.notebook.add(viz_frame, text="Visualization")
        
        # Matplotlib canvas container
        self.plot_container = tk.Frame(viz_frame, bg='#383838')
        self.plot_container.pack(fill=tk.BOTH, expand=True)
        
        # Welcome message
        self.welcome_label = tk.Label(
            self.plot_container,
            text="📊 Load data and generate plots to view visualization here",
            font=('Arial', 14),
            bg='#383838',
            fg='#a0a0a0'
        )
        self.welcome_label.pack(expand=True)
        
        # Tab 2: Interpretation Summary
        summary_frame = tk.Frame(self.notebook, bg='#383838')
        self.notebook.add(summary_frame, text="Interpretation Summary")
        
        summary_title = tk.Label(
            summary_frame,
            text="📊 Petrophysical Interpretation Report",
            font=('Arial', 16, 'bold'),
            bg='#383838',
            fg='white'
        )
        summary_title.pack(pady=15)
        
        # Create frame for summary text with better styling
        text_frame = tk.Frame(summary_frame, bg='#2b2b2b', relief=tk.RIDGE, borderwidth=2)
        text_frame.pack(fill=tk.BOTH, expand=True, padx=15, pady=(0, 15))
        
        self.summary_text = tk.Text(
            text_frame,
            wrap=tk.WORD,
            font=('Consolas', 10),
            bg='#1e1e1e',
            fg='#e0e0e0',
            insertbackground='white',
            padx=15,
            pady=15,
            relief=tk.FLAT
        )
        
        # Add scrollbar
        scrollbar = ttk.Scrollbar(text_frame, command=self.summary_text.yview)
        self.summary_text.configure(yscrollcommand=scrollbar.set)
        
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.summary_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # Configure text tags for formatting
        self.summary_text.tag_configure("title", foreground="#4CAF50", font=('Arial', 14, 'bold'))
        self.summary_text.tag_configure("section", foreground="#2196F3", font=('Arial', 12, 'bold'))
        self.summary_text.tag_configure("subsection", foreground="#FF9800", font=('Consolas', 10, 'bold'))
        self.summary_text.tag_configure("important", foreground="#FFD700", font=('Consolas', 10, 'bold'))
        self.summary_text.tag_configure("success", foreground="#4CAF50", font=('Consolas', 10, 'bold'))
        self.summary_text.tag_configure("warning", foreground="#FF5722", font=('Consolas', 10, 'bold'))
        self.summary_text.tag_configure("normal", foreground="#e0e0e0")
        
        # Initial message
        self.summary_text.insert('1.0', "Load and analyze well data to generate a detailed interpretation report...", "normal")
        self.summary_text.config(state=tk.DISABLED)
        
    def create_section(self, parent, title, buttons):
        """Create a section with title and buttons."""
        section_frame = tk.LabelFrame(
            parent,
            text=title,
            font=('Arial', 11, 'bold'),
            bg='#4a4a4a',
            fg='white',
            padx=10,
            pady=10
        )
        section_frame.pack(fill=tk.X, padx=15, pady=10)
        
        for btn_text, btn_command in buttons:
            btn = self.create_button(section_frame, btn_text, btn_command)
            btn.pack(fill=tk.X, pady=5)
    
    def create_button(self, parent, text, command, bg='#007bff'):
        """Create a styled button."""
        btn = tk.Button(
            parent,
            text=text,
            command=command,
            font=('Arial', 10, 'bold'),
            bg=bg,
            fg='white',
            activebackground='#0056b3',
            activeforeground='white',
            relief=tk.FLAT,
            cursor='hand2',
            padx=10,
            pady=8
        )
        return btn
    
    # ===== FUNCTIONALITY METHODS =====
    
    def generate_template(self):
        """Generate Excel template."""
        filename = filedialog.asksaveasfilename(
            defaultextension=".xlsx",
            filetypes=[("Excel files", "*.xlsx")],
            initialfile="well_log_template.xlsx"
        )
        
        if filename:
            TemplateGenerator.generate_template(filename)
            messagebox.showinfo(
                "Success",
                f"Template generated successfully!\n\n{filename}\n\nPlease fill the template with your well log data."
            )
    
    def load_data(self):
        """Load and process well data."""
        filename = filedialog.askopenfilename(
            title="Select Well Log Data",
            filetypes=[("Excel files", "*.xlsx"), ("All files", "*.*")]
        )
        
        if not filename:
            return
        
        try:
            # Load data
            loader = DataLoader(filename)
            if not loader.load_excel():
                messagebox.showerror("Error", "Failed to load Excel file")
                return
            
            if not loader.validate_data():
                messagebox.showerror("Error", "Missing required columns in Excel file")
                return
            
            loader.handle_nulls()
            stats = loader.get_statistics()
            
            self.data = loader.data
            
            # Calculate all derived logs
            self._calculate_all_logs(stats)
            
            # Update status
            self.data_status_label.config(
                text=f"✓ Data loaded: {len(self.data)} depth points",
                fg='#4caf50'
            )
            
            messagebox.showinfo(
                "Success",
                f"Data loaded successfully!\n\nDepth points: {len(self.data)}\nDepth range: {self.data['Depth (ft)'].min():.1f} - {self.data['Depth (ft)'].max():.1f} ft"
            )
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load data:\n{str(e)}")
    
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
        
        # Porosity calculations
        if 'Sonic (µs/ft)' in self.data.columns:
            self.data['Porosity (Sonic)'] = calc.calculate_sonic_porosity(
                self.data['Sonic (µs/ft)']
            )
        
        if 'Density (G/CC)' in self.data.columns and 'Lithology (GR)' in self.data.columns:
            self.data['Porosity (Density)'] = calc.calculate_density_porosity(
                self.data['Density (G/CC)'],
                self.data['Lithology (GR)']
            )
        
        if 'Neutron CNL (V/V)' in self.data.columns:
            self.data['Porosity (Neutron)'] = calc.calculate_neutron_porosity(
                self.data['Neutron CNL (V/V)']
            )
        
        # Average porosity
        if all(col in self.data.columns for col in ['Porosity (Sonic)', 'Porosity (Density)', 'Porosity (Neutron)']):
            self.data['Average Porosity'] = calc.calculate_average_porosity(
                self.data['Porosity (Sonic)'],
                self.data['Porosity (Density)'],
                self.data['Porosity (Neutron)']
            )
        
        # Neutron-Density Vsh
        if 'Porosity (Neutron)' in self.data.columns and 'Porosity (Density)' in self.data.columns:
            self.data['Vsh (N-D)'] = calc.calculate_vsh_neutron_density(
                self.data['Porosity (Neutron)'],
                self.data['Porosity (Density)']
            )
        
        # Archie saturation
        if 'Average Porosity' in self.data.columns and 'Resistivity Rt (OHM.M)' in self.data.columns:
            self.data['Sw (Water Saturation)'] = calc.calculate_sw(
                self.data['Average Porosity'],
                self.data['Resistivity Rt (OHM.M)']
            )
            self.data['Shc (Hydrocarbon Saturation)'] = calc.calculate_shc(
                self.data['Sw (Water Saturation)']
            )
        
        self.processed_data = self.data.copy()
    
    def generate_analysis(self):
        """Generate plots and interpretation."""
        if self.processed_data is None:
            messagebox.showwarning("No Data", "Please load well data first!")
            return
        
        # Get selected logs
        self.selected_logs = {key: var.get() for key, var in self.log_vars.items()}
        
        if not any(self.selected_logs.values()):
            messagebox.showwarning("No Logs Selected", "Please select at least one log to analyze!")
            return
        
        try:
            # Clear previous plot
            for widget in self.plot_container.winfo_children():
                widget.destroy()
            
            # Create plots
            plotter = LogPlotter(self.processed_data)
            fig = plotter.create_multitrack_plot(self.selected_logs)
            
            if fig is None:
                messagebox.showerror("Error", "Failed to generate plots")
                return
            
            # Create scrollable canvas for the plot
            # Create a frame to hold the canvas and scrollbars
            plot_frame = tk.Frame(self.plot_container, bg='#383838')
            plot_frame.pack(fill=tk.BOTH, expand=True)
            
            # Create canvas and scrollbars
            canvas = tk.Canvas(plot_frame, bg='#383838', highlightthickness=0)
            v_scrollbar = ttk.Scrollbar(plot_frame, orient="vertical", command=canvas.yview)
            h_scrollbar = ttk.Scrollbar(plot_frame, orient="horizontal", command=canvas.xview)
            
            # Create frame inside canvas for matplotlib
            scrollable_frame = tk.Frame(canvas, bg='#383838')
            
            # Configure canvas scrolling
            scrollable_frame.bind(
                "<Configure>",
                lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
            )
            
            canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
            canvas.configure(yscrollcommand=v_scrollbar.set, xscrollcommand=h_scrollbar.set)
            
            # Pack scrollbars and canvas
            v_scrollbar.pack(side="right", fill="y")
            h_scrollbar.pack(side="bottom", fill="x")
            canvas.pack(side="left", fill="both", expand=True)
            
            # Embed matplotlib figure in scrollable frame
            mpl_canvas = FigureCanvasTkAgg(fig, master=scrollable_frame)
            mpl_canvas.draw()
            mpl_canvas.get_tk_widget().pack()
            
            # Enable mousewheel scrolling
            def _on_mousewheel(event):
                canvas.yview_scroll(int(-1*(event.delta/120)), "units")
            canvas.bind_all("<MouseWheel>", _on_mousewheel)
            
            self.current_figure = fig
            
            # Generate interpretation
            interpreter = WellInterpreter(self.processed_data)
            summary = interpreter.generate_summary()
            self.current_summary = summary
            
            # Update summary tab
            self.summary_text.config(state=tk.NORMAL)
            self.summary_text.delete('1.0', tk.END)
            self.summary_text.insert('1.0', summary)
            self.summary_text.config(state=tk.DISABLED)
            
            messagebox.showinfo("Success", "Analysis generated successfully!\n\nCheck the Visualization and Interpretation tabs.")
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to generate analysis:\n{str(e)}")
    
    def export_excel(self):
        """Export data to Excel."""
        if self.processed_data is None:
            messagebox.showwarning("No Data", "No data to export!")
            return
        
        filename = filedialog.asksaveasfilename(
            defaultextension=".xlsx",
            filetypes=[("Excel files", "*.xlsx")],
            initialfile="well_data_export.xlsx"
        )
        
        if filename:
            ResultsExporter.export_to_excel(self.processed_data, filename, self.current_summary)
            messagebox.showinfo("Success", f"Data exported successfully to:\n{filename}")
    
    def export_plots(self):
        """Export plots to PNG and PDF."""
        if self.current_figure is None:
            messagebox.showwarning("No Plot", "Please generate plots first!")
            return
        
        filename = filedialog.asksaveasfilename(
            defaultextension=".png",
            filetypes=[("PNG files", "*.png"), ("PDF files", "*.pdf")],
            initialfile="well_plot.png"
        )
        
        if filename:
            base_name = os.path.splitext(filename)[0]
            png_path = base_name + ".png"
            pdf_path = base_name + ".pdf"
            
            ResultsExporter.export_plots(self.current_figure, png_path, pdf_path)
            messagebox.showinfo("Success", f"Plots exported successfully:\n{png_path}\n{pdf_path}")
    
    def export_all(self):
        """Export complete results package."""
        if self.processed_data is None or self.current_figure is None:
            messagebox.showwarning("Incomplete Data", "Please load data and generate analysis first!")
            return
        
        folder = filedialog.askdirectory(title="Select folder to save results")
        
        if folder:
            base_name = os.path.join(folder, "well_analysis")
            ResultsExporter.create_results_package(
                self.processed_data,
                self.current_figure,
                self.current_summary,
                base_name
            )
            messagebox.showinfo("Success", f"Complete results package exported to:\n{folder}")


# ============================================================================
# MAIN ENTRY POINT
# ============================================================================

def main():
    """Main application entry point."""
    root = tk.Tk()
    app = PetrophysicsWellLoggerGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()
