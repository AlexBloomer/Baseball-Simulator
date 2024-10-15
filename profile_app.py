from app import app  # Import your Flask app
from werkzeug.serving import run_simple

# Start the app manually
def run():
    run_simple('localhost', 5000, app)

if __name__ == "__main__":
    import cProfile
    cProfile.run('run()', sort='time')
