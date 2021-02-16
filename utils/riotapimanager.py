import requests
import json
import time
import collections

from typing import Optional

OFFSET = 2 # security to avoid error 429
BYPASS_FIRST_WAIT = False

# test url to initialize reset queue (we have to make a random request to get info)
test_url = 'https://jp1.api.riotgames.com/lol/league/v4/challengerleagues/by-queue/RANKED_SOLO_5x5'

class ApiError(Exception):
    pass

class ApiErrorTime(ApiError):
    pass

class ApiErrorUrl(ApiError):
    pass

class ApiErrorServer(ApiError):
    pass

class ApiError404(ApiErrorUrl):
    pass

class RiotApiClient(object):
    """
    Class for interacting with the riot api : it will handle requests
    """

    def __init__(
        self,
        api_key: str,
        freshapi: Optional[bool] = False,
        verbose: Optional[bool] = False
    ):

        self.api_key = api_key
        self.resets = {}
        self.verbose = verbose
        self.initialize_resetqueue(freshapi)

    def initialize_resetqueue(
        self,
        freshapi: bool
    ):

        """ creates the queue for managing rate-limit"""

        url = test_url + '?api_key=' + self.api_key
        resp = requests.get(url)
        if resp.status_code != 200:
            print('Problem initializing API Manager')
            print('Status code :', resp.status_code)
            return None

        # If we do not bypass this, we wait for a full cycle of API
        # This ensures we have a "fresh" API and the reset queue can be initialized to empty
        wait = 0
        if not freshapi:
            for r in resp.headers['X-App-Rate-Limit-Count'].split(','):
                [c, t] = list(map(int, r.split(':')))
                wait = max(wait, t) if c > 1 else wait

            if wait > 0:
                if self.verbose:
                    print('Waiting to reinitialise api for : ', wait)
                time.sleep(wait)

        # create reset queue
        for r in resp.headers['X-App-Rate-Limit'].split(','):
                [l, t] = list(map(int, r.split(':')))
                self.resets[t] = collections.deque(l * [0], l)

    def request_url(
        self,
        url: str,
        params: Optional[dict] = None,
        ntries: Optional[int] = 3
    ):
        """
        Request an url with additional params in a robust way
        (we wait and try again if we hit an error429)

        Args :
            - url : string
            - params : dict
            - ntries : int (numbers of tries)

        Return :
        A json with the response, or an APIError
        """

        tries = 0
        while tries<ntries:
            tries += 1
            try:
                response = self.request_url_once(url, params)
                return response

            # Server error -> stop for now
            except ApiErrorServer as e:
                if self.verbose:
                    print(time.strftime('%Y-%m-%d %H:%M:%S'), e)
                return None

            # Url error -> stop for now
            except ApiErrorUrl as e:
                if self.verbose:
                    print(time.strftime('%Y-%m-%d %H:%M:%S'), e)
                return None

            # Time error -> we try again after waiting
            except ApiErrorTime as e:
                if self.verbose:
                    print(time.strftime('%Y-%m-%d %H:%M:%S'), e)
                continue

    def request_url_once(self, url, params=None):
        """
        Request an url once (with additional params)

        Args :
            - url : string
            - params : dict

        Return :
        A json with the response, or an APIError
        """

        # for all rates we check in queue if we need to wait
        for t in self.resets:
            wait = self.resets[t][0] + t + OFFSET - time.time()

        # Request and response
        resp = requests.get(url, headers={"X-Riot-Token": self.api_key}, params=params)

        # update reset state with time of current request
        for t in self.resets:
            self.resets[t].append(time.time())

        # 200 response code : json guarenteed
        if resp.status_code == 200:
            return json.loads(resp.content.decode('utf-8'))
        else:
            if self.verbose:
                print(url)
            self.manage_badrequest(resp.status_code)

    def manage_badrequest(self, status_code):

        # Problem in the url
        if status_code == 400:
            raise ApiErrorUrl('Bad Request : syntax error in provided url')
        elif status_code == 401:
            raise ApiErrorUrl('Unauthorized : missing API key')
        elif status_code == 403:
            raise ApiErrorUrl('Forbidden : invalid API key')
        elif status_code == 404:
            raise ApiError404('Not Found : server has not found match for request')

        # Hit rate limit : should not happen with reset queue
        # it still sometimes happens, to investigate
        # currently wait a full minute to avoid problems
        elif status_code == 429:
            time.sleep(60)
            raise ApiErrorTime('Rate Limit Exceeded : please wait')

        # Problem on server side
        elif status_code == 500:
            raise ApiErrorServer('Internal server error')
        elif status_code == 503:
            raise ApiErrorServer('Service Unavailable')

        # a response code not in the Riot doc
        else:
            raise ApiErrorUrl('Undocumented error')
