import streamlit as st
from datetime import datetime
from passlib.hash import bcrypt
from backend.database.connection import get_session
from backend.database.models import User, AuditLog


class AuthManager:

    @staticmethod
    def register(username: str, email: str, password: str, role: str = "website_user") -> dict:
        session = get_session()
        try:
            existing = session.query(User).filter(
                (User.email == email) | (User.username == username)
            ).first()
            if existing:
                return {"success": False, "error": "User with this email or username already exists."}

            user = User(
                username=username.strip(),
                email=email.strip().lower(),
                password_hash=bcrypt.hash(password),
                role=role,
                is_active=True,
            )
            session.add(user)
            session.commit()
            session.refresh(user)
            session.add(AuditLog(user_id=user.id, username=username, action="REGISTER",
                                 details=f"Role: {role}"))
            session.commit()
            return {"success": True, "user": user.to_dict()}
        except Exception as e:
            session.rollback()
            return {"success": False, "error": str(e)}
        finally:
            session.close()

    @staticmethod
    def login(email: str, password: str) -> dict:
        session = get_session()
        try:
            user = session.query(User).filter(
                User.email == email.strip().lower(),
                User.is_active == True,
            ).first()
            if not user or not bcrypt.verify(password, user.password_hash):
                return {"success": False, "error": "Invalid email or password."}
            user.last_login = datetime.now()
            session.add(AuditLog(user_id=user.id, username=user.username,
                                 action="LOGIN", details="Successful login"))
            session.commit()
            return {"success": True, "user": user.to_dict()}
        except Exception as e:
            session.rollback()
            return {"success": False, "error": str(e)}
        finally:
            session.close()

    @staticmethod
    def logout():
        user = st.session_state.get("user", {})
        if user:
            session = get_session()
            try:
                session.add(AuditLog(user_id=user.get("id"), username=user.get("username"),
                                     action="LOGOUT", details="User logged out"))
                session.commit()
            finally:
                session.close()
        for key in ["user", "authenticated"]:
            st.session_state.pop(key, None)

    @staticmethod
    def is_authenticated() -> bool:
        return st.session_state.get("authenticated", False)

    @staticmethod
    def get_current_user() -> dict:
        return st.session_state.get("user", {})

    @staticmethod
    def require_auth(allowed_roles: list = None):
        if not st.session_state.get("authenticated", False):
            st.switch_page("pages/00_Auth.py")
            st.stop()
        user = st.session_state.get("user", {})
        if allowed_roles and user.get("role") not in allowed_roles:
            st.error("Access denied. You don't have permission to view this page.")
            st.stop()
        return user
