from .riotapimanager import RiotApiClient
from typing import Optional

class Riot_API(object):
    """
    Class for getting information from riot api
    """

    def __init__(
        self,
        api_key: str,
        freshapi: Optional[bool] = False,
        ntries: Optional[int] = 3,
        verbose: Optional[bool] = False
    ):

        self.apimanager = RiotApiClient(api_key, freshapi, verbose)
        self.ntries = ntries

    def get_players_division(
        self,
        region: str,
        queue: str,
        tier: str,
        division: str,
        max_players: int):

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

    def get_accountid(
        self,
        region: str,
        summonerid: str,
        additional: Optional[list] = None
    ):
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

    def get_matchlist_account_timeinfo(
        self,
        account_id: str,
        region: str,
        queue: int,
        timeinfo: Optional[dict] = None,
    ):
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
    def get_matchlist_accountid(
        self,
        account_id: str,
        region: str,
        queue: Optional[int] = 420,
        times: Optional[list] = None,
    ):
        """
        Get matchlist of an account
        Args :
            - account_id (encrypted)
            - times: list of two timestamp for begin/end in ms (adapted to region)
        """

        if times is None:
            return self.get_matchlist_account_timeinfo(account_id, region, queue, {})
        else:
            assert len(times) == 2
            res  = []
            weekly = [i for i in range(times[0], times[1], 24*7*60*60*1000)] + [times[1]]
            for i in range(len(weekly)-1):
                timeinfo = {'beginTime':weekly[i], 'endTime':weekly[i+1]}
                res += self.get_matchlist_account_timeinfo(account_id, region, queue, timeinfo)
            return res

    def get_matchinfo(
        self,
        match_id: int,
        region: str
    ):
        """ Get information on a specific match """

        url = 'https://' + region + '.api.riotgames.com/lol/match/v4/matches/'
        url += str(match_id)
        response = self.apimanager.request_url(url)
        return response

    def get_matchtimeline(
        self,
        match_id: int,
        region: str
    ):
        """ Get timeline of a specific match """

        url = 'https://' + region + '.api.riotgames.com/lol/match/v4/timelines/by-match/'
        url += str(match_id)
        response = self.apimanager.request_url(url)
        return response
