from flask import Flask, request, jsonify
import logging
import time
from utils.tesk_generation import generate_layer_tasks_v2, generate_grid_tasks_v2
app = Flask(__name__)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@app.route('/api/generate-layer-tasks', methods=['POST'])
def generate_layer_tasks_api():
    """
    API endpoint to generate layer tasks
    Expected JSON payload:
    {
        "layers": [...],  # layers data
        "number_of_respondents": int,
        "exposure_tolerance_pct": float (optional, default=2.0),
        "seed": int (optional, not used in original logic)
    }
    """
    try:
        # Get JSON data from request
        data = request.get_json()
        
        # Validate required fields
        if not data:
            return jsonify({
                "error": "No JSON data provided",
                "success": False
            }), 400
        
        if 'layers' not in data:
            return jsonify({
                "error": "Missing required field: 'layers'",
                "success": False
            }), 400
        
        if 'number_of_respondents' not in data:
            return jsonify({
                "error": "Missing required field: 'number_of_respondents'",
                "success": False
            }), 400
        
        # Extract parameters with defaults
        layers_data = data['layers']
        number_of_respondents = data['number_of_respondents']
        exposure_tolerance_pct = data.get('exposure_tolerance_pct', 2.0)
        seed = data.get('seed')  # Not used in original logic
        
        # Validate data types
        if not isinstance(layers_data, list):
            return jsonify({
                "error": "'layers' must be a list",
                "success": False
            }), 400
        
        if not isinstance(number_of_respondents, int) or number_of_respondents <= 0:
            return jsonify({
                "error": "'number_of_respondents' must be a positive integer",
                "success": False
            }), 400
        
        if not isinstance(exposure_tolerance_pct, (int, float)) or exposure_tolerance_pct <= 0:
            return jsonify({
                "error": "'exposure_tolerance_pct' must be a positive number",
                "success": False
            }), 400
        
        if seed is not None and not isinstance(seed, int):
            return jsonify({
                "error": "'seed' must be an integer",
                "success": False
            }), 400
        
        # Log the request with timestamp
        task_generation_start = time.time()
        logger.info(f"🔄 Starting layer task generation at {time.strftime('%H:%M:%S', time.localtime(task_generation_start))}")
        logger.info(f"Generating layer tasks for {number_of_respondents} respondents")
        
        # Call your layer function
        result = generate_layer_tasks_v2(
            layers_data=layers_data,
            number_of_respondents=number_of_respondents,
            exposure_tolerance_pct=exposure_tolerance_pct,
            seed=seed  # Not used in original logic
        )
        
        # Return successful response
        return jsonify(result), 200
        
    except Exception as e:
        logger.error(f"Error generating layer tasks: {str(e)}")
        return jsonify({
            "error": f"Internal server error: {str(e)}",
            "success": False
        }), 500

@app.route('/api/generate-grid-tasks', methods=['POST'])
def generate_grid_tasks_api():
    """
    API endpoint to generate grid tasks
    Expected JSON payload:
    {
        "categories": [...],  # categories data
        "number_of_respondents": int,
        "exposure_tolerance_cv": float (optional, default=1.0),
        "seed": int (optional)
    }
    """
    try:
        # Get JSON data from request
        data = request.get_json()
        
        # Validate required fields
        if not data:
            return jsonify({
                "error": "No JSON data provided",
                "success": False
            }), 400
        
        if 'categories' not in data:
            return jsonify({
                "error": "Missing required field: 'categories'",
                "success": False
            }), 400
        
        if 'number_of_respondents' not in data:
            return jsonify({
                "error": "Missing required field: 'number_of_respondents'",
                "success": False
            }), 400
        
        # Extract parameters with defaults
        categories_data = data['categories']
        number_of_respondents = data['number_of_respondents']
        exposure_tolerance_cv = data.get('exposure_tolerance_cv', 1.0)
        seed = data.get('seed')
        
        # Validate data types
        if not isinstance(categories_data, list):
            return jsonify({
                "error": "'categories' must be a list",
                "success": False
            }), 400
        
        if not isinstance(number_of_respondents, int) or number_of_respondents <= 0:
            return jsonify({
                "error": "'number_of_respondents' must be a positive integer",
                "success": False
            }), 400
        
        if not isinstance(exposure_tolerance_cv, (int, float)) or exposure_tolerance_cv <= 0:
            return jsonify({
                "error": "'exposure_tolerance_cv' must be a positive number",
                "success": False
            }), 400
        
        if seed is not None and not isinstance(seed, int):
            return jsonify({
                "error": "'seed' must be an integer",
                "success": False
            }), 400
        
        # Log the request
        logger.info(f"Generating grid tasks for {number_of_respondents} respondents")
        
        # Call your grid function
        grid_result = generate_grid_tasks_v2(
            categories_data=categories_data,
            number_of_respondents=number_of_respondents,
            exposure_tolerance_cv=exposure_tolerance_cv,
            seed=seed
        )
        
       
        
        # Return successful response with tasks matrix
        return jsonify(grid_result), 200
        
    except Exception as e:
        logger.error(f"Error generating grid tasks: {str(e)}")
        return jsonify({
            "error": f"Internal server error: {str(e)}",
            "success": False
        }), 500

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        "status": "healthy",
        "service": "Task Generation API",
        "endpoints": {
            "layer_tasks": "/api/generate-layer-tasks",
            "grid_tasks": "/api/generate-grid-tasks"
        }
    }), 200

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=55001)  # Run on port 55001