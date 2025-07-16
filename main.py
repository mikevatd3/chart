#!/usr/bin/env python3
"""
CSV Chart CLI Tool with Everforest Theme
Automatically creates histograms or scatter plots based on CSV column count.
"""

import sys
import csv
import click
import matplotlib
import matplotlib.pyplot as plt
import pandas as pd
from io import StringIO

# Set GUI backend for displaying charts
try:
    matplotlib.use('Qt5Agg')  # Try Qt5 first
except ImportError:
    try:
        matplotlib.use('TkAgg')  # Fallback to Tkinter
    except ImportError:
        try:
            matplotlib.use('GTK3Agg')  # Fallback to GTK
        except ImportError:
            pass  # Use default backend

# Everforest color palette
EVERFOREST_COLORS = {
    'bg0': '#2d353b',
    'bg1': '#343f44', 
    'bg2': '#3d484d',
    'bg3': '#475258',
    'bg4': '#4f585e',
    'bg5': '#56635f',
    'fg': '#d3c6aa',
    'red': '#e67e80',
    'orange': '#e69875',
    'yellow': '#dbbc7f',
    'green': '#a7c080',
    'aqua': '#83c092',
    'blue': '#7fbbb3',
    'purple': '#d699b6',
    'grey0': '#7a8478',
    'grey1': '#859289',
    'grey2': '#9da9a0'
}

def setup_everforest_theme():
    """Set up matplotlib with Everforest theme"""
    plt.style.use('dark_background')
    plt.rcParams.update({
        'figure.facecolor': EVERFOREST_COLORS['bg0'],
        'axes.facecolor': EVERFOREST_COLORS['bg1'],
        'axes.edgecolor': EVERFOREST_COLORS['grey1'],
        'axes.labelcolor': EVERFOREST_COLORS['fg'],
        'text.color': EVERFOREST_COLORS['fg'],
        'xtick.color': EVERFOREST_COLORS['fg'],
        'ytick.color': EVERFOREST_COLORS['fg'],
        'grid.color': EVERFOREST_COLORS['bg3'],
        'axes.spines.left': True,
        'axes.spines.bottom': True,
        'axes.spines.top': False,
        'axes.spines.right': False,
        'grid.alpha': 0.3,
        'font.size': 11,
        'axes.titlesize': 14,
        'axes.labelsize': 12,
        'xtick.labelsize': 10,
        'ytick.labelsize': 10,
        'legend.fontsize': 10
    })

def read_csv_data(file_input):
    """Read CSV data from file or stdin"""
    if file_input.name == '<stdin>':
        # Read from stdin
        content = file_input.read()
        if not content.strip():
            raise ValueError("No data provided via stdin")
        return StringIO(content)
    else:
        # Read from file
        return file_input

def parse_csv(data_source):
    """Parse CSV and return DataFrame"""
    try:
        # Try to read with pandas first (handles various CSV formats better)
        df = pd.read_csv(data_source)
        return df
    except Exception as e:
        # Fallback to manual CSV parsing
        data_source.seek(0)
        reader = csv.reader(data_source)
        rows = list(reader)
        if not rows:
            raise ValueError("CSV file is empty")
        
        # Assume first row is header if it contains non-numeric data
        try:
            float(rows[0][0])
            has_header = False
        except ValueError:
            has_header = True
        
        if has_header:
            headers = rows[0]
            data_rows = rows[1:]
        else:
            headers = [f"Column_{i+1}" for i in range(len(rows[0]))]
            data_rows = rows
        
        # Convert to DataFrame
        df = pd.DataFrame(data_rows, columns=headers)
        # Try to convert numeric columns
        for col in df.columns:
            try:
                df[col] = pd.to_numeric(df[col])
            except ValueError:
                pass  # Keep as string if not numeric
        
        return df

def create_histogram(df, title=None):
    """Create histogram for 2-column data (ID, Value)"""
    setup_everforest_theme()
    
    if len(df.columns) != 2:
        raise ValueError(f"Expected 2 columns for histogram, got {len(df.columns)}")
    
    id_col, value_col = df.columns
    
    # Ensure value column is numeric
    if not pd.api.types.is_numeric_dtype(df[value_col]):
        try:
            df[value_col] = pd.to_numeric(df[value_col])
        except ValueError:
            raise ValueError(f"Value column '{value_col}' must be numeric")
    
    fig, ax = plt.subplots(figsize=(10, 6))
    
    # Create histogram
    n, bins, patches = ax.hist(df[value_col], bins=20, alpha=0.8, 
                              color=EVERFOREST_COLORS['green'], 
                              edgecolor=EVERFOREST_COLORS['bg3'])
    
    # Customize appearance
    ax.set_xlabel(value_col, fontweight='bold')
    ax.set_ylabel('Frequency', fontweight='bold')
    ax.grid(True, alpha=0.3)
    
    if title:
        ax.set_title(title, fontweight='bold', pad=20)
    else:
        ax.set_title(f'Distribution of {value_col}', fontweight='bold', pad=20)
    
    # Add some statistics as text
    mean_val = df[value_col].mean()
    std_val = df[value_col].std()
    stats_text = f'Mean: {mean_val:.2f}\nStd: {std_val:.2f}\nCount: {len(df)}'
    ax.text(0.02, 0.98, stats_text, transform=ax.transAxes, 
            verticalalignment='top', bbox=dict(boxstyle='round', 
            facecolor=EVERFOREST_COLORS['bg2'], alpha=0.8),
            color=EVERFOREST_COLORS['fg'])
    
    plt.tight_layout()
    return fig

