""" This module provides a function to create a radial calendar plot using matplotlib and pandas.
    The plot is inspired by https://www.adamheisserer.com/#/energy-monitoring-calendars/"""

from typing import Optional, Tuple, Union
import calendar
from datetime import datetime, timedelta
import matplotlib.pyplot as plt
from matplotlib.colors import Normalize, LinearSegmentedColormap
import numpy as np
import pandas as pd
from matplotlib.colors import PowerNorm

def plot_radial_calendar(
    data: pd.DataFrame,
    size_column: str,
    colour_column: str,
    inner_radius: float = 5,
    outer_radius: float = 10,
    min_size: float = 0.1,
    max_size: float = 15,
    bg_color: str = "black",
    line_color: str = "white",
    month_label_color: str = "white",
    title: Optional[str] = None,
    subtitle: Optional[str] = None,
    show_legend: bool = False,
    fig_size: Tuple[float, float] = (12, 12),
    cmap: Optional[Union[str, LinearSegmentedColormap, list]] = None,
    year: int = 2025,
    ax: Optional[plt.Axes] = None,
    attribution_text: Optional[str] = None,
    attribution_color: str = "white",
    dpi: int = 100,
    glow: bool = False,
    mask_months: Optional[list] = None,
) -> Tuple[plt.Figure, plt.Axes]:
    """
    Create a radial calendar plot with January positioned at ~1 o'clock,
    going clockwise around the circle, with tangential month labels.
    
    Parameters:
        data (pd.DataFrame): Hourly data for one year.
        size_column (str): Name of the column to be used for marker sizes.
        colour_column (str): Name of the column to be used for marker colors.
        inner_radius (float): Inner radius of the plot.
        outer_radius (float): Outer radius of the plot.
        min_size (float): Minimum marker size.
        max_size (float): Maximum marker size.
        bg_color (str): Background color of the plot.
        line_color (str): Color for month divider lines.
        month_label_color (str): Color for month labels.
        title (Optional[str]): Title of the plot.
        subtitle (Optional[str]): Subtitle of the plot.
        show_legend (bool): Whether to display a color legend.
        fig_size (Tuple[float, float]): Size of the figure (width, height).
        cmap (Optional[Union[str, LinearSegmentedColormap, list]]): Colormap for the scatter plot.
        year (int): Year for which the data is provided. Adjusts for leap years.
        ax (Optional[plt.Axes]): Matplotlib Axes object to plot on. If None, one is created.
    
    Returns:
        Tuple[plt.Figure, plt.Axes]: The figure and axes objects containing the plot.
    
    Raises:
        ValueError: If any of the input parameters are invalid.
    """
    # --- Validation ---
    if not isinstance(data, pd.DataFrame):
        raise ValueError("data must be a pandas DataFrame.")
    
    for col_name in [size_column, colour_column]:
        if col_name not in data.columns:
            raise ValueError(f"Column '{col_name}' not found in data.")
        if not pd.api.types.is_numeric_dtype(data[col_name]):
            raise ValueError(f"Column '{col_name}' must be numeric.")
    
    if not (isinstance(inner_radius, (int, float)) and inner_radius > 0):
        raise ValueError("inner_radius must be a positive number.")
    
    if not (isinstance(outer_radius, (int, float)) and outer_radius > inner_radius):
        raise ValueError("outer_radius must be greater than inner_radius.")
    
    if not (isinstance(min_size, (int, float)) and min_size > 0):
        raise ValueError("min_size must be a positive number.")
    
    if not (isinstance(max_size, (int, float)) and max_size > min_size):
        raise ValueError("max_size must be greater than min_size.")
    
    if not (isinstance(fig_size, tuple) and len(fig_size) == 2 and all(isinstance(i, (int, float)) and i > 0 for i in fig_size)):
        raise ValueError("fig_size must be a tuple of two positive numbers (width, height).")
    
    for color_arg, color_name in zip([bg_color, line_color, month_label_color, attribution_color],
                                     ["bg_color", "line_color", "month_label_color", "attribution_color"]):
        if not isinstance(color_arg, str):
            raise ValueError(f"{color_name} must be a string representing a valid color.")
    
    for text_arg, text_name in zip([title, subtitle, attribution_text], ["title", "subtitle", "attribution_text"]):
        if text_arg is not None and not isinstance(text_arg, str):
            raise ValueError(f"{text_name} must be a string or None.")
    
    if not isinstance(show_legend, bool):
        raise ValueError("show_legend must be a boolean.")
    
    if not (isinstance(dpi, int) and dpi > 0):
        raise ValueError("dpi must be a positive integer.")
    
    # Max dpi 600
    if dpi > 600:
        raise ValueError("dpi must be less than or equal to 600.")
    
    if not isinstance(glow, bool):
        raise ValueError("glow must be a boolean.")
    
    if mask_months is not None:
        if not isinstance(mask_months, list) or not all(isinstance(m, int) and 1 <= m <= 12 for m in mask_months):
            raise ValueError("mask_months must be a list of integers between 1 and 12.")
    
    
    # Determine expected number of hours based on the year (leap year or not)
    expected_hours = 8784 if calendar.isleap(year) else 8760
    if len(data) != expected_hours:
        raise ValueError(f"Data must have {expected_hours} rows for the year {year}.")
    
    # Validate or create colormap
    if cmap is None:
        cmap = LinearSegmentedColormap.from_list(
            "custom_cmap",
            ["#2962FF", "#2E7BFF", "#42A5F5", "#FFD600", "#FFC107", "#FF9800", "#FF5722", "#F44336"]
        )
    else:
        if isinstance(cmap, str):
            try:
                cmap = plt.get_cmap(cmap)
            except ValueError:
                raise ValueError(f"Invalid colormap name: {cmap}")
        elif isinstance(cmap, list):
            cmap = LinearSegmentedColormap.from_list("custom_cmap", cmap)
        elif not isinstance(cmap, LinearSegmentedColormap):
            raise ValueError("cmap must be a string, LinearSegmentedColormap, or a list of colors.")
    



    # --- Setup Figure and Axes ---
    if ax is None:
        fig, ax = plt.subplots(figsize=fig_size, facecolor=bg_color, dpi = dpi)
        ax.set_facecolor(bg_color)
    else:
        fig = ax.get_figure()
    ax.set_axis_off()
    
    # --- Data Preparation ---
    hours_in_day = 24
    days_in_year = expected_hours // hours_in_day

    # Compute hour and day indices
    num_hours = len(data)
    hours = np.arange(num_hours) % hours_in_day
    days = np.arange(num_hours) // hours_in_day

    # Compute angles:
    # 1. Negative multiplier for clockwise progression.
    # 2. Offset so that January starts at ~1 o'clock.
    angles = (-days * 2 * np.pi / days_in_year) + (np.pi / 2)

    # Compute radii by linearly interpolating between outer and inner radii over the day
    radii = outer_radius*1.2 - (hours / (hours_in_day - 1)) * (outer_radius*1.2 - inner_radius*1.2)

    # Convert polar coordinates to Cartesian coordinates
    x_coords = radii * np.cos(angles)
    y_coords = radii * np.sin(angles)

    # Normalize marker sizes and color values
    size_norm = Normalize(data[size_column].min(), data[size_column].max())
    sizes = min_size + size_norm(data[size_column].values) * (max_size - min_size)
    color_norm = Normalize(data[colour_column].min(), data[colour_column].max())

    # --- Month Divider and Labels ---
    # Calculate month starting days using the provided year
    month_starts = [0]  # January starts at day 0
    for month in range(1, 12):
        days_in_month = calendar.monthrange(year, month)[1]
        month_starts.append(month_starts[-1] + days_in_month)
    month_names = ["JAN", "FEB", "MAR", "APR", "MAY", "JUN",
                   "JUL", "AUG", "SEP", "OCT", "NOV", "DEC"]

    # Draw month divider lines
    for month_start in month_starts:
        angle = (-month_start * 2 * np.pi / days_in_year) + (np.pi / 2)
        x_line = [(inner_radius * 2) * np.cos(angle), (outer_radius * 1) * np.cos(angle)]
        y_line = [(inner_radius * 2) * np.sin(angle), (outer_radius * 1) * np.sin(angle)]
        ax.plot(x_line, y_line, color=line_color, linewidth=0.5, alpha=0.5)

    # Mask out the months that are in the mask_months list
    if mask_months is not None:
        combined_mask = np.zeros_like(days, dtype=bool)
        for month in mask_months:
            month_start = month_starts[month - 1]
            days_in_month = calendar.monthrange(year, month)[1]
            combined_mask |= (days >= month_start) & (days < month_start + days_in_month)
        data.loc[combined_mask, size_column] = np.nan
        data.loc[combined_mask, colour_column] = np.nan
        x_coords[combined_mask] = np.nan 
        y_coords[combined_mask] = np.nan
        sizes[combined_mask] = np.nan


    # Use PowerNorm to brighten the colors (gamma < 1 brightens the colormap)
    color_norm = PowerNorm(gamma=0.5, vmin=data[colour_column].min(), vmax=data[colour_column].max())

    if glow:
        # Create a neon glow effect by overlaying multiple scatter plots with increasing sizes and lower alpha
        for factor, alpha in zip([1.5, 2.0, 2.5, 3.0], [0.3, 0.2, 0.1, 0.05]):
            ax.scatter(
                x_coords, y_coords,
                s=sizes * factor*2,
                c=data[colour_column].values,
                cmap=cmap,
                norm=color_norm,  # use the gamma-corrected norm here
                alpha=alpha/2,
                edgecolors='none'
            )
    # Plot data points using a scatter plot
    scatter = ax.scatter(
        x_coords, y_coords,
        s=sizes,
        c=data[colour_column].values,
        cmap=cmap,
        norm=color_norm,
        alpha=0.75,
        edgecolors='none'
    )




    # Add month labels with tangential orientation
    for i, month in enumerate(month_names):
        if i < 11:
            middle_day = (month_starts[i] + month_starts[i+1]) / 2
        else:
            middle_day = (month_starts[i] + days_in_year) / 2
        
        angle = (-middle_day * 2 * np.pi / days_in_year) + (np.pi / 2)
        label_radius = outer_radius * 1.1
        x_label = label_radius * np.cos(angle)
        y_label = label_radius * np.sin(angle)
        rotation = (np.degrees(angle) - 90) % 360

        ax.text(x_label, y_label, month,
                ha='center', va='center',
                color=month_label_color, fontsize=10,
                rotation=rotation)

    # Set circular axis limits
    limit = outer_radius * 1.2
    ax.set_xlim(-limit, limit)
    ax.set_ylim(-limit, limit)
    ax.set_aspect('equal')

    # Add title and subtitle if provided
    if title:
        plt.suptitle(title, fontsize=18, color='white', y=0.95)
    if subtitle:
        plt.figtext(0.5, 0.90, subtitle, fontsize=12, color='#CCCCCC', ha='center')
    if attribution_text:
        plt.figtext(0.5, 0.0, attribution_text, fontsize=10, color=attribution_color, ha='center')

    # Optionally add a horizontal colorbar legend
    if show_legend:
        cax = fig.add_axes([0.15, 0.08, 0.7, 0.02])
        cbar = plt.colorbar(scatter, cax=cax, orientation='horizontal')
        cbar.set_label(f"{colour_column}", color='white')
        cbar.ax.xaxis.set_tick_params(color='white')
        plt.setp(plt.getp(cbar.ax.axes, 'xticklabels'), color='white')

    plt.show()
    return fig, ax
