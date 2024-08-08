from rest_framework import serializers
from .models import Participant, Tournament, Round, Match, TournamentParticipant
from rest_framework.validators import UniqueTogetherValidator

class ParticipantSerializer(serializers.ModelSerializer):
    class Meta:
        model = Participant
        fields = '__all__'


class MatchSerializer(serializers.ModelSerializer):
    class Meta:
        model = Match
        fields = '__all__'


    def validate_winner(self, data):
        # ensure winner hasn't already been set
        if self.instance.winner != None:
            raise serializers.ValidationError("Winner has already been set.")

        # ensuring the winner is one of the two participants
        if data == self.instance.participant1 or data == self.instance.participant2:
            return data
        else:
            raise serializers.ValidationError("Winner must be a participant of the match.")



class RoundSerializer(serializers.ModelSerializer):
    matches = MatchSerializer(many=True, read_only=True)

    class Meta:
        model = Round
        fields = '__all__'

class TournamentSerializer(serializers.ModelSerializer):

    rounds = RoundSerializer(many=True, read_only=True) # rounds are also returned, so need to nest serialize Rounds

    class Meta:
        model = Tournament
        fields = '__all__'
    
    # validating the number of teams when creating a new tournament
    def validate_number_of_teams(self, data):
        bracket_size = (4, 8, 16, 32, 64)
        if data not in bracket_size:
            raise serializers.ValidationError("Number of teams must be 4, 8, 16, 32, or 64")
        return data
    
class TournamentParticipantSerializer(serializers.ModelSerializer):

    #tournament = TournamentSerializer()
    class Meta:
        model = TournamentParticipant
        fields = '__all__'

        # customise validation message for the uniqueness of tournament, participant
        validators = [
            UniqueTogetherValidator(
                queryset=TournamentParticipant.objects.all(),
                fields=['tournament', 'participant'],
                message= "Given participant is already participating in the given tournament."
            )
        ]
    
    
    def validate(self, data):
        
        # validate the tournament is not full before adding a new participant
        tournament = data['tournament']
        number_of_current_participants = TournamentParticipant.objects.filter(tournament=tournament.id).count()
        if tournament.number_of_teams == number_of_current_participants:
            raise serializers.ValidationError("Tournament is already full")
        return data