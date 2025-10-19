import requests
import json
import time
from typing import Optional, Dict, Any

class TaskGenerationClient:
    """
    Client for interacting with the Task Generation API
    """
    
    def __init__(self, base_url: str = "http://20.84.154.103:55001", timeout: int = 300):
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
        
        if response.status_code == 200:
            result = response.json()
            print(result)
            print(f"✅ Layer tasks generated successfully at {result.get('timestamp', 'unknown time')}")
            return result
        else:
            # Try to get error message from response
            try:
                error_result = response.json()
                error_msg = error_result.get('error', f'HTTP {response.status_code}')
            except:
                error_msg = f'HTTP {response.status_code}'
            raise Exception(f"API returned error: {error_msg}")
    
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
        print(payload)
        response = self.session.post(
            f"{self.base_url}/api/generate-grid-tasks",
            json=payload,
            headers={'Content-Type': 'application/json'},
            timeout=self.timeout
        )
        
        if response.status_code == 200:
            result = response.json()
            print(result)
            print(f"✅ Layer tasks generated successfully at {result.get('timestamp', 'unknown time')}")
            return result
        else:
            # Try to get error message from response
            try:
                error_result = response.json()
                error_msg = error_result.get('error', f'HTTP {response.status_code}')
            except:
                error_msg = f'HTTP {response.status_code}'
            raise Exception(f"API returned error: {error_msg}")
    
    def close(self):
        """Close the session"""
        self.session.close()