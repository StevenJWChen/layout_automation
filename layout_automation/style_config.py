#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Style configuration for layout visualization

Provides customizable styles for layers, boundaries, and shapes.
"""

from typing import Dict, Optional, Tuple


class LayerStyle:
    """Style configuration for a specific layer"""

    def __init__(self,
                 color: str = 'gray',
                 alpha: float = 0.6,
                 edge_color: str = 'black',
                 edge_width: float = 2.0,
                 shape: str = 'rectangle'):
        """
        Initialize layer style

        Args:
            color: Fill color for the layer
            alpha: Transparency (0.0 to 1.0)
            edge_color: Boundary/edge color
            edge_width: Boundary line width
            shape: Shape type ('rectangle', 'rounded', 'circle', 'octagon')
        """
        self.color = color
        self.alpha = alpha
        self.edge_color = edge_color
        self.edge_width = edge_width
        self.shape = shape


class ContainerStyle:
    """Style configuration for container cells"""

    def __init__(self,
                 edge_color: str = 'darkblue',
                 edge_width: float = 2.0,
                 linestyle: str = '--',
                 alpha: float = 0.8,
                 shape: str = 'rectangle'):
        """
        Initialize container style

        Args:
            edge_color: Boundary color
            edge_width: Boundary line width
            linestyle: Line style ('-', '--', '-.', ':')
            alpha: Transparency (0.0 to 1.0)
            shape: Shape type ('rectangle', 'rounded')
        """
        self.edge_color = edge_color
        self.edge_width = edge_width
        self.linestyle = linestyle
        self.alpha = alpha
        self.shape = shape


class StyleConfig:
    """Global style configuration for layout visualization"""

    # Default layer styles
    DEFAULT_LAYER_STYLES = {
        'metal1': LayerStyle(color='blue', alpha=0.6, edge_color='darkblue', edge_width=2.0),
        'metal2': LayerStyle(color='red', alpha=0.6, edge_color='darkred', edge_width=2.0),
        'metal3': LayerStyle(color='green', alpha=0.6, edge_color='darkgreen', edge_width=2.0),
        'metal4': LayerStyle(color='orange', alpha=0.6, edge_color='darkorange', edge_width=2.0),
        'metal5': LayerStyle(color='cyan', alpha=0.6, edge_color='darkcyan', edge_width=2.0),
        'metal6': LayerStyle(color='magenta', alpha=0.6, edge_color='darkmagenta', edge_width=2.0),
        'poly': LayerStyle(color='purple', alpha=0.6, edge_color='indigo', edge_width=2.0),
        'diff': LayerStyle(color='brown', alpha=0.6, edge_color='saddlebrown', edge_width=2.0),
        'nwell': LayerStyle(color='lightgreen', alpha=0.3, edge_color='green', edge_width=1.5),
        'pwell': LayerStyle(color='lightcoral', alpha=0.3, edge_color='red', edge_width=1.5),
        'contact': LayerStyle(color='gray', alpha=0.8, edge_color='black', edge_width=1.0),
        'via': LayerStyle(color='silver', alpha=0.8, edge_color='black', edge_width=1.0),
    }

    # Default container style
    DEFAULT_CONTAINER_STYLE = ContainerStyle(
        edge_color='darkblue',
        edge_width=2.0,
        linestyle='--',
        alpha=0.8
    )

    def __init__(self):
        """Initialize style configuration"""
        # Use default styles as starting point
        self.layer_styles: Dict[str, LayerStyle] = self.DEFAULT_LAYER_STYLES.copy()
        self.container_style = ContainerStyle(
            edge_color=self.DEFAULT_CONTAINER_STYLE.edge_color,
            edge_width=self.DEFAULT_CONTAINER_STYLE.edge_width,
            linestyle=self.DEFAULT_CONTAINER_STYLE.linestyle,
            alpha=self.DEFAULT_CONTAINER_STYLE.alpha
        )

        # Container color cycling for different hierarchy levels
        self.container_colors = ['darkblue', 'darkred', 'darkgreen', 'darkorange', 'darkviolet', 'darkcyan']

    def set_layer_style(self, layer_name: str,
                       color: Optional[str] = None,
                       alpha: Optional[float] = None,
                       edge_color: Optional[str] = None,
                       edge_width: Optional[float] = None,
                       shape: Optional[str] = None):
        """
        Set style for a specific layer

        Args:
            layer_name: Name of the layer
            color: Fill color
            alpha: Transparency (0.0 to 1.0)
            edge_color: Boundary color
            edge_width: Boundary line width
            shape: Shape type ('rectangle', 'rounded', 'circle', 'octagon')
        """
        # Get existing style or create new one
        if layer_name in self.layer_styles:
            style = self.layer_styles[layer_name]
        else:
            style = LayerStyle()

        # Update only provided parameters
        if color is not None:
            style.color = color
        if alpha is not None:
            style.alpha = alpha
        if edge_color is not None:
            style.edge_color = edge_color
        if edge_width is not None:
            style.edge_width = edge_width
        if shape is not None:
            style.shape = shape

        self.layer_styles[layer_name] = style

    def set_container_style(self,
                           edge_color: Optional[str] = None,
                           edge_width: Optional[float] = None,
                           linestyle: Optional[str] = None,
                           alpha: Optional[float] = None,
                           shape: Optional[str] = None):
        """
        Set style for container cells

        Args:
            edge_color: Boundary color
            edge_width: Boundary line width
            linestyle: Line style ('-', '--', '-.', ':')
            alpha: Transparency (0.0 to 1.0)
            shape: Shape type ('rectangle', 'rounded')
        """
        if edge_color is not None:
            self.container_style.edge_color = edge_color
        if edge_width is not None:
            self.container_style.edge_width = edge_width
        if linestyle is not None:
            self.container_style.linestyle = linestyle
        if alpha is not None:
            self.container_style.alpha = alpha
        if shape is not None:
            self.container_style.shape = shape

    def get_layer_style(self, layer_name: str) -> LayerStyle:
        """Get style for a specific layer"""
        return self.layer_styles.get(layer_name, LayerStyle())

    def get_container_color(self, level: int) -> str:
        """Get container edge color for a specific hierarchy level"""
        return self.container_colors[level % len(self.container_colors)]

    def set_container_colors(self, colors: list):
        """Set the color cycle for container cells at different levels"""
        self.container_colors = colors


# Global style configuration instance
_global_style_config = StyleConfig()


def get_style_config() -> StyleConfig:
    """Get the global style configuration"""
    return _global_style_config


def reset_style_config():
    """Reset style configuration to defaults"""
    global _global_style_config
    _global_style_config = StyleConfig()
    # Make fresh copies of defaults
    _global_style_config.layer_styles = {}
    for layer, style in StyleConfig.DEFAULT_LAYER_STYLES.items():
        _global_style_config.layer_styles[layer] = LayerStyle(
            color=style.color,
            alpha=style.alpha,
            edge_color=style.edge_color,
            edge_width=style.edge_width,
            shape=style.shape
        )
