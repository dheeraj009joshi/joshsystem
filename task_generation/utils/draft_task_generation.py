import requests
import json
import time
from typing import Optional, Dict, Any

class TaskGenerationClient:
    """
    Client for interacting with the Task Generation API
    """
    
    def __init__(self, base_url: str = "http://localhost:5000", timeout: int = 300):
        self.base_url = base_url.rstrip('/')
        self.timeout = timeout
        self.session = requests.Session()
        
    def health_check(self) -> bool:
        """Check if API server is healthy"""
        try:
            response = self.session.get(f"{self.base_url}/api/health", timeout=10)
            return response.status_code == 200
        except:
            return False
    
    def generate_layer_tasks(self, 
                           layers_data: list, 
                           number_of_respondents: int, 
                           exposure_tolerance_pct: float = 2.0, 
                           seed: Optional[int] = None) -> Dict[str, Any]:
        """
        Generate layer tasks via API call
        
        Args:
            layers_data: Layers configuration data
            number_of_respondents: Number of respondents
            exposure_tolerance_pct: Exposure tolerance percentage (default: 2.0)
            seed: Random seed (not used in original logic)
        
        Returns:
            API response with generated tasks
        """
        print(f"🔄 Starting layer task generation via API at {time.strftime('%H:%M:%S')}")
        
        payload = {
            "layers": layers_data,
            "number_of_respondents": number_of_respondents,
            "exposure_tolerance_pct": exposure_tolerance_pct,
            "seed": seed
        }
        
        response = self.session.post(
            f"{self.base_url}/api/generate-layer-tasks",
            json=payload,
            headers={'Content-Type': 'application/json'},
            timeout=self.timeout
        )
        
        response.raise_for_status()
        result = response.json()
        
        if result.get('success'):
            print(f"✅ Layer tasks generated successfully at {result.get('timestamp', 'unknown time')}")
            return result
        else:
            raise Exception(f"API Error: {result.get('error', 'Unknown error')}")
    
    def generate_grid_tasks(self, 
                          categories_data: list, 
                          number_of_respondents: int, 
                          exposure_tolerance_cv: float = 1.0, 
                          seed: Optional[int] = None) -> Dict[str, Any]:
        """
        Generate grid tasks via API call
        
        Args:
            categories_data: Categories configuration data
            number_of_respondents: Number of respondents
            exposure_tolerance_cv: Exposure tolerance CV (default: 1.0)
            seed: Random seed
        
        Returns:
            API response with generated tasks and tasks_matrix
        """
        payload = {
            "categories": categories_data,
            "number_of_respondents": number_of_respondents,
            "exposure_tolerance_cv": exposure_tolerance_cv,
            "seed": seed
        }
        
        response = self.session.post(
            f"{self.base_url}/api/generate-grid-tasks",
            json=payload,
            headers={'Content-Type': 'application/json'},
            timeout=self.timeout
        )
        
        response.raise_for_status()
        result = response.json()
        
        if result.get('success'):
            print("✅ Grid tasks generated successfully")
            return result
        else:
            raise Exception(f"API Error: {result.get('error', 'Unknown error')}")
    
    def close(self):
        """Close the session"""
        self.session.close()