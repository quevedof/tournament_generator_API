# Knockout Tournament Generator API

RESTful API built in Django REST Framework that enables the creation of single elimination knockout tournament brackets of 4, 8, 16, 32, or 64 teams.

### Features
- Create single-elimination tournaments
- Add participants to tournaments
- Generates all matches to be played in the tournament in a bracket style
- When a match is updated, the winner automatically becomes a participant on the next round's corresponding match.

### Prerequistes
- Python 3.x

### Installation
1. Clone the repository
    ```
    git clone https://github.com/quevedof/tournament_generator_API.git

    cd tournament_generator_API
    ``` 
2. Enable virtual environment (optional)
    ```
    python -m venv .venv
    .venv/Scripts/activate
    ```
3. Install dependecies
    ```
    pip install -r requirements.txt
    ```
4. Make SqliteDB migrations
    ```
    py manage.py makemigrations
    py manage.py migrate
    ```
5. Run API server
    ```
    py manage.py runserver
    ```

### API Endpoints:
Method | Endpoint | Description
--- | --- | ---
POST| `/api/tournaments/`| Create a new tournament
POST| `/api/tournaments/{tournamentKey}/join/` | Add participant to a tournament
GET| `/api/tournaments/{tournamentKey}/participants` | Get tournament participants
DELETE | `/api/tournaments/{tournamentKey}/remove_participant/` | Removes participant from a tournament
GET| `/api/tournaments/{tournamentKey}`| Get tournament details including all its rounds and matches
POST| `/api/tournaments/{tournamentKey}/generate_bracket/`| Generates tournament brackets
PATCH| `/api/matches/<int:match_id>/input_winner/` | Updates a match to add a winner
GET| `/api/rounds/`| Get all rounds with their matches for all tournaments
GET| `/api/tournaments/`| Get all tournaments

