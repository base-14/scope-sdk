"""Resource classes for scope-client.

This module exports the main resource classes used to represent
API responses as objects.
"""

from scope_client.resources.base import Resource
from scope_client.resources.prompt import Prompt
from scope_client.resources.prompt_version import PromptVersion

__all__ = ["Resource", "Prompt", "PromptVersion"]
