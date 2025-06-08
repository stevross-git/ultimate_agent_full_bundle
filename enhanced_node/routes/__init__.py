"""
Routes module for Enhanced Node Server
"""

from .api_v3 import register_api_v3_routes
from .api_v5_remote import register_api_v5_routes

__all__ = [
    'register_api_v3_routes',
    'register_api_v5_routes'
]
