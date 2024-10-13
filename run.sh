# Create a venv if not already there.
python3 -m venv .

# Activate the venv.
chmod +x ./bin/activate
source ./bin/activate

# Install dependencies if not already installed.
python3 -m pip install -r ./requirements.txt

# Run the game.
python3 -O ./src/main.py