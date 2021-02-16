from .apimanager import ApiManager

class Riot_API():
    """
    Class for getting information from riot api
    """

    def __init__(self, api_key, freshapi=False, ntries=3, verbose=False):

        self.apimanager = ApiManager(api_key, freshapi, verbose)
        self.ntries = ntries

    def get_players_division(self, region, queue, tier, division, max_players):
        """
        Provide a list of players in a division inside a tier
        Uses the entries with summonerId, but it is missing accountId
        Args :
            - tier : league tier (chall etc)
            - division : I II III IV
            - maxplayers : int
        """

        res = []
        page, findmore = 1, True # enter loop

        while findmore:

            url = 'https://' + region + '.api.riotgames.com/lol/'
            if tier in ['CHALLENGER', 'GRANDMASTER', 'MASTER']:
                url += 'league-exp/v4/entries/'
            else:
                url += 'league/v4/entries/'
            url += queue + '/' + tier + '/' + division

            response = self.apimanager.request_url(url, {'page':page}, ntries=self.ntries)
            if response is None:
                break

            res += response
            page += 1

            # stop when no more players are found or more than max
            findmore = len(response) > 0 and len(res)<=max_players

        return res[:max_players]

    def get_accountid(self, region, summonerid, additional=None):
        """
        Get accountid (+ additional data such as profileiconId if necessary from summonerId)
        """

        url = 'https://' + region + '.api.riotgames.com/lol/summoner/v4/summoners/'
        url += summonerid

        response = self.apimanager.request_url(url)
        if response is None:
            print(summonerid, 'not found')
            return None

        res = {'accountId':response['accountId']}
        if additional:
            for i in additional:
                res[i] = response[i]
        return res

    def get_matchlist_account_timeinfo(self, account_id, region, timeinfo, queue):
        """
        Matchlist by account  + Region
        If timeinfo is None all games, else specify 'beginTime', 'endTime' in timeinfo
        """

        findmore, beginIndex = True, 0
        res = []

        while findmore:
            url = 'https://' + region + '.api.riotgames.com/lol/match/v4/matchlists/by-account/'
            url += account_id

            timeinfo['beginIndex'] = beginIndex
            games = self.apimanager.request_url(url, timeinfo)
            if games is None:
                return res
            res += games['matches']
            beginIndex += 100
            findmore = len(games['matches']) == 100

        return res

    ## FOR NOW WE ASSUME SOMEONE CANNOT PLAY MORE THAN 1 HUNDRED GAMES A WEEK
    def get_matchlist_accountid(self, account_id, region, times=None, queue=420):
        """
        Get matchlist of an account
        Args :
            - account_id (encrypted)
            - timelimit : timestamp(ms) (adapted to region)
        """

        if times is None:
            return self.get_matchlist_account_timeinfo(account_id, region, {}, queue)
        else:
            assert len(times) == 2
            res  = []
            weekly = [i for i in range(times[0], times[1], 24*7*60*60*1000)] + [times[1]]
            for i in range(len(weekly)-1):
                timeinfo = {'beginTime':weekly[i], 'endTime':weekly[i+1]}
                res += self.get_matchlist_account_timeinfo(account_id, region, timeinfo, queue)
            return res

    def get_matchinfo(self, match_id, region):

        url = 'https://' + region + '.api.riotgames.com/lol/match/v4/matches/'
        url += str(match_id)
        response = self.apimanager.request_url(url)
        return response

    def get_matchtimeline(self, match_id, region):

        url = 'https://' + region + '.api.riotgames.com/lol/match/v4/timelines/by-match/'
        url += str(match_id)
        response = self.apimanager.request_url(url)
        return response
