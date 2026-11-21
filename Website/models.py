from typing import Optional
import datetime
import enum

from sqlalchemy import Column, Date, Enum, ForeignKeyConstraint, Index, Integer, String, TIMESTAMP, Table, Text, text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from . import db

from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash


class SubmissionsStatus(str, enum.Enum):
    PENDING = 'Pending'
    APPROVED = 'Approved'
    REJECTED = 'Rejected'


class Interest(db.Model):
    __tablename__ = 'interest'

    interest_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    interests: Mapped[Optional[str]] = mapped_column(String(100))

    user: Mapped[list['Users']] = relationship('Users', secondary='user_interests', back_populates='interest')


class Opportunities(db.Model):
    __tablename__ = 'opportunities'

    opportunity_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    opportunity_type: Mapped[str] = mapped_column(String(50), nullable=False)
    category: Mapped[str] = mapped_column(String(100), nullable=False)
    country: Mapped[str] = mapped_column(String(100), nullable=False)
    min_age: Mapped[Optional[int]] = mapped_column(Integer)
    max_age: Mapped[Optional[int]] = mapped_column(Integer)
    education_level: Mapped[Optional[str]] = mapped_column(String(50))
    opportunity_description: Mapped[Optional[str]] = mapped_column(Text)
    application_link: Mapped[Optional[str]] = mapped_column(String(500))
    deadline: Mapped[Optional[datetime.date]] = mapped_column(Date)

    saved_opportunities: Mapped[list['SavedOpportunities']] = relationship('SavedOpportunities', back_populates='opportunity')


class Submissions(db.Model):
    __tablename__ = 'submissions'

    submission_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    organization_name: Mapped[str] = mapped_column(String(255), nullable=False)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    opportunity_type: Mapped[Optional[str]] = mapped_column(String(100))
    category: Mapped[Optional[str]] = mapped_column(String(100))
    country: Mapped[Optional[str]] = mapped_column(String(100))
    min_age: Mapped[Optional[int]] = mapped_column(Integer)
    max_age: Mapped[Optional[int]] = mapped_column(Integer)
    education_level: Mapped[Optional[str]] = mapped_column(String(50))
    description: Mapped[Optional[str]] = mapped_column(Text)
    application_link: Mapped[Optional[str]] = mapped_column(String(500))
    deadline: Mapped[Optional[datetime.date]] = mapped_column(Date)
    status: Mapped[Optional[SubmissionsStatus]] = mapped_column(Enum(SubmissionsStatus, values_callable=lambda cls: [member.value for member in cls]), server_default=text("'Pending'"))
    submitted_at: Mapped[Optional[datetime.datetime]] = mapped_column(TIMESTAMP, server_default=text('CURRENT_TIMESTAMP'))


class Users(UserMixin, db.Model):
    __tablename__ = 'users'
    __table_args__ = (
        Index('email', 'email', unique=True),
    )

    user_id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    first_name: Mapped[Optional[str]] = mapped_column(String(100))
    last_name: Mapped[Optional[str]] = mapped_column(String(100))
    age: Mapped[Optional[int]] = mapped_column(Integer)
    email: Mapped[Optional[str]] = mapped_column(String(255))
    country: Mapped[Optional[str]] = mapped_column(String(100))
    education_level: Mapped[Optional[str]] = mapped_column(String(100))
    password_hash: Mapped[Optional[str]] = mapped_column(String(255))

    interest: Mapped[list['Interest']] = relationship('Interest', secondary='user_interests', back_populates='user')
    saved_opportunities: Mapped[list['SavedOpportunities']] = relationship('SavedOpportunities', back_populates='user')

    def get_id(self):
        return str(self.user_id)
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return self.password_hash is not None and check_password_hash(self.password_hash, password)

class SavedOpportunities(db.Model):
    __tablename__ = 'saved_opportunities'
    __table_args__ = (
        ForeignKeyConstraint(['opportunity_id'], ['opportunities.opportunity_id'], name='saved_opportunities_ibfk_2'),
        ForeignKeyConstraint(['user_id'], ['users.user_id'], name='saved_opportunities_ibfk_1'),
        Index('opportunity_id', 'opportunity_id')
    )

    user_id: Mapped[int] = mapped_column(Integer, primary_key=True)
    opportunity_id: Mapped[int] = mapped_column(Integer, primary_key=True)
    saved_at: Mapped[Optional[datetime.datetime]] = mapped_column(TIMESTAMP, server_default=text('CURRENT_TIMESTAMP'))

    opportunity: Mapped['Opportunities'] = relationship('Opportunities', back_populates='saved_opportunities')
    user: Mapped['Users'] = relationship('Users', back_populates='saved_opportunities')


t_user_interests = Table(
    'user_interests', db.Model.metadata,
    Column('user_id', Integer, primary_key=True),
    Column('interest_id', Integer, primary_key=True),
    ForeignKeyConstraint(['interest_id'], ['interest.interest_id'], name='user_interests_ibfk_2'),
    ForeignKeyConstraint(['user_id'], ['users.user_id'], name='user_interests_ibfk_1'),
    Index('interest_id', 'interest_id')
)