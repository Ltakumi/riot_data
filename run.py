from utils.player_database import player_db
from utils.games_database import games_db
import multiprocessing

key = 'RGAPI-d939b194-0b19-42e8-8acc-65276fe9d11f'

path2db =  '/Users/ltakumi/Documents/data/league/db/'
path2games = '/Users/ltakumi/Documents/data/league/games/'



def get_player_db(region):

    a = player_db(key, path2db + region + '_playerdb.csv', region, freshapi=True)

    # divisions = ['CHALLENGER_I', 'GRANDMASTER_I', 'MASTER_I']
    # a.update_players_db(divisions=divisions, max_players=500)

    divisions = []
    # divisions = ['DIAMOND_'+str(i) for i in ['I', 'II', 'III', 'IV']]
    # divisions += ['PLATINUM_'+str(i) for i in ['I', 'II', 'III', 'IV']]
    divisions += ['GOLD_'+str(i) for i in ['I', 'II', 'III', 'IV']]
    divisions += ['SILVER_'+str(i) for i in ['I', 'II', 'III', 'IV']]
    divisions += ['BRONZE_'+str(i) for i in ['I', 'II', 'III', 'IV']]
    divisions += ['IRON_'+str(i) for i in ['I', 'II', 'III', 'IV']]
    a.update_players_db(divisions=divisions, max_players=150)

    return None

def get_games_db(region):
    a = games_db(key, path2db + region + '_games.csv', region, freshapi=True)
    a.update_games(path2db + region + '_playerdb.csv', ['10.18']) # done
    return None

def dl_games_db(region):
    a = games_db(key, path2db + region + '_games.csv', region, freshapi=True)
    a.download_games(path2games, index=None, gameinfo=True, timeline=True)
    return None

def get_players():

    # regions = ['ru', 'kr', 'oc1',  'jp1', 'na1', 'eun1', 'euw1', 'tr1', 'la1', 'la2']
    regions = ['ru', 'kr', 'oc1',  'jp1', 'na1', 'eun1', 'tr1', 'la1', 'la2']

    keprocs = []
    for region in regions:
        keprocs.append(multiprocessing.Process(target=get_player_db, args=(region,)))
        keprocs[-1].start()

def get_games():

    regions = ['ru', 'kr', 'oc1',  'jp1', 'na1', 'eun1', 'tr1', 'la1', 'la2']

    keprocs = []
    for region in regions:
        keprocs.append(multiprocessing.Process(target=get_games_db, args=(region,)))
        keprocs[-1].start()

def dl_games():

    regions = ['ru', 'kr', 'oc1',  'jp1', 'na1', 'eun1', 'euw1', 'tr1', 'la1', 'la2']

    keprocs = []
    for region in regions:
        keprocs.append(multiprocessing.Process(target=dl_games_db, args=(region,)))
        keprocs[-1].start()



if __name__ == '__main__':
    # get_players()
    # get_games()
    dl_games()
