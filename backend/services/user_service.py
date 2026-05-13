from datetime import datetime
from backend.database.connection import get_session
from backend.database.models import User, AuditLog
from passlib.hash import bcrypt


class UserService:
    """FR9: Admin CRUD operations for user management."""

    @staticmethod
    def list_users() -> list:
        session = get_session()
        try:
            users = session.query(User).order_by(User.created_at.desc()).all()
            return [u.to_dict() for u in users]
        finally:
            session.close()

    @staticmethod
    def create_user(username: str, email: str, password: str, role: str) -> dict:
        session = get_session()
        try:
            existing = session.query(User).filter(
                (User.email == email) | (User.username == username)
            ).first()
            if existing:
                return {"success": False, "error": "Username or email already exists."}
            user = User(
                username=username.strip(),
                email=email.strip().lower(),
                password_hash=bcrypt.hash(password),
                role=role,
                is_active=True,
            )
            session.add(user)
            session.commit()
            return {"success": True, "user": user.to_dict()}
        except Exception as e:
            session.rollback()
            return {"success": False, "error": str(e)}
        finally:
            session.close()

    @staticmethod
    def update_user(user_id: int, **kwargs) -> dict:
        session = get_session()
        try:
            user = session.query(User).filter(User.id == user_id).first()
            if not user:
                return {"success": False, "error": "User not found."}
            for field in ["role", "is_active", "username", "email"]:
                if field in kwargs:
                    setattr(user, field, kwargs[field])
            if "password" in kwargs and kwargs["password"]:
                user.password_hash = bcrypt.hash(kwargs["password"])
            session.commit()
            return {"success": True, "user": user.to_dict()}
        except Exception as e:
            session.rollback()
            return {"success": False, "error": str(e)}
        finally:
            session.close()

    @staticmethod
    def deactivate_user(user_id: int) -> dict:
        return UserService.update_user(user_id, is_active=False)

    @staticmethod
    def delete_user(user_id: int) -> dict:
        session = get_session()
        try:
            user = session.query(User).filter(User.id == user_id).first()
            if not user:
                return {"success": False, "error": "User not found."}
            session.delete(user)
            session.commit()
            return {"success": True}
        except Exception as e:
            session.rollback()
            return {"success": False, "error": str(e)}
        finally:
            session.close()

    @staticmethod
    def get_audit_logs(limit: int = 200) -> list:
        session = get_session()
        try:
            logs = session.query(AuditLog).order_by(AuditLog.timestamp.desc()).limit(limit).all()
            return [l.to_dict() for l in logs]
        finally:
            session.close()
