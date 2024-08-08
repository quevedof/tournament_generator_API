# Knockout Tournament Generator API

RESTful API built in Django REST Framework that enables the creation of single elimination knockout tournament brackets of 4, 8, 16, 32, or 64 teams.\
The API allows the creation of a tournament, addition of participants, and the complete generation of the bracket that includes all matches to be played. Once a winner is entered, it automatically becomes a participant on the next round's corresponding match.

## Endpoints:

### Create Tournament
POST `/api/tournaments/`

Request Body
```
{
    "name":"tournament1",
    "number_of_teams": 4
}
```
Response Body
```
{
    "id": 1,
    "rounds": [],
    "name": "tournament1",
    "generated_key": "qrZFoxmTvb",
    "number_of_teams": 4,
    "created_at": "2024-05-23T17:37:34.263638Z"
}
```

### Join Tournament
POST `/api/tournaments/<str:generated_key>/join/`

Request Body
```
{
    "name":"Bob",
    "surname": "Smith",
    "email":"bob@gmail.com"
}
```

### Get Tournament Participants
GET `/api/tournaments/{tournamentKey}/participants`

Response Body
```
[
    {
        "id": 1,
        "name": "Bobby",
        "surname": "Smith",
        "email": "bob@gmail.com"
    },
    {
        "id": 2,
        "name": "Jake",
        "surname": "Smith",
        "email": "jake@gmail.com"
    },
]
```

### Remove a participant from a given tournament
DELETE `api/tournaments/{tournamentKey}/remove_participant/`

Request Body
```
{
    "id":"5",
}
```

### Get Tournament Details by Key
GET `/api/tournaments/{tournamentKey}`

Response Body
```
{
    "id": 1,
    "rounds": [],
    "name": "tournament1",
    "generated_key": "qrZFoxmTvb",
    "number_of_teams": 4,
    "created_at": "2024-05-23T17:37:34.263638Z"
}
```

### Generate Tournament Brackets
POST `/api/tournaments/{tournamentKey}/generate_bracket/`

No Request Body

### Input winner of a match
PATCH `/api/matches/<int:match_id>/input_winner/`

Request Body
```
{
    "winner": 4,
}
```

Response Body
```
{
    "id": 6,
    "round": 3,
    "participant1": 2,
    "participant2": 4,
    "winner": 4,
    "next_match": 7
}
```



