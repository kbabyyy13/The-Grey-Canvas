import os
import uuid
from functools import wraps
from urllib.parse import urlencode

import jwt
import requests
from flask import g, redirect, render_template, request, session, url_for
from flask_dance.consumer import (
    OAuth2ConsumerBlueprint,
    oauth_authorized,
    oauth_error,
)
from flask_dance.consumer.storage import BaseStorage
from flask_login import LoginManager, current_user, login_user, logout_user
from jwt import PyJWKClient
from oauthlib.oauth2.rfc6749.errors import InvalidGrantError
from sqlalchemy.exc import NoResultFound
from werkzeug.local import LocalProxy

from app import app, db
from models import OAuth, User

# Cache for JWK clients
_jwk_clients = {}

login_manager = LoginManager(app)
login_manager.login_view = "replit_auth.login"
login_manager.login_message = "Please log in to access the admin panel."


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(user_id)


class UserSessionStorage(BaseStorage):

    def get(self, blueprint):
        try:
            token = (
                db.session.query(OAuth)
                .filter_by(
                    user_id=current_user.get_id(),
                    browser_session_key=g.browser_session_key,
                    provider=blueprint.name,
                )
                .one()
                .token
            )
        except NoResultFound:
            token = None
        return token

    def set(self, blueprint, token):
        db.session.query(OAuth).filter_by(
            user_id=current_user.get_id(),
            browser_session_key=g.browser_session_key,
            provider=blueprint.name,
        ).delete()
        new_model = OAuth()
        new_model.user_id = current_user.get_id()
        new_model.browser_session_key = g.browser_session_key
        new_model.provider = blueprint.name
        new_model.token = token
        db.session.add(new_model)
        db.session.commit()

    def delete(self, blueprint):
        db.session.query(OAuth).filter_by(
            user_id=current_user.get_id(),
            browser_session_key=g.browser_session_key,
            provider=blueprint.name,
        ).delete()
        db.session.commit()


def make_replit_blueprint():
    try:
        repl_id = os.environ["REPL_ID"]
    except KeyError:
        raise SystemExit("the REPL_ID environment variable must be set")

    issuer_url = os.environ.get("ISSUER_URL", "https://replit.com/oidc")

    replit_bp = OAuth2ConsumerBlueprint(
        "replit_auth",
        __name__,
        client_id=repl_id,
        client_secret=None,
        base_url=issuer_url,
        authorization_url_params={
            "prompt": "login consent",
        },
        token_url=issuer_url + "/token",
        token_url_params={
            "auth": (),
            "include_client_id": True,
        },
        auto_refresh_url=issuer_url + "/token",
        auto_refresh_kwargs={
            "client_id": repl_id,
        },
        authorization_url=issuer_url + "/auth",
        use_pkce=True,
        code_challenge_method="S256",
        scope=["openid", "profile", "email", "offline_access"],
        storage=UserSessionStorage(),
    )

    @replit_bp.before_app_request
    def set_applocal_session():
        if "_browser_session_key" not in session:
            session["_browser_session_key"] = uuid.uuid4().hex
        session.modified = True
        g.browser_session_key = session["_browser_session_key"]
        g.flask_dance_replit = replit_bp.session

    @replit_bp.route("/logout")
    def logout():
        del replit_bp.token
        logout_user()

        end_session_endpoint = issuer_url + "/session/end"
        encoded_params = urlencode(
            {
                "client_id": repl_id,
                "post_logout_redirect_uri": request.url_root,
            }
        )
        logout_url = f"{end_session_endpoint}?{encoded_params}"

        return redirect(logout_url)

    @replit_bp.route("/error")
    def error():
        return render_template("auth_error.html"), 403

    return replit_bp


def save_user(user_claims):
    user = User()
    user.id = user_claims["sub"]
    user.email = user_claims.get("email")
    user.first_name = user_claims.get("first_name")
    user.last_name = user_claims.get("last_name")
    user.profile_image_url = user_claims.get("profile_image_url")
    merged_user = db.session.merge(user)
    db.session.commit()
    return merged_user


@oauth_authorized.connect
def logged_in(blueprint, token):
    try:
        # Get issuer URL for OIDC verification
        issuer_url = os.environ.get("ISSUER_URL", "https://replit.com/oidc")

        # Get or create JWK client for this issuer
        if issuer_url not in _jwk_clients:
            # Fetch OIDC configuration to get JWKS URI
            config_response = requests.get(
                f"{issuer_url}/.well-known/openid-configuration", timeout=10
            )
            config_response.raise_for_status()
            config = config_response.json()

            # Create JWK client
            _jwk_clients[issuer_url] = PyJWKClient(config["jwks_uri"])

        jwk_client = _jwk_clients[issuer_url]

        # Get the signing key for the JWT
        signing_key = jwk_client.get_signing_key_from_jwt(token["id_token"])

        # Verify the JWT signature and claims
        user_claims = jwt.decode(
            token["id_token"],
            signing_key.key,
            algorithms=["RS256"],
            audience=os.environ.get("REPL_ID"),
            issuer=issuer_url,
            options={"verify_signature": True},
        )
    except jwt.InvalidTokenError as e:
        # Log the error and redirect to error page
        app.logger.error(f"JWT verification failed: {e}")
        return redirect(url_for("replit_auth.error"))
    except Exception as e:
        # Handle other errors (network issues, etc.)
        app.logger.error(f"JWT verification error: {e}")
        return redirect(url_for("replit_auth.error"))

    user = save_user(user_claims)
    login_user(user)
    blueprint.token = token
    next_url = session.pop("next_url", None)
    if next_url is not None:
        return redirect(next_url)


@oauth_error.connect
def handle_error(blueprint, error, error_description=None, error_uri=None):
    return redirect(url_for("replit_auth.error"))


def require_login(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            session["next_url"] = get_next_navigation_url(request)
            return redirect(url_for("replit_auth.login"))

        # Check if token is expired and refresh if needed
        if hasattr(g, "flask_dance_replit") and g.flask_dance_replit.token:
            expires_in = g.flask_dance_replit.token.get("expires_in", 0)
            if expires_in < 0:
                refresh_token_url = (
                    os.environ.get("ISSUER_URL", "https://replit.com/oidc") + "/token"
                )
                try:
                    token = g.flask_dance_replit.refresh_token(
                        token_url=refresh_token_url, client_id=os.environ["REPL_ID"]
                    )
                    g.flask_dance_replit.token = token
                except InvalidGrantError:
                    # If the refresh token is invalid, the user needs to re-login
                    session["next_url"] = get_next_navigation_url(request)
                    return redirect(url_for("replit_auth.login"))

        return f(*args, **kwargs)

    return decorated_function


def get_next_navigation_url(request):
    is_navigation_url = (
        request.headers.get("Sec-Fetch-Mode") == "navigate"
        and request.headers.get("Sec-Fetch-Dest") == "document"
    )
    if is_navigation_url:
        return request.url
    return request.referrer or request.url


replit = LocalProxy(lambda: g.flask_dance_replit)
