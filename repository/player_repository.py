"""
Module for managing player information and storage.

This module contains functions and classes for managing player data storage
and retrieval, including loading players from a JSON file,
sorting them alphabetically, adding new players, and displaying player details.

Classes:
    - PlayerRepository:
    Manages the storage and retrieval of player information.

Functions:
    - get_selected_player:
    Get the selected player based on user input.
"""

import os
import json

from model.player import Player


def get_selected_player(sorted_players):
    """Get the selected player based on user input."""
    while True:
        index_input = input("Entrez l'index du joueur : ")
        if index_input.isdigit():
            index = int(index_input)
            if 1 <= index <= len(sorted_players):
                player_data = sorted_players[index - 1]
                player_instance = Player(player_data['firstname'],
                                         player_data['lastname'],
                                         player_data['birth'],
                                         player_data['national chess ID'])
                return player_instance, index
            else:
                print("\033[91mIndex invalide.\033[0m")

        else:
            print("\033[91mVeuillez indiquer un numéro valide.\033[0m")


class PlayerRepository:
    """Repository for managing player data storage and retrieval."""

    def __init__(self, filename='players.json'):
        """Initialize the PlayerRepository.

        Args:
            filename (str, optional):
            Name of the JSON file to store player data.
            Defaults to 'players.json'.
        """
        data_dir = os.path.join(os.path.dirname(__file__), '..', 'data')
        self.filename = os.path.join(data_dir, filename)

    def load_players(self):
        """Load players from the JSON file.

        Returns:
            List[dict]: A list of dictionaries
            containing player information loaded from the JSON file.
            If the file does not exist, an empty list is returned.
        """
        if not os.path.exists(self.filename):
            return []

        with open(self.filename, 'r') as file:
            players = json.load(file)
        return players

    def get_player_by_alphabetical_order(self):
        """Get players from the repository sorted alphabetically by last name.

        Returns:
            List[Dict[str, str]]: A list of dictionaries
            representing player information sorted alphabetically
            by last name.

        Note:
            This method retrieves player data from the repository,
            sorts the players alphabetically
            by last name, and returns a list of dictionaries.
        """
        players = self.load_players()
        sorted_players = sorted(players, key=lambda x: x['lastname'])
        return sorted_players

    def add_player(self, player):
        """Add a player to the repository."""

        players = self.load_players()
        players.append(player.to_json())

        with open(self.filename, 'w') as file:
            json.dump(players, file, indent=4)

    def display_players_by_index(self):
        """Get a player from the repository by index."""
        sorted_players = self.get_player_by_alphabetical_order()
        print("\nListe des joueurs triés par ordre alphabétique:")
        for i, player_data in enumerate(sorted_players):
            print(f"{i + 1} - {player_data['lastname']} "
                  f"{player_data['firstname']}")
        return sorted_players


if __name__ == "__main__":
    pass
