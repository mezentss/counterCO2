"""
Visualizer module for creating CO2 emission charts and graphs.
"""

import matplotlib.pyplot as plt
import matplotlib
import io
import numpy as np
from typing import Dict, List, Tuple

# Use non-interactive backend
matplotlib.use('Agg')

# Set style for better looking plots
plt.style.use('default')


def create_transport_comparison(data: Dict) -> bytes:
    """
    Create a bar chart comparing CO2 emissions by transport type.
    
    Args:
        data: Dictionary with transport and emissions data
        Example:
        {
            'transport': ['plane', 'train', 'car', 'bus'],
            'emissions': [95.5, 32.5, 104.0, 45.5]
        }
    
    Returns:
        bytes: Image data for sending to Telegram
    """
    fig, ax = plt.subplots(figsize=(10, 6))
    
    transport_types = data['transport']
    emissions = data['emissions']
    
    # Color mapping based on emission levels (green = low, red = high)
    colors = []
    for emission in emissions:
        if emission <= 30:
            colors.append('#2ecc71')  # Green
        elif emission <= 60:
            colors.append('#f39c12')  # Orange
        elif emission <= 90:
            colors.append('#e67e22')  # Dark orange
        else:
            colors.append('#e74c3c')  # Red
    
    # Create bar chart
    bars = ax.bar(transport_types, emissions, color=colors, alpha=0.8, edgecolor='black', linewidth=1)
    
    # Customize the chart
    ax.set_xlabel('Тип транспорта', fontsize=12, fontweight='bold')
    ax.set_ylabel('Выбросы CO2 (кг)', fontsize=12, fontweight='bold')
    ax.set_title('Сравнение выбросов CO2 по видам транспорта', fontsize=14, fontweight='bold', pad=20)
    
    # Add value labels on bars
    for bar, emission in zip(bars, emissions):
        height = bar.get_height()
        ax.text(bar.get_x() + bar.get_width()/2., height + max(emissions)*0.01,
                f'{emission:.1f}', ha='center', va='bottom', fontweight='bold')
    
    # Auto-scale y-axis
    ax.set_ylim(0, max(emissions) * 1.2)
    
    # Grid for better readability
    ax.grid(axis='y', alpha=0.3)
    
    plt.tight_layout()
    
    # Save to bytes
    buf = io.BytesIO()
    plt.savefig(buf, format='png', dpi=150, bbox_inches='tight')
    buf.seek(0)
    
    plt.close()
    return buf.getvalue()


def create_comparison_pie_chart(route1_data: Dict, route2_data: Dict) -> bytes:
    """
    Create a pie chart comparing two routes.
    
    Args:
        route1_data: Dictionary for first route
        route2_data: Dictionary for second route
    
    Returns:
        bytes: Image data for sending to Telegram
    """
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 7))
    
    def create_pie(ax, data, title):
        transport_types = data['transport']
        emissions = data['emissions']
        
        # Color mapping
        colors = []
        for emission in emissions:
            if emission <= 30:
                colors.append('#2ecc71')
            elif emission <= 60:
                colors.append('#f39c12')
            elif emission <= 90:
                colors.append('#e67e22')
            else:
                colors.append('#e74c3c')
        
        # Create pie chart
        wedges, texts, autotexts = ax.pie(emissions, labels=transport_types, colors=colors,
                                          autopct='%1.1f%%', startangle=90, textprops={'fontweight': 'bold'})
        
        ax.set_title(title, fontsize=12, fontweight='bold')
        
        # Equal aspect ratio ensures that pie is drawn as a circle
        ax.axis('equal')
    
    # Create both pie charts
    create_pie(ax1, route1_data, 'Маршрут 1')
    create_pie(ax2, route2_data, 'Маршрут 2')
    
    plt.suptitle('Сравнение выбросов CO2 для двух маршрутов', fontsize=14, fontweight='bold')
    plt.tight_layout()
    
    # Save to bytes
    buf = io.BytesIO()
    plt.savefig(buf, format='png', dpi=150, bbox_inches='tight')
    buf.seek(0)
    
    plt.close()
    return buf.getvalue()


def create_best_route_visualization(best_transport: str, all_data: Dict) -> bytes:
    """
    Create a visualization highlighting the best transport option.
    
    Args:
        best_transport: The transport type with lowest emissions
        all_data: Dictionary with all transport data
    
    Returns:
        bytes: Image data for sending to Telegram
    """
    fig, ax = plt.subplots(figsize=(10, 6))
    
    transport_types = all_data['transport']
    emissions = all_data['emissions']
    
    # Color mapping - highlight the best option
    colors = []
    for i, transport in enumerate(transport_types):
        if transport == best_transport:
            colors.append('#27ae60')  # Bright green for best
        else:
            colors.append('#95a5a6')  # Gray for others
    
    # Create horizontal bar chart
    bars = ax.barh(transport_types, emissions, color=colors, alpha=0.8, edgecolor='black', linewidth=1)
    
    # Customize the chart
    ax.set_xlabel('Выбросы CO2 (кг)', fontsize=12, fontweight='bold')
    ax.set_title('Самый экологичный вид транспорта', fontsize=14, fontweight='bold', pad=20)
    
    # Add value labels
    for bar, emission in zip(bars, emissions):
        width = bar.get_width()
        ax.text(width + max(emissions)*0.01, bar.get_y() + bar.get_height()/2.,
                f'{emission:.1f}', ha='left', va='center', fontweight='bold')
    
    # Auto-scale x-axis
    ax.set_xlim(0, max(emissions) * 1.3)
    
    # Grid
    ax.grid(axis='x', alpha=0.3)
    
    plt.tight_layout()
    
    # Save to bytes
    buf = io.BytesIO()
    plt.savefig(buf, format='png', dpi=150, bbox_inches='tight')
    buf.seek(0)
    
    plt.close()
    return buf.getvalue()
