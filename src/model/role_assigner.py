"""Gemini-powered role suggestion service."""

from __future__ import annotations

import json
import os
from typing import Dict, List, Tuple

import google.generativeai as genai
from dotenv import load_dotenv

from logger import get_logger

load_dotenv()
log = get_logger(__name__)

_MODEL_NAME = "gemini-2.5-flash"


class RoleAssigner:
    """Analyze user introductions and map them to configured Discord role IDs."""

    def __init__(self, roles_config_path: str = "config/roles.json") -> None:
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise ValueError("GEMINI_API_KEY not found in environment variables")

        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel(_MODEL_NAME)

        self.roles_config_path = roles_config_path
        self.role_mappings: Dict[str, int] = self._load_role_mappings()

    # ------------------------------------------------------------ mappings IO

    def _load_role_mappings(self) -> Dict[str, int]:
        try:
            with open(self.roles_config_path, "r", encoding="utf-8") as f:
                return json.load(f)
        except FileNotFoundError:
            log.warning("Role config file not found at %s", self.roles_config_path)
            return {}
        except json.JSONDecodeError as e:
            log.warning("Invalid JSON in role config file %s: %s", self.roles_config_path, e)
            return {}

    def reload_role_mappings(self) -> None:
        self.role_mappings = self._load_role_mappings()

    # ----------------------------------------------------------- Gemini prompt

    def _build_prompt(self, intro_text: str, available_roles: List[str]) -> str:
        return f"""You are a helpful assistant that analyzes user introductions on a Discord server and suggests appropriate roles.

Available roles:
{', '.join(available_roles)}

User introduction:
"{intro_text}"

Based on the user's introduction, determine which roles are most appropriate for them. Consider:
- Their interests and hobbies
- Their profession or skills
- What they mention wanting to do or learn
- Their background and experience

Return ONLY a JSON array of role names that should be assigned. Use lowercase for role names.
Return an empty array if no roles match.

Example format: ["developer", "gamer", "tech enthusiast"]

Your response:"""

    async def analyze_intro(self, intro_text: str) -> List[str]:
        """Ask Gemini which configured roles fit the intro. Returns validated role names."""
        if not intro_text or not intro_text.strip():
            return []

        available_roles = list(self.role_mappings.keys())
        if not available_roles:
            log.warning("No roles configured")
            return []

        prompt = self._build_prompt(intro_text, available_roles)

        try:
            response = self.model.generate_content(prompt)
        except Exception as e:
            log.error("Gemini request failed: %s", e)
            return []

        if not response or not response.text:
            log.warning("Empty response from Gemini")
            return []

        response_text = response.text.strip()
        start = response_text.find("[")
        end = response_text.rfind("]")
        if start == -1 or end == -1:
            log.warning("No JSON array found in response: %s", response_text)
            return []

        try:
            suggested = json.loads(response_text[start:end + 1])
        except json.JSONDecodeError as e:
            log.error("Error parsing Gemini response as JSON: %s | response=%s", e, response_text)
            return []

        valid: List[str] = []
        for role in suggested:
            lowered = str(role).lower().strip()
            if lowered in available_roles:
                valid.append(lowered)
            else:
                log.warning("Suggested role '%s' not in available roles", role)
        return valid

    # ---------------------------------------------------------- public helpers

    def get_role_ids(self, role_names: List[str]) -> List[int]:
        ids: List[int] = []
        for name in role_names:
            role_id = self.role_mappings.get(name.lower())
            if role_id:
                ids.append(role_id)
            else:
                log.warning("No role ID found for role name '%s'", name)
        return ids

    async def assign_roles_from_intro(self, intro_text: str) -> Tuple[List[str], List[int]]:
        role_names = await self.analyze_intro(intro_text)
        return role_names, self.get_role_ids(role_names)
