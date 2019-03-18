# EsiPysi

EsiPysi (pronounced like "Easy Peasy") is a utility for accessing the Eve api called Esi.  The goal of this project is 
to create a lightweight and fast tool which makes devloping with Esi easier.

## Features

* Auth storage and auto refreshing
    * If your access token expires, EsiPysi will acquire a new one
* Fast API calling and JSON parsing using [aiohttp](https://aiohttp.readthedocs.io/en/stable/)
    * Uses asyncio and event loops so that the API calls are non-blocking
* Light input validation
    *  Only validates that the parameters are in the Esi Swagger Spec, does not validate types/values
* Caching using Redis
* Automatic retries for certain error codes
    * Typically those pesky 501s

## Install

Install with pip:

```
pip install EsiPysi
```

Requires python 3.5+

## How to use

Get familliar with the [ESI reference](https://esi.evetech.net/latest/#/) and [Eve SSO](http://eveonline-third-party-documentation.readthedocs.io/en/latest/sso/authentication.html)

start with an EsiPysi object, this will keep track of global settings like which Esi version to use (_latest is reccomended)

```python
from esipysi import EsiPysi

esi = EsiPysi("https://esi.evetech.net/_latest/swagger.json?datasource=tranquility", user_agent="Your User Agent Here")
```

Now from that object you can create operations, pass the operation ID to the get_operation function

```python
op = await esi.get_operation("get_search")
```

If it requires authorization you can use EsiAuth

You can either get one from your client info, access token, refresh token, and expire datetime (in UTC)
```python
from esipysi import EsiAuth

auth = EsiAuth(CLIENT_ID, CLIENT_SECRET, ACCESS_TOKEN, REFRESH_TOKEN, EXPIRES_AT)
op.set_auth(auth)
```

Or you can get it from less data such as an authorization code you got back from the callback or just a refresh token:
```python
from esipysi import EsiAuth

auth = await EsiAuth.from_authorization_code(CLIENT_ID, CLIENT_SECRET, AUTHORIZATION_CODE)
auth = await EsiAuth.from_refresh_token(CLIENT_ID, CLIENT_SECRET, REFRESH_TOKEN)
op.set_auth(auth)
```

And then you can execute that operation with parameters

```python
result = await op.execute(categories="character", search="Flying Kiwi Sertan")
```

### Response Object

EsiPysi returns a response object called EsiResponse, it contains the following:

* `response.text` - The plain text of the body of the response
* `resonse.json()` - The text decoded as json into a python Dict
* `response.status` - The HTTP status code (likely 200)
* `response.headers` - a [CIMultiDict](https://multidict.readthedocs.io/en/stable/multidict.html#cimultidict) which is a special dict cabable of holding multiple of the same key because headers are funky.  They act just like a `Dict` with some extras.

### Caching

EsiPysi has caching provided by redis.  First create a redis client.

Example from [redis-py](https://github.com/andymccurdy/redis-py)

```python
import redis
r = redis.StrictRedis(host='localhost', port=6379, db=0)
```

Now create a RedisCache object and pass it to the EsiPysi object

```python
from esipysy import EsiPysi
from esipysy.cache import RedisCache
cache = RedisCache(r)
esi = EsiPysi("https://esi.evetech.net/_latest/swagger.json?datasource=tranquility", user_agent="Your User Agent Here", cache=cache)
```