from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import ForeignKey

db = SQLAlchemy()

class Users(db.Model):
    __tablename__ = "users"
    user_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    email = db.Column(db.String, nullable=False, unique=True)
    password = db.Column(db.String, nullable=False)
    role = db.Column(db.Integer, nullable=False)
    niche = db.Column(db.String, nullable=True)
    platform = db.Column(db.String, nullable=True)
    followers = db.Column(db.Integer, nullable=True)
    campaigns = db.relationship('Campaign', back_populates='user', lazy='joined')
    ad_requests_source = db.relationship('AdRequest', foreign_keys='AdRequest.source', back_populates='usr_source', lazy='joined')
    ad_requests_target = db.relationship('AdRequest', foreign_keys='AdRequest.target', back_populates='usr_target', lazy='joined')


class Campaign(db.Model):
    __tablename__ = "campaign"
    campaign_id = db.Column(db.Integer, primary_key=True)
    sponsor_id = db.Column(db.Integer, ForeignKey('users.user_id'))
    start_date = db.Column(db.Date, nullable=False)
    end_date = db.Column(db.Date, nullable=False)
    status = db.Column(db.Integer, nullable=False, default=0)
    campaign_name = db.Column(db.String, nullable=False)
    campaign_description = db.Column(db.String, nullable=False)
    budget = db.Column(db.Integer)
    visibility = db.Column(db.Integer, default=0)
    niche = db.Column(db.String)
    user = db.relationship("Users", back_populates="campaigns")
    ad_requests = db.relationship("AdRequest", back_populates="campaign")

class AdRequest(db.Model):
    __tablename__ = "adrequest"
    adrequest_id = db.Column(db.Integer, primary_key=True)
    campaign_id = db.Column(db.Integer, ForeignKey('campaign.campaign_id'))
    source = db.Column(db.Integer, ForeignKey('users.user_id'))
    target = db.Column(db.Integer, ForeignKey('users.user_id'))
    status = db.Column(db.String, nullable=False, default='Pending')
    payment_status = db.Column(db.String, nullable=False, default="Pending")
    amount = db.Column(db.Integer)
    requirements = db.Column(db.String, nullable=False)
    usr_source = db.relationship("Users", foreign_keys=[source], back_populates="ad_requests_source")
    usr_target = db.relationship("Users", foreign_keys=[target], back_populates="ad_requests_target")
    campaign = db.relationship("Campaign", back_populates="ad_requests")

class Flagged(db.Model):
    __tablename__ = "flagged"
    flagged_id = db.Column(db.Integer, primary_key=True)
    user_or_campaign = db.Column(db.Integer, nullable=False) # 0 -> user 1 -> campaign
    status = db.Column(db.String)
