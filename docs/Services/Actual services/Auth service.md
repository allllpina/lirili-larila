# Authorization
'Auth' service is provided for authorization and receiving JSON Web Token
## Dependencies:
```
fastapi[standard]==0.116.1
python-dotenv==1.1.1
pydantic==2.11.7
sqlalchemy[asyncio]==2.0.23
asyncpg==0.30.0
Authlib==1.6.4
passlib[bcrypt]==1.7.4
itsdangerous==2.2.0
python-jose==3.5.0
pydantic-settings==2.10.1
```

## Structure (may be changed)
```
├── config.py
├── Dockerfile
├── main.py
├── models
│   ├── auth_models.py
│   ├── __init__.py
├── routers
│   ├── auth_router.py
│   ├── __init__.py
└── utils
    ├── database.py
    ├── __init__.py
    ├── jwt.py
    ├── oauth.py
    └── pwd_crypt.py
```
## Endpoints
With `NGINX` this service is on `localhost:1313/auth`, e.g. if we want to make [POST] request for `/register`, we must make this request on `localhost:1313/auth/register`
### [POST]/register
Used to register users
#### Requires
```json
{
  "email": "user@example.com",
  "username": "string",
  "password": "string"
}
```
#### Returns
If user is already exists `CODE 409: Conflict`
```json
{
  "detail": "User with this email already exists"
}
```
If succeed `CODE 200`
```json
"<JWT Token>"
```
### [POST] /token
Used to authorize users
#### Requires
```json
{
  "login": "str", // either username or email
  "password": "string"
}
```
#### Returns
If user is not found or wrong login/password `CODE 401: Unauthorized`
```json
{
  "detail": "Invalid credentials"
}
```
If succeed `CODE 200`
```json
"<JWT Token>"
```
### GOOGLE
Endpoints which used to authorize/register via google
#### [GET] /google/login
Used to make user login with his google account returns `/google/callback`
#### [GET] /google/callback
Returned by `/google/login`, contains `<JWT token>`

### [GET] /get_current_user
Used to get users using JWT in HTTP request
#### Requires
```
HTTP request with Authorization Header: Bearer <JWT Token>
```
#### Returns
If expired or wrong token `CODE 401: Unauthorized`
```json
{
  "detail": "Invalid token"
}
```
If succeed `CODE 200`
```json
{
  "email": str,
  "id": int,
  "username": str,
}
```
### [GET] /get_user_by_id
Used to get users using id 
#### Requires
```
HTTP request with Authorization Header: Bearer <JWT Token>
And query param:
localhost:1313/auth/get_user_by_id?user_id=int 
```
#### Returns
If expired or wrong token `CODE 401: Unauthorized`
```json
{
  "detail": "Invalid token"
}
```
Or if none users found `CODE 401: Unauthorized`
```json
{
  "detail": "User not found"
}
```
If succeed `CODE 200`
```json
{
  "email": str,
  "id": int,
  "username": str,
}
```

