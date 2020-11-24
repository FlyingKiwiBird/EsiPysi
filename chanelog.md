### 0.10.3
- Changed Redis expiration to EXPIREAT to avoid potential expiration issues
- Cache will no longer store keys without an expiration date (could have happened on an error when parsing exipry date from ESI)
- EsiResponses will now be returned even if they result in a HTTP status that is in the 400 block (not found, not authorized, etc.).  Old behavior can be achieved by setting the optional argument `esi_400_codes_throw` to `True`

### 0.10.2
- Fix some dependency issues

### 0.10.1
- Added a basic cache called `DictCache` which uses a simple python dictionary to store cached items
- `DictCache` will be used by default if no other cache (or `None`) is specified
- EsiResponse now includes the calling information `operation_id` and `operation_parameters` as well as a helper function `expires()` which returns a datetime of when the ESI cache expires

### 0.9.2
- Added EsiSession, that allows a single EsiPysi object to be active for the duration of the application which can spawn multiple short-lived sessions

### 0.9.1
- Added `with` pattern to EsiPysi

### 0.9.0
- Changed to start/stop session for more control over aiohttp sessions
- Fixed a bug with `asyncio.run()`
- Deprecated everything but `op.execute()`

### 0.8.4
- Errors should now be handled better (better logging)

### 0.8.3
- FIXED: Close also closes the connector now 

### 0.8.2
- FIXED: Bug with setting an event loop caused mismatch between session & connector for AIOHttp

### 0.8.1
- Each client now spawns 1 session which is used for every call of that client
- Sessions have 50 max connections to avoid problem of windows running out of file descriptors

### 0.7.0
- Moved from different response types to a simple response object which contains the data, headers, status, and url
- The object will also parse data into json

### 0.6.1
- Fixed a caching issue due to pickling of a "futures" object

### 0.6.0
- Added automatic retry

### pre-version 0.6.0
- Not tracked