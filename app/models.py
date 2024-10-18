"""
This module defines the database models for Kestrel.

It includes models for User, Game, Genre, and Comment, as well as association tables
for many-to-many relationships between these entities.
"""

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
    """
    Represents a user in the database.

    This class defines the structure for storing user information, including
    authentication details and relationships with games and comments.

    Attributes:
        id (int): The unique identifier for the user.
        username (str): The user's username (unique, max 64 characters).
        email (str): The user's email address (unique, max 120 characters).
        auth0_id (str): The user's Auth0 identifier (unique, max 120 characters).
        password_hash (str): The hashed password for the user (max 128 characters).
        created_at (datetime): The timestamp when the user account was created.
        updated_at (datetime): The timestamp when the user account was last updated.
        owned_games (relationship): The games owned by this user.
        now_playing (relationship): The games currently being played by this user.
        user_comments (relationship): The comments made by this user.

    Methods:
        __repr__: Returns a string representation of the User object.
    """

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=False, nullable=False)
    email = db.Column(db.String(120), index=True, unique=False, nullable=False)
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
    """
    Represents a game in the database.

    This class defines the structure for storing game information, including
    details from the IGDB (Internet Game Database) and relationships with
    other entities such as genres, users, and comments.

    Attributes:
        id (int): The unique identifier for the game.
        igdb_id (int): The unique identifier from the IGDB.
        title (str): The title of the game (max 100 characters).
        description (str): A description of the game.
        cover_art_url (str): URL to the game's cover art image.
        franchise (str): The franchise the game belongs to (if any).
        studio (str): The studio that developed the game.
        release_date (date): The release date of the game.
        created_at (datetime): The timestamp when the game entry was created.
        updated_at (datetime): The timestamp when the game entry was last updated.
        genres (relationship): The genres associated with this game.
        owners (relationship): The users who own this game.
        current_players (relationship): The users currently playing this game.
        game_comments (relationship): The comments associated with this game.

    Methods:
        __repr__: Returns a string representation of the Game object.
    """

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
    """
    Represents a genre in the database.

    Attributes:
        id (int): The unique identifier for the genre.
        name (str): The name of the genre (unique, max 50 characters).
        description (str): A description of the genre.
        created_at (datetime): The timestamp when the genre was created.
        updated_at (datetime): The timestamp when the genre was last updated.
        games (relationship): The games associated with this genre.

    Methods:
        __repr__: Returns a string representation of the Genre object.
    """

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
    """
    Represents a comment in the database.

    This class defines the structure for storing comments related to games and users.

    Attributes:
        id (int): The unique identifier for the comment.
        content (str): The text content of the comment.
        created_at (datetime): The timestamp when the comment was created.
        user_id (int): The ID of the user who made the comment.
        game_id (int): The ID of the game the comment is associated with.
        user (relationship): The relationship to the User model.
        game (relationship): The relationship to the Game model.

    Methods:
        __repr__: Returns a string representation of the Comment object.
    """

    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    game_id = db.Column(db.Integer, db.ForeignKey('game.id'), nullable=False)

    user = db.relationship('User', back_populates='user_comments')
    game = db.relationship('Game', back_populates='game_comments')

    def __repr__(self):
        return f'<Comment {self.id}>'