def create_hexbin_plot(df, title=None, gridsize=20):
    """Create hexagonal binning plot for 3-column data (ID, X, Y)"""
    setup_everforest_theme()
    
    if len(df.columns) != 3:
        raise ValueError(f"Expected 3 columns for hexbin plot, got {len(df.columns)}")
    
    id_col, x_col, y_col = df.columns
    
    # Ensure x and y columns are numeric
    for col in [x_col, y_col]:
        if not pd.api.types.is_numeric_dtype(df[col]):
            try:
                df[col] = pd.to_numeric(df[col])
            except ValueError:
                raise ValueError(f"Column '{col}' must be numeric for hexbin plot")
    
    fig, ax = plt.subplots(figsize=(10, 8))
    
    # Create hexbin plot with Everforest colors
    hb = ax.hexbin(df[x_col], df[y_col], 
                   gridsize=gridsize,
                   cmap='viridis',  # We'll customize this
                   alpha=0.8,
                   linewidths=0.2,
                   edgecolors=EVERFOREST_COLORS['bg3'])
    
    # Create custom colormap with Everforest colors
    from matplotlib.colors import LinearSegmentedColormap
    everforest_colors = [
        EVERFOREST_COLORS['bg1'],    # Low density
        EVERFOREST_COLORS['blue'],   # Medium-low
        EVERFOREST_COLORS['aqua'],   # Medium
        EVERFOREST_COLORS['green'],  # Medium-high
        EVERFOREST_COLORS['yellow'], # High density
    ]
    custom_cmap = LinearSegmentedColormap.from_list('everforest', everforest_colors)
    hb.set_cmap(custom_cmap)
    
    # Add colorbar
    cb = plt.colorbar(hb, ax=ax)
    cb.set_label('Point Density', fontweight='bold', color=EVERFOREST_COLORS['fg'])
    cb.ax.yaxis.set_tick_params(color=EVERFOREST_COLORS['fg'])
    plt.setp(plt.getp(cb.ax.axes, 'yticklabels'), color=EVERFOREST_COLORS['fg'])
    
    # Customize appearance
    ax.set_xlabel(x_col, fontweight='bold')
    ax.set_ylabel(y_col, fontweight='bold')
    ax.grid(True, alpha=0.3)
    
    if title:
        ax.set_title(title, fontweight='bold', pad=20)
    else:
        ax.set_title(f'{y_col} vs {x_col} (Density)', fontweight='bold', pad=20)
    
    # Add statistics
    try:
        correlation = df[x_col].corr(df[y_col])
        total_points = len(df)
        max_density = hb.get_array().max()
        stats_text = f'Correlation: {correlation:.3f}\nTotal Points: {total_points}\nMax Density: {int(max_density)}'
        ax.text(0.02, 0.98, stats_text, transform=ax.transAxes, 
                verticalalignment='top', bbox=dict(boxstyle='round', 
                facecolor=EVERFOREST_COLORS['bg2'], alpha=0.8),
                color=EVERFOREST_COLORS['fg'])
    except Exception:
        pass  # Skip if statistics can't be calculated
    
    plt.tight_layout()
    return fig

def create_scatter_plot(df, title=None):
    """Create scatter plot for 3-column data (ID, X, Y)"""
    setup_everforest_theme()
    
    if len(df.columns) != 3:
        raise ValueError(f"Expected 3 columns for scatter plot, got {len(df.columns)}")
    
    id_col, x_col, y_col = df.columns
    
    # Ensure x and y columns are numeric
    for col in [x_col, y_col]:
        if not pd.api.types.is_numeric_dtype(df[col]):
            try:
                df[col] = pd.to_numeric(df[col])
            except ValueError:
                raise ValueError(f"Column '{col}' must be numeric for scatter plot")
    
    fig, ax = plt.subplots(figsize=(10, 8))
    
    # Create scatter plot
    scatter = ax.scatter(df[x_col], df[y_col], 
                        c=EVERFOREST_COLORS['blue'], 
                        alpha=0.7, s=50,
                        edgecolors=EVERFOREST_COLORS['bg3'], 
                        linewidth=0.5)
    
    # Customize appearance
    ax.set_xlabel(x_col, fontweight='bold')
    ax.set_ylabel(y_col, fontweight='bold')
    ax.grid(True, alpha=0.3)
    
    if title:
        ax.set_title(title, fontweight='bold', pad=20)
    else:
        ax.set_title(f'{y_col} vs {x_col}', fontweight='bold', pad=20)
    
    # Add correlation coefficient if possible
    try:
        correlation = df[x_col].corr(df[y_col])
        corr_text = f'Correlation: {correlation:.3f}\nPoints: {len(df)}'
        ax.text(0.02, 0.98, corr_text, transform=ax.transAxes, 
                verticalalignment='top', bbox=dict(boxstyle='round', 
                facecolor=EVERFOREST_COLORS['bg2'], alpha=0.8),
                color=EVERFOREST_COLORS['fg'])
    except Exception:
        pass  # Skip if correlation can't be calculated
    
    plt.tight_layout()
    return fig

