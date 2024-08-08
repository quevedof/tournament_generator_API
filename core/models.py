from django.db import models
import random, string

class Participant(models.Model):
    name = models.CharField(max_length=100)
    surname = models.CharField(max_length=100)
    email = models.EmailField(unique=True)

    def __str__(self):
        return self.name

class Tournament(models.Model):
    name = models.CharField(max_length=100)
    generated_key = models.CharField(max_length=255, unique=True, default=''.join(random.choices(string.ascii_letters + string.digits, k=10))) #generate random 10 chars string
    number_of_teams = models.IntegerField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name
    
class TournamentParticipant(models.Model):
    tournament = models.ForeignKey(Tournament, on_delete=models.CASCADE)
    participant = models.ForeignKey(Participant, on_delete=models.CASCADE)
    
    class Meta:
        unique_together = ('tournament', 'participant')

class Round(models.Model):
    tournament = models.ForeignKey(Tournament, related_name='rounds', on_delete=models.CASCADE)
    round_number = models.IntegerField()

    # def __str__(self):
    #     return f"{self.tournament.name} - Round {self.round_number}"

class Match(models.Model):
    round = models.ForeignKey(Round, related_name='matches', on_delete=models.CASCADE) # related name reverse relationship, so when rounds are queried, also return the matches on that round
    participant1 = models.ForeignKey(Participant, related_name='matches_as_participant1', on_delete=models.SET_NULL, null=True)
    participant2 = models.ForeignKey(Participant, related_name='matches_as_participant2', on_delete=models.SET_NULL, null=True)
    winner = models.ForeignKey(Participant, related_name='matches_as_winner', null=True, blank=True, on_delete=models.SET_NULL)
    next_match = models.ForeignKey('self', on_delete=models.SET_NULL, null=True, blank=True)

    # def __str__(self):
    #     return f"{self.participant1.name} vs {self.participant2.name}"
