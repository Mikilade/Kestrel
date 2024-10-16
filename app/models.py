from app.extensions import db
from datetime import datetime

# Association table for the many-to-many relationship between Game and Genre
game_genre = db.Table('game_genre',
    db.Column('game_id', db.Integer, db.ForeignKey('game.id'), primary_key=True),
    db.Column('genre_id', db.Integer, db.ForeignKey('genre.id'), primary_key=True)
)

# Association table for the many-to-many relationship between User and Game (owned games)
user_owned_games = db.Table('user_owned_games',
    db.Column('user_id', db.Integer, db.ForeignKey('user.id'), primary_key=True),
    db.Column('game_id', db.Integer, db.ForeignKey('game.id'), primary_key=True)
)

# Association table for the many-to-many relationship between User and Game (now playing)
user_now_playing = db.Table('user_now_playing',
    db.Column('user_id', db.Integer, db.ForeignKey('user.id'), primary_key=True),
    db.Column('game_id', db.Integer, db.ForeignKey('game.id'), primary_key=True)
)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True, nullable=False)
    email = db.Column(db.String(120), index=True, unique=True, nullable=False)
    auth0_id = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    owned_games = db.relationship('Game', secondary=user_owned_games, back_populates='owners')
    now_playing = db.relationship('Game', secondary=user_now_playing, back_populates='current_players')
    user_comments = db.relationship('Comment', back_populates='user', lazy='dynamic')

    def __repr__(self):
        return f'<User {self.username}>'

class Game(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    igdb_id = db.Column(db.Integer, unique=True)  # IGDB ID for the game
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    cover_art_url = db.Column(db.String(255))
    franchise = db.Column(db.String(100))
    studio = db.Column(db.String(100))
    release_date = db.Column(db.Date)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    genres = db.relationship('Genre', secondary=game_genre, back_populates='games')
    owners = db.relationship('User', secondary=user_owned_games, back_populates='owned_games')
    current_players = db.relationship('User', secondary=user_now_playing, back_populates='now_playing')
    game_comments = db.relationship('Comment', back_populates='game', lazy='dynamic')

    def __repr__(self):
        return f'<Game {self.title}>'

class Genre(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False, unique=True)
    description = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationship
    games = db.relationship('Game', secondary=game_genre, back_populates='genres')

    def __repr__(self):
        return f'<Genre {self.name}>'
    
class Comment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    game_id = db.Column(db.Integer, db.ForeignKey('game.id'), nullable=False)

    user = db.relationship('User', back_populates='user_comments')
    game = db.relationship('Game', back_populates='game_comments')

    def __repr__(self):
        return f'<Comment {self.id}>'
