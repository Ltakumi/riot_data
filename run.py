from utils.player_database import player_db
from utils.games_database import games_db
import multiprocessing
from configparser import ConfigParser
import os

config = ConfigParser()
config.read("config.ini")

general = config['GENERAL']
target = config['TARGET']

os.makedirs(general['path2db'], exist_ok = True)
os.makedirs(general['path2games'], exist_ok = True)

# convert type since when we read config its a string
def convert(x):
    # single integer
    try:
        return int(x)
    # list
    except:
        return x.replace('\n', ' ').split(', ')

def get_player_db(region):
    """ Find list of players for a specific region """

    players = player_db(general['api_key'], general['path2db'] + region + '_playerdb.csv', region, freshapi=True)
    players.update_players_db(divisions=convert(target['high_elo']), max_players=convert(target['high_elo_players']))
    players.update_players_db(divisions=convert(target['low_elo']), max_players=convert(target['low_elo_players']))
    return None

def get_games_db(region):
    """ Find list of games for a specific region """

    games = games_db(general['api_key'], general['path2db'] + region + '_gamesdb.csv', region, freshapi=True)
    games.update_games(general['path2db'] + region + '_playerdb.csv', convert(target['patches']))
    return None

def dl_games_db(region):
    """ Download games for a specific region """

    games = games_db(general['api_key'], general['path2db'] + region + '_gamesdb.csv', region, freshapi=True)
    games.download_games(general['path2games'], index=None, gameinfo=target.getboolean('gameinfo'), timeline=target.getboolean('timeline'))
    return None

def get_players():
    """ Find list of players for all regions in parallel """

    keprocs = []
    for region in convert(target['regions']):
        keprocs.append(multiprocessing.Process(target=get_player_db, args=(region,)))
        keprocs[-1].start()

    for job in keprocs:
        job.join()

    return None

def get_games():
    """ Find list of players for all regions in parallel """

    keprocs = []
    for region in convert(target['regions']):
        keprocs.append(multiprocessing.Process(target=get_games_db, args=(region,)))
        keprocs[-1].start()

    for job in keprocs:
        job.join()

    return None

def dl_games():
    """  Download games for all regions in parallel """

    keprocs = []
    for region in convert(target['regions']):
        keprocs.append(multiprocessing.Process(target=dl_games_db, args=(region,)))
        keprocs[-1].start()

    for job in keprocs:
        job.join()

    return None

if __name__ == '__main__':

    if general.getboolean('findplayers'):
        print('--- Getting players ---')
        get_players()

    if general.getboolean('findgames'):
        print('--- Finding games ---')
        get_games()

    if general.getboolean('dlgames'):
        print('--- Downloading games ---')
        dl_games()
