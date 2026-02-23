import logging
from app import db, bcrypt
from app.models import User
from flask_login import login_user, logout_user

logger = logging.getLogger(__name__)


class AuthService:
    @staticmethod
    def register_user(username, email, password):
        """
        Handle user registration business logic.
        """
        try:
            hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')
            user = User(
                username=username.lower(),
                email=email.lower(),
                password_hash=hashed_password
            )
            db.session.add(user)
            db.session.commit()
            return user
        except Exception:
            db.session.rollback()
            logger.exception("Failed to register user %s", email)
            raise

    @staticmethod
    def authenticate_user(email, password, remember=False):
        """
        Handle user login business logic.
        """
        user = User.query.filter_by(email=email.lower()).first()
        if user and bcrypt.check_password_hash(user.password_hash, password):
            login_user(user, remember=remember)
            return user
        return None

    @staticmethod
    def logout_user():
        """
        Handle user logout business logic.
        """
        logout_user()