@click.command()
@click.argument('file', type=click.File('r'), default='-')
@click.option('--title', '-t', help='Optional title for the chart')
@click.option('--output', '-o', type=click.Path(), help='Output file path (default: display chart)')
@click.option('--chart-type', '-c', type=click.Choice(['auto', 'histogram', 'scatter', 'hexbin']), 
              default='auto', help='Force specific chart type (default: auto-detect)')
@click.option('--gridsize', default=20, help='Grid size for hexbin charts (default: 20)')
@click.option('--dpi', default=100, help='DPI for saved image (default: 100)')
@click.option('--viewer', is_flag=True, help='Save to temp file and open in image viewer instead of matplotlib window')
def main(file, title, output, chart_type, gridsize, dpi, viewer):
    """Create histogram or scatter plot from CSV data with Everforest theme.
    
    Automatically detects chart type based on columns:
    - 2 columns (ID, Value) → Histogram  
    - 3 columns (ID, X, Y) → Scatter plot
    
    Examples:
    
      cat data.csv | chart-tool --title "My Chart"
      
      chart-tool data.csv
      
      echo "id,value\\n1,10\\n2,20" | chart-tool
    """
    try:
        # Read and parse CSV data
        data_source = read_csv_data(file)
        df = parse_csv(data_source)
        
        print(f"Loaded {len(df)} rows with {len(df.columns)} columns", file=sys.stderr)
        print(f"Columns: {list(df.columns)}", file=sys.stderr)
        
        # Determine chart type
        if chart_type == 'auto':
            if len(df.columns) == 2:
                chart_type = 'histogram'
            elif len(df.columns) == 3:
                chart_type = 'scatter'
            else:
                raise click.ClickException(f"Auto-detection failed: {len(df.columns)} columns. "
                                         "Use --chart-type to specify histogram, scatter, or hexbin")
        
        # Validate chart type with data
        if chart_type == 'histogram' and len(df.columns) != 2:
            raise click.ClickException(f"Histogram requires 2 columns, got {len(df.columns)}")
        elif chart_type in ['scatter', 'hexbin'] and len(df.columns) != 3:
            raise click.ClickException(f"{chart_type.title()} requires 3 columns, got {len(df.columns)}")
        
        # Create the appropriate chart
        if chart_type == 'histogram':
            click.echo("Creating histogram", err=True)
            fig = create_histogram(df, title)
        elif chart_type == 'scatter':
            click.echo("Creating scatter plot", err=True)
            fig = create_scatter_plot(df, title)
        elif chart_type == 'hexbin':
            click.echo(f"Creating hexbin plot (gridsize={gridsize})", err=True)
            fig = create_hexbin_plot(df, title, gridsize)
        
        # Save or display the chart
        if output:
            fig.savefig(output, dpi=dpi, bbox_inches='tight',
                       facecolor=EVERFOREST_COLORS['bg0'])
            click.echo(f"Chart saved to {output}", err=True)
        elif viewer:
            # Save to temp file and open in image viewer
            import tempfile
            import subprocess
            with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as tmp:
                fig.savefig(tmp.name, dpi=dpi, bbox_inches='tight',
                           facecolor=EVERFOREST_COLORS['bg0'])
                click.echo(f"Opening chart in image viewer...", err=True)
                # Try common image viewers
                viewers = ['feh', 'eog', 'gwenview', 'ristretto', 'xdg-open']
                for viewer_cmd in viewers:
                    try:
                        subprocess.run([viewer_cmd, tmp.name], check=True)
                        break
                    except (subprocess.CalledProcessError, FileNotFoundError):
                        continue
                else:
                    click.echo(f"Could not find image viewer. Chart saved to {tmp.name}", err=True)
        else:
            # Ensure we have a display
            if hasattr(plt.get_current_fig_manager(), 'window'):
                # Set window properties for better integration
                mngr = plt.get_current_fig_manager()
                try:
                    mngr.window.wm_geometry("+100+100")  # Position window
                    mngr.set_window_title("CSV Chart Viewer")
                except AttributeError:
                    pass  # Backend doesn't support window management
            
            plt.show(block=True)  # Block until window is closed
    
    except KeyboardInterrupt:
        click.echo("\nOperation cancelled by user", err=True)
        raise click.Abort()
    except Exception as e:
        raise click.ClickException(str(e))

if __name__ == '__main__':
    main()
