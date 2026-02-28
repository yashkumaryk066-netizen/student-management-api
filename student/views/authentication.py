from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.authentication import get_authorization_header
from rest_framework.exceptions import AuthenticationFailed

class QueryParameterTokenAuthentication(JWTAuthentication):
    """
    Clients can authenticate by passing the token key in the "token" query parameter.
    """
    def authenticate(self, request):
        # 1. Check for Query Parameter "token"
        raw_token = request.query_params.get('token')
        
        # 2. If not found, fall back to standard Header checks (Optional, but good for hybrid use)
        # But since we are likely chaining this with default JWTAuthentication, we can return None here
        # if no query param is found, allowing the next class to try.
        if not raw_token:
            return None

        try:
            validated_token = self.get_validated_token(raw_token)
            return self.get_user(validated_token), validated_token
        except Exception as e:
            # If a token was provided but is invalid, we might want to return None 
            # to let other authenticators try, or raise AuthenticationFailed.
            # Usually if a specific credential is provided and fails, we should fail.
            raise AuthenticationFailed(str(e))
