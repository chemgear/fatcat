"""
Entry point for the Cat Food Tracking application.
"""
import os
import sys
import subprocess


def run_streamlit_app():
    """Run the Streamlit app."""
    try:
        # Add the current directory to the Python path
        current_dir = os.path.dirname(os.path.abspath(__file__))
        sys.path.append(current_dir)
        
        # Run the Streamlit app
        subprocess.run(["streamlit", "run", os.path.join("catweight", "app.py")])
    except Exception as e:
        print(f"Error running Streamlit app: {e}")
        sys.exit(1)


def main():
    """Main entry point."""
    print("🐱 Starting Cat Food Weight Tracking App 🐱")
    run_streamlit_app()


if __name__ == "__main__":
    main()
