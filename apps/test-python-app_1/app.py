from flask import Flask, jsonify

# Create a Flask application instance
app = Flask(__name__)

# Define a route for the root URL '/'
@app.route('/')
def hello_world():
    """Returns a simple Hello World message."""
    return 'Hello from Microservice A (Python/Flask)!'

# Define a health check endpoint
@app.route('/health')
def health_check():
    """Returns a health status."""
    return jsonify({"status": "UP", "service": "test-python-app_1"}), 200

# Run the app if this script is executed directly
if __name__ == '__main__':
    # 0.0.0.0 makes it accessible from outside the container
    # Port 5000 is a common port for Flask apps
    app.run(host='0.0.0.0', port=5000, debug=True)