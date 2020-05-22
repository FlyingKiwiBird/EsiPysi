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