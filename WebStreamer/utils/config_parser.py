from os import environ
from typing import Dict, Optional
import re

class TokenParser:
    def __init__(self, config_file: Optional[str] = None):
        self.tokens = {}
        self.config_file = config_file

    def parse_from_env(self) -> Dict[int, str]:
        """
        Parse MULTI_TOKEN environment variables and return a dict mapping bot indices to tokens.
        Uses numerical sorting to ensure MULTI_TOKEN1-10 are assigned correctly.
        
        Returns:
            Dict with bot index (1-based) as key and token string as value
        """
        # Filter MULTI_TOKEN variables
        multi_token_vars = [
            (key, value) for key, value in environ.items() 
            if key.startswith("MULTI_TOKEN")
        ]
        
        # Sort by the numeric part of the variable name (not alphabetically)
        def extract_token_number(item):
            key, _ = item
            match = re.search(r'MULTI_TOKEN(\d+)', key)
            return int(match.group(1)) if match else 0
        
        sorted_tokens = sorted(multi_token_vars, key=extract_token_number)
        
        # Create dict with 1-based indexing
        self.tokens = dict(
            (c + 1, token)
            for c, (_, token) in enumerate(sorted_tokens)
        )
        return self.tokens

    def get_github_token(self) -> str:
        return environ.get("GITHUB_TOKEN")

    def get_github_username(self) -> str:
        return environ.get("GITHUB_USERNAME")

    def get_github_repo(self) -> str:
        return environ.get("GITHUB_REPO")
