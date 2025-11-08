"""
Gemini-based role assigner service
Analyzes user introductions and assigns appropriate roles
"""

import google.generativeai as genai
import json
import os
from typing import List, Dict
from dotenv import load_dotenv

load_dotenv()


class RoleAssigner:
    """Service for analyzing intros and assigning roles using Gemini"""

    def __init__(self, roles_config_path: str = "config/roles.json"):
        """
        Initialize the role assigner with Gemini API

        Args:
            roles_config_path: Path to the roles configuration JSON file
        """
        # Configure Gemini API
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise ValueError("GEMINI_API_KEY not found in environment variables")

        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel('gemini-2.5-flash')

        # Load role mappings
        self.roles_config_path = roles_config_path
        self.role_mappings = self.ls_load_role_mappings()

    def ls_load_role_mappings(self) -> Dict[str, int]:
        """Load role name to role ID mappings from JSON file"""
        try:
            with open(self.roles_config_path, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            print(f"Warning: Role config file not found at {self.roles_config_path}")
            return {}
        except json.JSONDecodeError:
            print(f"Warning: Invalid JSON in role config file {self.roles_config_path}")
            return {}

    def reload_role_mappings(self):
        """Reload role mappings from the configuration file"""
        self.role_mappings = self.ls_load_role_mappings()

    async def analyze_intro(self, intro_text: str) -> List[str]:
        """
        Analyze an introduction and suggest appropriate roles

        Args:
            intro_text: The user's introduction message

        Returns:
            List of role names that should be assigned
        """
        if not intro_text or not intro_text.strip():
            return []

        # Get available roles
        available_roles = list(self.role_mappings.keys())
        if not available_roles:
            print("Warning: No roles configured")
            return []

        # Create prompt for Gemini
        prompt = f"""
You are a helpful assistant that analyzes user introductions on a Discord server and suggests appropriate roles.

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

        try:
            # Generate response from Gemini
            response = self.model.generate_content(prompt)

            if not response or not response.text:
                print("Warning: Empty response from Gemini")
                return []

            # Parse the response
            response_text = response.text.strip()

            # Try to extract JSON array from response
            # Handle cases where the model might include extra text
            start_idx = response_text.find('[')
            end_idx = response_text.rfind(']')

            if start_idx == -1 or end_idx == -1:
                print(f"Warning: No JSON array found in response: {response_text}")
                return []

            json_str = response_text[start_idx:end_idx + 1]
            suggested_roles = json.loads(json_str)

            # Validate and filter roles
            valid_roles = []
            for role in suggested_roles:
                role_lower = role.lower().strip()
                if role_lower in available_roles:
                    valid_roles.append(role_lower)
                else:
                    print(f"Warning: Suggested role '{role}' not found in available roles")

            return valid_roles

        except json.JSONDecodeError as e:
            print(f"Error parsing Gemini response as JSON: {e}")
            print(f"Response was: {response_text if 'response_text' in locals() else 'N/A'}")
            return []
        except Exception as e:
            print(f"Error analyzing intro with Gemini: {e}")
            return []

    def get_role_ids(self, role_names: List[str]) -> List[int]:
        """
        Convert role names to role IDs

        Args:
            role_names: List of role names

        Returns:
            List of role IDs
        """
        role_ids = []
        for role_name in role_names:
            role_id = self.role_mappings.get(role_name.lower())
            if role_id:
                role_ids.append(role_id)
            else:
                print(f"Warning: No role ID found for role name '{role_name}'")
        return role_ids

    async def assign_roles_from_intro(self, intro_text: str) -> tuple[List[str], List[int]]:
        """
        Analyze intro and return both role names and IDs

        Args:
            intro_text: The user's introduction message

        Returns:
            Tuple of (role_names, role_ids)
        """
        role_names = await self.analyze_intro(intro_text)
        role_ids = self.get_role_ids(role_names)
        return role_names, role_ids
