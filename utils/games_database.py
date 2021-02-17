import os
import time
import pandas as pd
import numpy as np
from .externalinfo import get_timestamped_patches
from .riot_api import Riot_API
from tqdm import tqdm
import json

DEFAULTKEEP = ['platformId', 'gameId', 'queue', 'timestamp', 'tier', 'rank', 'patch', 'updated', 'gameinfo', 'timeline']

class games_db():

    def __init__(self, api_key, path2db, region, additional=None, freshapi=False, ntries=3, save_every=600):

        self.api = Riot_API(api_key, freshapi, ntries)
        self.additonal = additional
        if additional:
            self.tokeep = DEFAULTKEEP +  additional
        else:
            self.tokeep = DEFAULTKEEP

        self.region = region
        self.path2db = path2db
        if os.path.exists(path2db):
            self.db = pd.read_csv(path2db)
        else:
            self.db = pd.DataFrame(columns=self.tokeep)
            self.db[:] = None

        self.save_every = save_every

    def update_games(self, path2playerdb, patches, queue=420):
        """
        For all players in path2playerdb, for all patches will fetch games and add to database
        """

        player_db = pd.read_csv(path2playerdb)

        save = time.time()

        timestamped_patches = get_timestamped_patches(self.region, patches, unit='ms')

        for patch in timestamped_patches:

            newgame = 0
            print('Region:', self.region, 'Patch:', patch, len(player_db), 'players')

            for accountid, tier, division in zip(tqdm(player_db['accountId']), player_db['tier'], player_db['rank']):

                match_list = self.api.get_matchlist_accountid(accountid, self.region, queue, timestamped_patches[patch])

                # no matchlist we just skip
                if match_list is None:
                    continue

                for game in match_list:
                    idx = self.db.index[self.db['gameId']==game['gameId']]

                    # new game
                    if len(idx)==0:
                        game['updated'] = time.strftime('%Y-%m-%d %H:%M:%S')
                        game['tier'] = tier
                        game['rank'] = division
                        game['patch'] = patch
                        self.db = self.db.append(pd.Series({i:game[i] for i in game.keys() if i in self.tokeep}), ignore_index=True)
                        newgame += 1

                if time.time() - save > self.save_every:
                    save = time.time()
                    self.db.to_csv(self.path2db, index=False)
                    print('Checkpoint saved')

            self.db.to_csv(self.path2db, index=False)
            print('Region:', self.region, 'Patch:', patch, newgame, 'new games, saved to', self.path2db)

    def download_games(self, path2games, index=None, gameinfo=True, timeline=True):

        if index is None:
            index = self.db.index

        os.makedirs(path2games, exist_ok=True)

        save = time.time()

        for idx in tqdm(index):

            gameid = self.db.loc[idx, 'gameId']

            if gameinfo:

                # already dl
                gameinfo = str(self.db.loc[idx, 'gameinfo'])
                if gameinfo != 'nan' and os.path.exists(gameinfo):
                    continue

                res = self.api.get_matchinfo(gameid, self.region)
                if res is not None:
                    path2save = path2games + self.region + '_' + str(gameid) + '_gameinfo.json'
                    self.db.loc[idx, 'gameinfo'] = path2save
                    json.dump(res, open(path2save, 'w'))

            if timeline:

                # already dl
                timeline = str(self.db.loc[idx, 'timeline'])
                if timeline != 'nan' and os.path.exists(timeline):
                    continue

                res = self.api.get_matchtimeline(gameid, self.region)
                if res is not None:
                    path2save = path2games + self.region + '_' + str(gameid) + '_timeline.json'
                    self.db.loc[idx, 'timeline'] = path2save
                    json.dump(res, open(path2save, 'w'))

            if time.time() - save > self.save_every:
                save = time.time()
                self.db.to_csv(self.path2db, index=False)
                print('Checkpoint saved')
