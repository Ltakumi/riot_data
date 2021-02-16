from itertools import chain
import os
import pandas as pd
import time
from tqdm import tqdm
from .riot_api import Riot_API

DEFAULTKEEP = ['accountId', 'summonerId', 'summonerName', 'tier',
               'rank', 'leaguePoints', 'wins', 'losses', 'updated']

class player_db():

    def __init__(self, api_key, path2db, region, additional=None, freshapi=False, ntries=3, save_every=600):

        self.api = Riot_API(api_key, freshapi, ntries)

        self.region = region
        self.additonal = additional
        if additional:
            self.tokeep = DEFAULTKEEP +  additional
        else:
            self.tokeep = DEFAULTKEEP

        self.path2db = path2db
        if os.path.exists(path2db):
            self.db = pd.read_csv(path2db)
        else:
            self.db = pd.DataFrame(columns=self.tokeep)

        self.save_every = save_every

    def update_players_db(self, divisions, max_players=1000, queue='RANKED_SOLO_5x5', overwrite=False):

        save = time.time()

        # if maxplayers is a single number we multiply to match divisions
        # if not must be same lenght as divisions
        if isinstance(max_players, int):
            max_players = [max_players]*len(divisions)
        else:
            assert len(max_players) == len(divisions)

        for division, max_player in zip(divisions, max_players):
            tier, division = division.split('_')
            print('Region:', self.region, 'Tier:', tier, 'Division:', division)

            # get player list
            player_list = self.api.get_players_division(self.region, queue, tier, division, max_player)

            for player in tqdm(player_list):
                idx = self.db.index[self.db['summonerId']==player['summonerId']]

                # new player
                if len(idx)==0:
                    account = self.api.get_accountid(self.region, player['summonerId'])
                    player = dict(chain.from_iterable(d.items() for d in (player, account)))
                    player['updated'] = time.strftime('%Y-%m-%d %H:%M:%S')
                    self.db = self.db.append(pd.Series({i:player[i] for i in self.tokeep}), ignore_index=True)

                elif len(idx)==1 and overwrite:
                    account = self.api.get_accountid(self.region, player['summonerId'])
                    player = dict(chain.from_iterable(d.items() for d in (player, account)))
                    player['updated'] = time.strftime('%Y-%m-%d %H:%M:%S')
                    self.db.loc[idx[0]] = pd.Series({i:player[i] for i in self.tokeep})

            if time.time() - save > self.save_every:
                save = time.time()
                self.db.to_csv(self.path2db, index=False)
                print('Checkpoint saved')

        self.db.to_csv(self.path2db, index=False)
        print('Region:', self.region, 'over, saved to', self.path2db)
