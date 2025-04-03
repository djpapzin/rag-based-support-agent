import requests
from typing import List, Dict, Any, Optional
import sys
import os

# Add the parent directory to sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.config import config

class ZendeskClient:
    def __init__(self):
        self.base_url = config.ZENDESK_API_URL
        self.headers = {
            "Authorization": config.ZENDESK_API_KEY,
            "Content-Type": "application/json"
        }
        self._support_user_ids = None

    def get_support_user_ids(self) -> List[int]:
        """Get all support user IDs from Zendesk."""
        if self._support_user_ids is not None:
            return self._support_user_ids

        try:
            # Use the search endpoint with proper query format
            response = requests.get(
                f"{self.base_url}/api/v2/search",
                params={"query": "role:agent"},
                headers=self.headers
            )
            response.raise_for_status()
            results = response.json().get("results", [])
            
            # Extract user IDs from search results
            support_ids = [
                result["id"] for result in results 
                if result.get("role") == "agent" or 
                   result.get("tags") and "support" in result.get("tags", [])
            ]
            
            if not support_ids:
                print("Warning: No support user IDs found. Using default ID.")
                support_ids = [config.SUPPORT_USER_ID]
            
            self._support_user_ids = support_ids
            return support_ids
            
        except Exception as e:
            print(f"Error fetching support user IDs: {str(e)}")
            print("Using default support user ID.")
            return [config.SUPPORT_USER_ID]

    def get_resolved_tickets(self) -> List[Dict[str, Any]]:
        """Get all resolved tickets from Zendesk."""
        response = requests.get(
            f"{self.base_url}/api/v2/search",
            params={"query": "status:solved"},
            headers=self.headers
        )
        response.raise_for_status()
        return response.json().get("results", [])

    def get_open_tickets(self) -> List[Dict[str, Any]]:
        """Get all open tickets from Zendesk."""
        response = requests.get(
            f"{self.base_url}/api/v2/search",
            params={"query": "status:open"},
            headers=self.headers
        )
        response.raise_for_status()
        return response.json().get("results", [])

    def get_ticket_comments(self, ticket_id: int) -> List[Dict[str, Any]]:
        """Get all comments for a specific ticket."""
        response = requests.get(
            f"{self.base_url}/api/v2/tickets/{ticket_id}/comments",
            headers=self.headers
        )
        response.raise_for_status()
        return response.json().get("comments", [])

    def add_comment(self, ticket_id: int, comment: str, public: bool = False) -> Dict[str, Any]:
        """Add a comment to a ticket."""
        # Get the first available support user ID
        support_id = self.get_support_user_ids()[0]
        
        data = {
            "tickets": [{
                "id": ticket_id,
                "comment": {
                    "body": comment,
                    "public": public,
                    "author_id": support_id
                }
            }]
        }
        response = requests.post(
            f"{self.base_url}/api/v2/tickets/update_many",
            headers=self.headers,
            json=data
        )
        response.raise_for_status()
        return response.json() 