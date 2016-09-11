# Poloniex API wrapper tested on Python 2.7.6 & 3.4.3
# https://github.com/s4w3d0ff/python-poloniex
# BTC: 15D8VaZco22GTLVrFMAehXyif6EGf8GMYV
# TODO:
#   [x] PEP8
#   [ ] Add better logger access
#   [ ] Find out if request module has the equivalent to urlencode
#   [ ] Add Push Api application wrapper
#   [ ] Convert docstrings to sphinx
#
#    Copyright (C) 2016  https://github.com/s4w3d0ff
#
#    This program is free software; you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation; either version 2 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License along
#    with this program; if not, write to the Free Software Foundation, Inc.,
#    51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.
import sys
import time
import calendar
import logging
import json
import hmac
import hashlib
# pip
import requests

if sys.version_info[0] is 3:
    from urllib.parse import urlencode
else:
    from urllib import urlencode

# Possible Commands
PUBLIC_COMMANDS = [
    'returnTicker',
    'return24hVolume',
    'returnOrderBook',
    'returnTradeHistory',
    'returnChartData',
    'returnCurrencies',
    'returnLoanOrders']

PRIVATE_COMMANDS = [
    'returnBalances',
    'returnCompleteBalances',
    'returnDepositAddresses',
    'generateNewAddress',
    'returnDepositsWithdrawals',
    'returnOpenOrders',
    'returnTradeHistory',
    'returnAvailableAccountBalances',
    'returnTradableBalances',
    'returnOpenLoanOffers',
    'returnOrderTrades',
    'returnActiveLoans',
    'createLoanOffer',
    'cancelLoanOffer',
    'toggleAutoRenew',
    'buy',
    'sell',
    'cancelOrder',
    'moveOrder',
    'withdraw',
    'returnFeeInfo',
    'transferBalance',
    'returnMarginAccountSummary',
    'marginBuy',
    'marginSell',
    'getMarginPosition',
    'closeMarginPosition']


