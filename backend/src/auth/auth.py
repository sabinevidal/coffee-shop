import json
from flask import request, _request_ctx_stack
from functools import wraps
from jose import jwt
from urllib.request import urlopen


AUTH0_DOMAIN = 'coffee-shop-app.eu.auth0.com'
ALGORITHMS = ['RS256']
API_AUDIENCE = 'http://coffee-shop-app'

## AuthError Exception
'''
AuthError Exception
A standardized way to communicate auth failure modes
'''
class AuthError(Exception):
    def __init__(self, error, status_code):
        self.error = error
        self.status_code = status_code

# --------------------------------
# Auth Header
# --------------------------------

## Get Access Token from Authorization Header

def get_token_auth_header(): 
    # get auth from header and verify auth exists
    auth = request.headers.get('Authorization', None)
    if not auth:
        raise AuthError({
            'code': 'authorization_header_missing',
            'description': 'Authorization header is expected.'
        }, 401)
    
    # split keyword and token
    parts = auth.split()

    #verify keyword is 'bearer', error if not
    if parts[0].lower() != 'bearer':
        raise AuthError({
            'code': 'invalid_header',
            'description': 'Authorization header must start with "bearer".'
        }, 401)

    # auth header must have 2 parts
    elif len(parts) == 1:
        raise AuthError({
            'code': 'invalid_header',
            'description': 'Token not found.'
        }, 401)

    elif len(parts) > 2:
        raise AuthError({
            'code': 'invalid_header',
            'description': 'Authorization header must be bearer token.'
        }, 401)
    
    # get token from parts and return
    token = parts[1]
    return token

## Verify user permissions

def check_permissions(permission, payload):

    # verify permissions included in JWT
    if 'permissions' not in payload:
        raise AuthError({
            'code': 'invalid_claims',
            'description': 'Permission not included in JWT.'
        }, 401)

    # verify user permissions from payload contain permission for route
    if permission not in payload['permissions']:
        raise AuthError({
            'code': 'unauthorized',
            'description': 'Permission not found.'
        }, 401)

    # return True if no AuthErrors
    return True

## Validate and decode Auth) JWTs

def verify_decode_jwt(token):

    # get public key from Auth0
    jsonurl = urlopen(f'https://{AUTH0_DOMAIN}/.well-known/jwks.json')
    jwks = json.loads(jsonurl.read())

    # TODO: where does get_unverified come from?
    unverified_header = jwt.get_unverified_header(token)

    # choose rsa key
    rsa_key = {}

    # validate token header contains kid
    if 'kid' not in unverified_header:
        raise AuthError({
            'code': 'invalid_header',
            'description': 'Authorization invalid.'
        }, 401)
    
    # build rsa key if kid match
    for key in jwks['keys']:
        if key['kid'] == unverified_header['kid']:
            rsa_key = {
                'kty': key['kty'],
                'kid': key['kid'],
                'use': key['use'],
                'n': key['n'],
                'e': key['e']
            }
    
    # validate the token
    if rsa_key:
        try:
            payload = jwt.decode(
                token,
                rsa_key,
                algorithms=ALGORITHMS,
                audience=API_AUDIENCE,
                issuer='https://' + AUTH0_DOMAIN + '/'
            )
        
            return payload
        
        # catch common errors
        except jwt.ExpiredSignatureError:
            raise AuthError({
                'code': 'token_expired',
                'description': 'Token expired.'
            }, 401)

        except jwt.JWTClaimsError:
            raise AuthError({
                'code': 'invalid_claims',
                'description': 'Incorrect claims. Please, check the audience and issuer.'
            }, 401)

        except Exception:
            raise AuthError({
                'code': 'invalid_header',
                'description': 'Unable to parse authentication token.'
            }, 400)

    raise AuthError({
        'code': 'invalid_header',
        'description': 'Unable to find the appropriate key.'
    }, 400)

## Decorator function to add authorization to endpoints
def requires_auth(permission=''):
    def requires_auth_decorator(f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            # get token from header 
            token = get_token_auth_header()
            # decode and validate token, else raise AuthError
            try:
                payload = verify_decode_jwt(token)
            except:
                raise AuthError({
                    'code': 'invalid_token',
                    'description': 'Access denied due to invalid token'
                }, 401)

            check_permissions(permission, payload)
            return f(payload, *args, **kwargs)

        return wrapper
    return requires_auth_decorator
