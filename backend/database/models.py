from sqlalchemy import Column, Integer, String, DateTime, Boolean, Text
from sqlalchemy.orm import declarative_base
from sqlalchemy.sql import func

Base = declarative_base()


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String(50), unique=True, nullable=False)
    email = Column(String(100), unique=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    role = Column(String(20), default="website_user", nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, server_default=func.now())
    last_login = Column(DateTime, nullable=True)

    def to_dict(self):
        return {
            "id": self.id,
            "username": self.username,
            "email": self.email,
            "role": self.role,
            "is_active": self.is_active,
            "created_at": str(self.created_at) if self.created_at else None,
            "last_login": str(self.last_login) if self.last_login else None,
        }


class AuditLog(Base):
    __tablename__ = "audit_logs"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, nullable=True)
    username = Column(String(50), nullable=True)
    action = Column(String(100), nullable=False)
    details = Column(Text, nullable=True)
    timestamp = Column(DateTime, server_default=func.now())

    def to_dict(self):
        return {
            "id": self.id,
            "username": self.username,
            "action": self.action,
            "details": self.details,
            "timestamp": str(self.timestamp) if self.timestamp else None,
        }

class WebLog(Base):
    __tablename__ = "web_logs"

    id              = Column(Integer, primary_key=True, autoincrement=True)
    timestamp       = Column(DateTime, nullable=True, index=True)

    # Identity & session
    user_id         = Column(String(50),  nullable=True, index=True)
    session_id      = Column(String(100), nullable=True, index=True)
    ip_address      = Column(String(50),  nullable=True)

    # Request details
    activity_type   = Column(String(100), nullable=True)
    service_name    = Column(String(200), nullable=True)
    page_url        = Column(String(500), nullable=True)
    http_status     = Column(Integer,     nullable=True)
    response_time_ms= Column(Integer,     nullable=True)

    # Geography & campaign
    location        = Column(String(100), nullable=True)
    campaign_id     = Column(String(100), nullable=True)
    campaign_type   = Column(String(100), nullable=True)
    referrer        = Column(String(200), nullable=True)

    # Device info
    device_type     = Column(String(50),  nullable=True)
    browser         = Column(String(50),  nullable=True)

    # Business metrics
    lead_flag       = Column(Integer,     default=0)
    conversion_flag = Column(Integer,     default=0)
    conversion_type = Column(String(100), nullable=True)
    revenue_value   = Column(Integer,     default=0)

    # Legacy aliases kept for backward compatibility with old queries
    @property
    def status_code(self):
        return self.http_status

    @property
    def country(self):
        return self.location

    @property
    def service_type(self):
        return self.service_name

    @property
    def revenue(self):
        return self.revenue_value
