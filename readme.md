# EsiPysi

EsiPysi (pronounced like "Easy Peasy") is a utility for accessing the Eve api called Esi.  The goal of this project is 
to create a lightweight and fast tool which makes devloping with Esi easier.

## Features

* Auth storage and auto refreshing
    * If your access token expires, EsiPysi will acquire a new one
* Fast API calling and JSON parsing using [requests](https://github.com/requests/requests)
    * Uses the popular requests package for calling APIs and parsing the JSON response
* Light input validation
    *  Only validates that the parameters are in the Esi Swagger Spec, does not validate types/values

## How to use

start with an EsiPysi object, this will keep track of global settings like which Esi version to use (_latest is reccomended)

```python
esi = EsiPysi("https://esi.tech.ccp.is/_latest/swagger.json?datasource=tranquility", user_agent="Your User Agent Here")
```

Now from that object you can create operations, for more info on avaliable operations see [CCP's documentation](https://esi.tech.ccp.is/latest/)

```python
op = esi.get_operation("get_search")
```

If it requires authorization you can use EsiAuth

```python
auth = EsiAuth(CLIENT_ID, CLIENT_SECRET, ACCESS_TOKEN, REFRESH_TOKEN, EXPIRES_AT)
op.set_auth(auth)
```

And then you can execute that operation with parameters

```python
result = op.execute({"categories" : "character", "search" : "Flying Kiwi Bird"})
```
