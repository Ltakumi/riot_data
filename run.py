from utils.player_database import player_db
from utils.games_database import games_db
import multiprocessing
from configparser import ConfigParser

config = ConfigParser()
config.read("config.ini")

general = config['GENERAL']
target = config['TARGET']


def get_player_db(region):
    """ Find list of players for a specific region """

    players = player_db(general['api_key'], general['path2db'] + region + '_playerdb.csv', region, freshapi=True)
    players.update_players_db(divisions=target['high_elo'], max_players=target['high_elo_players'])
    players.update_players_db(divisions=target['low_elo'], max_players=target['low_elo_players'])
    return None

def get_games_db(region):
    """ Find list of games for a specific region """

    games = games_db(key, general['path2db'] + region + '_gamesdb.csv', region, freshapi=True)
    games.update_games(general['path2db'] + region + '_playerdb.csv', target['patches'])
    return None

def dl_games_db(region):
    """ Download games for a specific region """

    games = games_db(key, general['path2db']+ region + '_gamesdb.csv', region, freshapi=True)
    games.download_games(general['path2games'], index=None, gameinfo=target['gameinfo'], timeline=target['timeline'])
    return None

def get_players():
    """ Find list of players for all regions in parallel """

    keprocs = []
    for region in target['regions']:
        keprocs.append(multiprocessing.Process(target=get_player_db, args=(region,)))
        keprocs[-1].start()

def get_games():
    """ Find list of players for all regions in parallel """

    keprocs = []
    for region in target['regions']:
        keprocs.append(multiprocessing.Process(target=get_games_db, args=(region,)))
        keprocs[-1].start()

def dl_games():
    """  Download games for all regions in parallel """

    keprocs = []
    for region in target['regions']:
        keprocs.append(multiprocessing.Process(target=dl_games_db, args=(region,)))
        keprocs[-1].start()

if __name__ == '__main__':

    if general['findplayers']:
        get_players()

    if general['findgames']:
        get_games()

    if general['dlgames']:
        dl_games()
