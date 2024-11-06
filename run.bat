REM Create a venv if not already there.
CALL py -m venv .

REM Activate the venv.
CALL ./Scripts/activate.bat

REM Install dependencies if not already installed.
CALL py -m pip install -r ./requirements.txt

REM Run the game.
CALL py -O ./src/main.py