class Poloniex(object):
    """The Poloniex Object!"""
    def __init__(
            self, APIKey=False, Secret=False,
            timeout=3, coach=False, loglevel=logging.WARNING):
        """
        APIKey = str api key supplied by Poloniex
        Secret = str secret hash supplied by Poloniex
        timeout = int time in sec to wait for an api response
            (otherwise 'requests.exceptions.Timeout' is raised)
        coach = bool to indicate if the api coach should be used
        loglevel = logging level object to set the module at
            (changes the requests module as well)

        self.apiCoach = object that regulates spacing between api calls

        # Time Placeholders # (MONTH == 30*DAYS)

        self.MINUTE, self.HOUR, self.DAY, self.WEEK, self.MONTH, self.YEAR
        """
        # Set wrapper logging level
        logging.basicConfig(
                format='[%(asctime)s] %(message)s',
                datefmt="%H:%M:%S",
                level=loglevel)
        # Suppress the requests	module logging output
        logging.getLogger("requests").setLevel(loglevel)
        logging.getLogger("urllib3").setLevel(loglevel)
        # Call coach, set nonce
        self.apiCoach, self.nonce = [Coach(), int(time.time()*1000)]
        # Grab keys, set timeout, ditch coach?
        self.APIKey, self.Secret, self.timeout, self._coaching = \
            [APIKey, Secret, timeout, coach]
        # Set time labels
        self.MINUTE, self.HOUR, self.DAY, self.WEEK, self.MONTH, self.YEAR = \
            [60, 60*60, 60*60*24, 60*60*24*7, 60*60*24*30, 60*60*24*365]

    # -----------------Meat and Potatos---------------------------------------
    def api(self, command, args={}):
        """
        Main Api Function
        - encodes and sends <command> with optional [args] to Poloniex api
        - raises 'ValueError' if an api key or secret is missing
            (and the command is 'private'), or if the <command> is not valid
        - returns decoded json api message
        """
        global PUBLIC_COMMANDS, PRIVATE_COMMANDS

        # check in with the coach
        if self._coaching:
            self.apiCoach.wait()

        # pass the command
        args['command'] = command

        # private?
        if command in PRIVATE_COMMANDS:
            # check for keys
            if not self.APIKey or not self.Secret:
                raise ValueError("APIKey and Secret needed!")
            # set nonce
            args['nonce'] = self.nonce

            try:
                # encode arguments for url
                postData = urlencode(args)
                # sign postData with our Secret
                sign = hmac.new(
                        self.Secret.encode('utf-8'),
                        postData.encode('utf-8'),
                        hashlib.sha512)
                # post request
                ret = requests.post(
                        'https://poloniex.com/tradingApi',
                        data=args,
                        headers={
                            'Sign': sign.hexdigest(),
                            'Key': self.APIKey
                            },
                        timeout=self.timeout)
                # return decoded json
                return json.loads(ret.text)

            except Exception as e:
                raise e

            finally:
                # increment nonce(no matter what)
                self.nonce += 1

        # public?
        elif command in PUBLIC_COMMANDS:
            try:
                ret = requests.post(
                        'https://poloniex.com/public?' + urlencode(args),
                        timeout=self.timeout)
                return json.loads(ret.text)
            except Exception as e:
                raise e
        else:
            raise ValueError("Invalid Command!")

    def publicTradeHist(self, pair, start=False, end=time.time()):
        """
        Returns public trade history for <pair>
        starting at <start> and ending at [end=time.time()]
        """
        if self._coaching:
            self.apiCoach.wait()
        if not start:
            start = time.time()-self.HOUR
        try:
            ret = requests.post(
                    'https://poloniex.com/public?'+urlencode({
                        'command': 'returnTradeHistory',
                        'currencyPair': str(pair),
                        'start': str(start),
                        'end': str(end)
                        }),
                    timeout=self.timeout)
            return json.loads(ret.text)
        except Exception as e:
            raise e

class Coach(object):
    """
    Coaches the api wrapper, makes sure it doesn't get all hyped up on Mt.Dew
    Poloniex default call limit is 6 calls per 1 sec.
    """
    def __init__(self, timeFrame=1.0, callLimit=6):
        """
        timeFrame = float time in secs [default = 1.0]
        callLimit = int max amount of calls per 'timeFrame' [default = 6]
        """
        self._timeFrame, self._callLimit = [timeFrame, callLimit]
        self._timeBook = []

    def wait(self):
        """ Makes sure our api calls don't go past the api call limit """
        # what time is it?
        now = time.time()
        # if it's our turn
        if len(self._timeBook) is 0 or \
                (now - self._timeBook[-1]) >= self._timeFrame:
            # add 'now' to the front of 'timeBook', pushing other times back
            self._timeBook.insert(0, now)
            logging.info(
                "Now: %d  Oldest Call: %d  Diff: %f sec" %
                (now, self._timeBook[-1], now - self._timeBook[-1])
                )
            # 'timeBook' list is longer than 'callLimit'?
            if len(self._timeBook) > self._callLimit:
                # remove the oldest time
                self._timeBook.pop()
        else:
            logging.info(
                "Now: %d  Oldest Call: %d  Diff: %f sec" %
                (now, self._timeBook[-1], now - self._timeBook[-1])
                )
            logging.info(
                "Waiting %s sec..." %
                str(self._timeFrame-(now - self._timeBook[-1]))
                )
            # wait your turn (maxTime - (now - oldest)) = time left to wait
            time.sleep(self._timeFrame-(now - self._timeBook[-1]))
            # add 'now' to the front of 'timeBook', pushing other times back
            self._timeBook.insert(0, time.time())
            # 'timeBook' list is longer than 'callLimit'?
            if len(self._timeBook) > self._callLimit:
                # remove the oldest time
                self._timeBook.pop()
