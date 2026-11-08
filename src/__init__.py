"""
Insurance Claims Agent Demo - Core Package
"""

from src.policies import POLICY, get_policy
from src.workflow import process_claim

__all__ = ["POLICY", "get_policy", "process_claim"]
