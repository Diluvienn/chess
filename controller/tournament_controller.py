"""Module containing the TournamentController class and related functions.

This module provides a controller class
for managing tournament-related operations,
such as displaying tournaments,
showing tournament details, creating new tournaments,
and playing tournaments.
It also includes helper functions for calculating leaderboard,
getting tournament details,
and adding director notes to tournaments.

Classes:
    TournamentController:
    A controller class for managing tournament-related operations.

Functions:
    get_tournament_name_by_index:
    Get the name of the tournament corresponding to the given index.
    calculate_leaderboard:
    Calculate and display the leaderboard for a tournament.

"""

from datetime import datetime

from utils.confirm_return_menu import (confirm_return_to_previous_menu,
                                       confirm_stop_add_note,
                                       confirm_return_to_main_menu)
from model.tournament import Tournament
from model.round import Round
from repository.tournament_repository import TournamentRepository
from repository.player_repository import get_selected_player
from view.tournament_view import (display_tournament_list,
                                  get_tournament_index_from_user,
                                  prompt_add_players,
                                  prompt_play_tournament,
                                  ask_to_play_next_round,
                                  display_add_player_menu,
                                  get_user_choice)


def get_tournament_name_by_index(tournaments, tournament_index):
    """Get the name of the tournament corresponding to the given index.

    Args:
        tournaments (list): List of tournaments.
        tournament_index (int): Index of the tournament.

    Returns:
        str: Name of the tournament at the specified index,
        or None if index is invalid.

    """
    if 1 <= tournament_index <= len(tournaments):
        return tournaments[tournament_index - 1].name
    else:
        return None


def calculate_leaderboard(tournament, previous_scores):
    """Calculate and display the leaderboard for a tournament.

    Args:
        tournament (Tournament):
        The tournament object.
        previous_scores (dict):
        Dictionary containing previous scores of players.

    """
    # Crée une liste de tuples (joueur, score total)
    leaderboard = [(player,
                    player.calculate_total_score(tournament.rounds,
                                                 previous_scores))
                   for player in tournament.players_list]
    # Triez la liste en fonction du score total (en ordre décroissant)
    sorted_leaderboard = sorted(leaderboard, key=lambda x: x[1], reverse=True)

    tournament.players_score = \
        {f"{player.firstname} {player.lastname}": score
         for player, score in sorted_leaderboard}
    # Affiche le classement
    # Vérifie si c'est le dernier round
    if tournament.current_round == len(tournament.rounds) - 1:
        print("\nClassement final du tournoi :")
    else:
        print(f"\nClassement fin du round {tournament.current_round + 1} :")

    # Afficher le classement
    for i, (player, score) in enumerate(sorted_leaderboard, start=1):
        print(f"{i}. {player.firstname} {player.lastname} : {score} points")


