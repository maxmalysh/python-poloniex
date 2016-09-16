#**An API wrapper for Poloniex.com written in Python (MINIMAL BRANCH)**
#####poloniex.py - _Tested on Python 2.7.6 & 3.4.3_
Inspired by [this](http://pastebin.com/8fBVpjaj) wrapper written by 'oipminer'

###Features:
- Poloniex object **only has the `Poloniex.api()` method, this is the minimal version!**
- ApiKey and Secret are optional if used for just public commands.
- Raises `ValueError` if the command supplied does not exist or if the api keys are not defined
- The `poloniex.Poloniex()` object has an optional 'timeout' attribute/arg that adjusts the number of seconds to wait for a response from polo (default = 3 sec)
- Optional api 'coach' can restrict the amount of calls per sec, keeping your api calls (that aren't threaded) under the limit (6 calls per sec). Activate the coach using `poloniex.Poloniex(coach=True)` when creating the polo object or by defining `polo._coaching = True`.

You like?!
```
CGA: aZ1yHGx4nA64aWMDNQKXJrojso7gfQ1J5P
BTC: 15D8VaZco22GTLVrFMAehXyif6EGf8GMYV
LTC: LakbntAYrwpVSnLWj1fCLttVzpiDXDa5JV
DOGE: DAQjkQNbhpUoQw7KHAGkDYZ3yySKi751dd
```
