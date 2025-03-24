# 🐱 Cat Food Weight Tracker 🐱

A Streamlit application to track the food consumption of three cats: Mittens, Cheddar, and Lola.

## Features

- Track initial food weight for each cat's bowl
- Record remaining food weight to calculate consumption
- Beautiful, interactive UI with individual tracking for each cat
- 30-day historical graphs showing:
  - Initial food weight
  - Remaining food weight
  - Consumed food (the difference)
- Persistent storage using SQLite database

## Installation

1. Clone the repository:
   ```
   git clone https://github.com/chemgear/fatcat.git
   cd fatcat
   ```

2. Create a virtual environment and install dependencies:
   ```
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   pip install -e .
   ```

## Usage

1. Run the application:
   ```
   python main.py
   ```

2. Or run the Streamlit app directly:
   ```
   streamlit run catweight/app.py
   ```

3. Open the application in your web browser (typically http://localhost:8501).

4. For each cat:
   - Enter the initial weight of the food bowl when filled
   - Later, enter the remaining weight to track consumption
   - View statistics and trends over time

## Development

### Running Tests

Run the unit tests with pytest:

```
pytest catweight/tests/
```

### Project Structure

- `catweight/app.py` - Main Streamlit application
- `catweight/db.py` - Database operations for tracking cat food weights
- `catweight/tests/` - Unit tests
- `main.py` - Entry point for the application

## License

MIT
