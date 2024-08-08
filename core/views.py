from rest_framework import viewsets, status
from .models import Participant, Tournament, Round, Match, TournamentParticipant
from .serializers import ParticipantSerializer, TournamentSerializer, RoundSerializer, MatchSerializer, TournamentParticipantSerializer
from rest_framework.response import Response
from rest_framework.decorators import action
from django.db import transaction
from django.core.exceptions import ObjectDoesNotExist
import random
from django.shortcuts import get_object_or_404

class ParticipantViewSet(viewsets.ModelViewSet):
    queryset = Participant.objects.all()
    serializer_class = ParticipantSerializer


class TournamentViewSet(viewsets.ModelViewSet):
    queryset = Tournament.objects.all()
    serializer_class = TournamentSerializer
    lookup_field = 'generated_key' # uses this field insead of id when looking up for a single tournament

    # create a tournament
    def create(self, request):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            # Process valid data
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            # Return error response for invalid data
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    # endpoint to join a tournament
    @action(detail=True, methods=['post']) # detail means actions intended for a single object
    #all db actions are cancelled if there's an exception raised (ValidationErrors are also exceptions)
    @transaction.atomic
    def join(self, request, generated_key=None):
        tournament = self.get_object()

        participant_serializer = ParticipantSerializer(data=request.data)
        participant = None

        # get participant if exists, or create a new one if it doesnt
        try:
            participant = Participant.objects.get(email = request.data['email'])
            
        except Participant.DoesNotExist:
            if participant_serializer.is_valid(raise_exception=True):
                participant = participant_serializer.save()
            else:
                return Response(participant_serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        #save tournament_participant record
        tp_data = {
            "tournament": tournament.id,
            "participant": participant.id
        }
        tp_serializer = TournamentParticipantSerializer(data=tp_data)
        
        if tp_serializer.is_valid(raise_exception=True):
            tp_serializer.save()
            return Response(f"{participant.name} has joined {tournament.name} ({tournament.generated_key})", status=status.HTTP_201_CREATED)
        
        else:
            return Response(tp_serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
    # shows all participants of the tournament
    @action(detail=True, methods=['get'])
    def participants(self, request, generated_key=None):


        tournament = self.get_object()
        tourn_participants = TournamentParticipant.objects.filter(tournament = tournament.id)

        #check if there are participants in the given tournament
        if tourn_participants:
            # list comprehension to create a list of all participants
            participants = [tp.participant for tp in tourn_participants]
            # serialize 
            participant_serializer = ParticipantSerializer(participants, many=True)
            return Response(participant_serializer.data, status=status.HTTP_200_OK)
        
        else:
            return Response('Tournament has no participants yet', status=status.HTTP_200_OK)



    
    # removes a given participant from the given tournament
    @action(detail=True, methods=['delete'])
    def remove_participant(self, request, generated_key=None):
        tournament = self.get_object()
        participant_id = request.data['id']
        try:
            TournamentParticipant.objects.get(tournament=tournament.id, participant = participant_id).delete()
            return Response('Participant removed from tournament.', status=status.HTTP_204_NO_CONTENT)
        except:
            return Response('Participant could not be removed from tournament.', status=status.HTTP_400_BAD_REQUEST)

    # generates the bracket of the tournament
    @action(detail=True, methods=['post'])
    def generate_bracket(self, request, generated_key=None):

        tournament = self.get_object()
        
        # ensure the bracket hasn't been generated yet
        if tournament.rounds.exists():
            return Response({'error': 'Bracket already generated for this tournament.'}, status=status.HTTP_400_BAD_REQUEST)
        
        tournament_participants = list(TournamentParticipant.objects.filter(tournament=tournament.id))
        # get all participants
        participants = [part.participant for part in tournament_participants]

        if len(participants) != tournament.number_of_teams:
            return Response({'error': f"The tournament needs to be full to generate a bracket. {len(participants)}/{tournament.number_of_teams} participants"}, status=status.HTTP_400_BAD_REQUEST)
        
        # create all rounds
        with transaction.atomic():
            self.create_rounds(tournament, participants)

        return Response({'status': 'Knockout bracket generated.'}, status=status.HTTP_201_CREATED)
   

    def create_rounds(self, tournament, participants):

        #4 teams -> 2 rounds
        #8 teams -> 3 rounds
        #16 teams -> 4 rounds
        #32 teams -> 5 rounds
        #64 teams -> 6 rounds

        # get the number of rounds needed
        rounds_count = 2
        match len(participants):
            case 8:
                rounds_count += 1
            case 16:
                rounds_count += 2
            case 32:
                rounds_count += 3
            case 64:
                rounds_count += 4

        # Randomises participants list
        shuffled_participants = randomize_list(participants)

        #create all matches for the first round
        round1_instance = Round.objects.create(tournament=tournament, round_number=1)
        matches = []
        while len(shuffled_participants) > 1:
            participant1 = shuffled_participants.pop(0)
            participant2 = shuffled_participants.pop(0)
            matches.append(Match(round=round1_instance, participant1=participant1, participant2=participant2))

        previous_round_matches = Match.objects.bulk_create(matches)
        

        # create matches for the rest of the rounds
        
        # half the amount of participants for round 2
        number_participants = int(len(participants)/2)
        # loop to create the following rounds, starting from round 2
        for round_number in range(2,rounds_count+1):
            round_instance = Round.objects.create(tournament=tournament, round_number=round_number)
            if number_participants > 1:
                # indexes to update the 'next_match' field in the previous round matches
                upper_match = 0
                lower_match = 1
                # number of matches is always half the number of participants in the current round
                for i in range(int(number_participants/2)):
                    # create a match 
                    new_match = Match.objects.create(round=round_instance, participant1= None, participant2=None)
                    
                    # update the 'next_match' field with the newly created match
                    # ensures that the first match on second round is between the winners of the first two matches of the first round, and so on
                    Match.objects.filter(id=previous_round_matches[upper_match].id).update(next_match=new_match)
                    Match.objects.filter(id=previous_round_matches[lower_match].id).update(next_match=new_match)

                    # update indexes
                    upper_match += 2
                    lower_match += 2

            # get the newly created list of matches to be updated on the following round     
            previous_round = Round.objects.get(tournament=tournament, round_number=round_number)
            previous_round_matches = Match.objects.filter(round = previous_round.id)

            # after each round, participants are halved
            number_participants /= 2       
                    
    # Algorithm summary: create all matches of the first round with shuffled participants
    # then create the remaining matches of the whole tournament round by round,
    # every time a new match is created the field 'next_match' from the corresponding matches from the previous round are updated
    

class RoundViewSet(viewsets.ModelViewSet):
    queryset = Round.objects.all()
    serializer_class = RoundSerializer


class MatchViewSet(viewsets.ModelViewSet):
    queryset = Match.objects.all()
    serializer_class = MatchSerializer

    # partial_update allows to update just one field
    # update winner field
    @action(detail=True, methods=['patch'])
    def input_winner(self, request, pk=None):
        
        match = get_object_or_404(Match.objects.all(), pk=pk)
        data = {'winner': request.data['winner']}
        
        # partial serializer update
        serializer = self.get_serializer(match, data=data, partial=True)

        if serializer.is_valid(raise_exception=True):
            # Match.objects.filter(id=match.next_match.id).update(participant1= None)
            # Match.objects.filter(id=match.next_match.id).update(participant2= None)

            # #update the next match's participants with the winner
            if match.next_match.participant1 == None:
                Match.objects.filter(id=match.next_match.id).update(participant1=serializer.validated_data['winner'])
            elif match.next_match.participant2 == None:
                Match.objects.filter(id=match.next_match.id).update(participant2=serializer.validated_data['winner'])

            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


def randomize_list(input_list):
    # Create a copy of the input list to avoid modifying the original list
    shuffled_list = input_list.copy()
    
    # Shuffle the elements in the copied list
    random.shuffle(shuffled_list)
    
    return shuffled_list