class TournamentController:
    """A controller class for managing tournament-related operations."""
    def __init__(self,
                 tournament_repository,
                 tournament_view,
                 player_repository,
                 player_controller):
        self.tournament_repository = tournament_repository
        self.tournament_view = tournament_view
        self.player_repository = player_repository
        self.player_controller = player_controller
        self.num_players = 0

    def show_tournaments(self):
        """Display the list of tournaments."""
        tournaments = (
            self.tournament_repository.get_tournaments_by_alphabetical_order())
        display_tournament_list(tournaments)
        return tournaments

    def show_tournament_details(self):
        """Display details of a selected tournament."""
        tournaments = self.show_tournaments()
        total_tournaments = len(tournaments)
        tournament_index = (
            get_tournament_index_from_user(total_tournaments))
        if tournament_index is not None:
            tournament_name = (
                get_tournament_name_by_index(tournaments, tournament_index))
            self.get_tournament_details(tournament_name)
        else:
            return

    def create_new_tournament(self):
        """Create a new tournament with the details provided by the user.

        Returns:
            Tournament:
            The newly created tournament object,
            or None if the creation was canceled.

        """
        tournament_details = (
            self.tournament_view.get_new_tournament_details())

        if tournament_details is None:
            print("Retour au menu principal sans sauvegarde.")
            return

        (name, place, date_start, date_end,
         director_note, rounds) = tournament_details

        # Création du tournoi avec les détails fournis
        new_tournament = Tournament(name=name,
                                    place=place,
                                    date_start=date_start,
                                    date_end=date_end,
                                    director_note=director_note)

        # Ajout des rounds
        if rounds is not None:
            for round_details in rounds:
                round_name = round_details["name"]
                start_time = round_details["start_time"]
                end_time = round_details["end_time"]
                matches = round_details.get("matches", [])
                new_round = Round(round_name, matches, start_time, end_time)
                new_tournament.add_round(new_round)

            # Ajout du tournoi à la base de données
            self.tournament_repository.add_tournament(new_tournament)

            # Initialisation de la liste des joueurs du tournoi
            if prompt_add_players():
                self.add_players_to_tournament(new_tournament)

            print(f"\nLe tournoi {new_tournament.name} à "
                  f"{new_tournament.place} avec a bien été enregistré.")

        return new_tournament

    def add_players_to_tournament(self, tournament):
        """Add players to the tournament.
        Args:
            tournament (Tournament):
            The tournament to which players will be added.
        """
        selected_players_index = []
        selected_players = []
        sorted_players_list = self.player_repository.display_players_by_index()

        # Ajouter les joueurs déjà présents dans le tournoi
        for player in tournament.players_list:
            selected_players.append(player)
            self.num_players += 1

        if tournament.players_list:
            print("\nJoueurs déjà inscrits dans le tournoi:")
            for player in selected_players:
                print(f"- {player.firstname} {player.lastname}")
            tournament.players_list = []

        print("\n\033[92mInfo : Le nombre de joueur "
              "doit être de minimum 6 et pair.\033[0m")

        while True:
            display_add_player_menu(self.num_players)
            user_choice = get_user_choice()
            if user_choice == "1":
                selected_player, index = (
                    get_selected_player(sorted_players_list))
                # Vérifier si le joueur est déjà dans le tournoi
                if any(player.firstname == selected_player.firstname and
                       player.lastname == selected_player.lastname
                       for player in selected_players):
                    print("Ce joueur est déjà ajouté au tournoi.")

                    continue
                # Ajouter le joueur au tournoi
                selected_players_index.append(index)
                selected_players.append(selected_player)
                self.num_players += 1
                print(f"Ajout du joueur "
                      f"{selected_player.firstname} "
                      f"{selected_player.lastname}")
                print("\nJoueurs inscrits dans le tournoi:")
                for player in selected_players:
                    print(f"- {player.firstname} {player.lastname}")

            elif user_choice == "2":
                # Ajouter un nouveau joueur
                new_player = self.player_controller.create_new_player()
                if new_player is not None:
                    print(f"new_player : {new_player}")

                    # Ajouter le joueur au tournoi
                    selected_players.append(new_player)
                    self.num_players += 1
                    print(f"Ajout du joueur "
                          f"{new_player.firstname} {new_player.lastname}")
                    print("\nJoueurs inscrits dans le tournoi:")
                    for player in selected_players:
                        print(f"- {player.firstname} {player.lastname}")
                else:
                    continue

            elif user_choice == "3":
                # Vérifier si le nombre de joueurs est pair et au moins 6
                if (len(selected_players) >= 6
                        and len(selected_players) % 2 == 0):
                    for player in selected_players:
                        tournament.players_list.append(player)
                    self.tournament_repository.add_tournament(tournament)
                    print("Les joueurs ont bien été ajoutés.")
                    if prompt_play_tournament():
                        self.play_tournament(tournament)
                    break
                else:
                    print("Le nombre d'inscrits doit être pair "
                          "et au moins égal à 6.")
            elif user_choice == "q":
                if confirm_return_to_main_menu():
                    break
            else:
                print("\033[91mVeuillez indiquer un choix valide.\033[0m")

    def resume_unstarted_tournament(self):
        unstarted_tournaments = (
            self.tournament_repository.find_unstarted_tournaments())
        if not unstarted_tournaments:
            self.tournament_view.display_no_unstarted_tournaments_message()
            return
        (self.tournament_view.
         display_unstarted_tournaments(unstarted_tournaments))
        chosen_tournament = (
            self.tournament_view.get_chosen_tournament(unstarted_tournaments))
        if chosen_tournament:
            self.tournament_view.display_chosen_tournament(chosen_tournament)
            tournament = Tournament.from_json(chosen_tournament)
            self.add_players_to_tournament(tournament)
        else:
            return

    def get_tournament_details(self, tournament_name):
        """Display the details of the specified tournament.
        Args:
            tournament_name (str): The name of the tournament.
        """
        tournament_details = \
            self.tournament_repository.get_tournament_details(tournament_name)
        if tournament_details:
            # Afficher les détails du tournoi
            self.tournament_view.display_tournament_details(tournament_details)
        else:
            print("Le tournoi spécifié n'existe pas ou n'a pas été trouvé.")

    def add_director_notes_to_tournament(self):
        """Add director's notes to the tournament.
        Returns:
            str or None: The director's notes entered by the user,
            or None if canceled.
        """
        while True:
            notes = input("Ajouter des notes du directeur (y/n) ? : ")
            if notes.lower() == "y":
                notes_text = input("Entrez les notes du directeur : ")
                if notes_text == "q":
                    if confirm_stop_add_note():
                        return ""
                else:
                    return notes_text
            elif notes.lower() == "n":
                return ""
            elif notes.lower() == 'q':
                if confirm_return_to_previous_menu():
                    return None
            else:
                print("Choix invalide.")

    def resume_tournament(self):
        """Resume an unfinished tournament."""
        chosen_tournament = self.tournament_repository.resume_tournament()
        if chosen_tournament:
            tournament = Tournament.from_json(chosen_tournament)
            self.play_tournament(tournament)
        else:
            return

    def play_tournament(self, tournament):
        """Play the specified tournament.

        Args:
            tournament (Tournament): The tournament to be played.

        """
        while tournament.current_round <= len(tournament.rounds):
            current_round = tournament.rounds[tournament.current_round]

            print(f"\nRound {tournament.current_round + 1} :")

            # Définir l'heure de début du round s'il n'est pas déjà défini
            if current_round.start_time is None:
                current_round.start_time = (
                    datetime.now().strftime("%d-%m-%Y %H:%M"))

            # Générer les paires de matchs pour ce round
            tournament.generate_pairs_for_round()

            for match in current_round.matches:
                player1 = list(match.players.keys())[0]
                player2 = list(match.players.keys())[1]
                player1_name = f"{player1.firstname} {player1.lastname}"
                player2_name = f"{player2.firstname} {player2.lastname}"
                score1 = match.players[player1]
                score2 = match.players[player2]
                print(f"Match: {player1_name} vs {player2_name}, "
                      f"Scores: {score1}-{score2}")

            # Récupérer les scores précédents à partir des données du tournoi
            previous_scores = self.players_score \
                if hasattr(self, 'players_score') else {}

            # Calculer et afficher le classement provisoire
            calculate_leaderboard(tournament, previous_scores)

            if current_round.end_time is None:
                current_round.end_time = (
                    datetime.now().strftime("%d-%m-%Y %H:%M"))

            # Demander si vous voulez jouer le prochain round

            if tournament.current_round == (len(tournament.rounds) - 1):
                tournament.current_round += 1
                tournament_repository = TournamentRepository()
                tournament_repository.add_tournament(tournament)
                break

            if not ask_to_play_next_round():
                tournament.current_round += 1
                tournament_repository = TournamentRepository()
                tournament_repository.add_tournament(tournament)
                break

            tournament.current_round += 1


if __name__ == "__main__":
    pass
