"""
This module defines the main routes for the Flask application.
It includes endpoints for managing users, games, genres, comments, and user libraries.
"""

from flask import Blueprint, jsonify, request
from app.models import User, Game, Genre, Comment
from app.extensions import db
from app.search_engine import IGDBApi
from sqlalchemy import func
import datetime
from datetime import date
from auth.auth import AuthError, requires_auth
from app.decorators import user_required

bp = Blueprint('main', __name__)

@bp.route('/api/users', methods=['POST'])
def create_user(payload):
    data = request.json
    new_user = User(username=data['username'], email=data['email'], auth0_id=payload['sub'])
    # In a real application, you'd hash the password here
    db.session.add(new_user)
    db.session.commit()
    return jsonify({'id': new_user.id, 'username': new_user.username}), 201

@bp.route('/api/users/<int:user_id>/owned_games', methods=['POST'])
def add_owned_game(user_id):
    user = User.query.get_or_404(user_id)
    data = request.json
    game = Game.query.get_or_404(data['game_id'])
    user.owned_games.append(game)
    db.session.commit()
    return jsonify({'message': 'Game added to owned games'}), 200

@bp.route('/api/users/<int:user_id>/now_playing', methods=['POST'])
def add_now_playing(user_id):
    user = User.query.get_or_404(user_id)
    data = request.json
    game = Game.query.get_or_404(data['game_id'])
    user.now_playing.append(game)
    db.session.commit()
    return jsonify({'message': 'Game added to now playing'}), 200

@bp.route('/api/users/<int:user_id>', methods=['GET'])
def get_user(user_id):
    user = User.query.get_or_404(user_id)
    return jsonify({
        'id': user.id,
        'username': user.username,
        'email': user.email,
        'owned_games': [{'id': game.id, 'title': game.title} for game in user.owned_games],
        'now_playing': [{'id': game.id, 'title': game.title} for game in user.now_playing]
    })

@bp.route('/api/games', methods=['GET'])
def get_games():
    games = Game.query.all()
    return jsonify([{
        'id': game.id,
        'title': game.title,
        'genres': [{'id': genre.id, 'name': genre.name} for genre in game.genres]
    } for game in games])

@bp.route('/api/games', methods=['POST'])
def create_game():
    data = request.json

    # Check if the game already exists in our database
    existing_game = Game.query.filter_by(igdb_id=data['id']).first()
    if existing_game:
        return jsonify({'message': 'Game already exists', 'game': existing_game.id}), 409

    # Create new game
    new_game = Game(
        igdb_id=data['id'],
        title=data['name'],
        description=data.get('summary'),
        cover_art_url=data.get('cover_url'),
        franchise=data.get('franchise'),
        studio=data.get('studio'),
        release_date=date.fromtimestamp(data['first_release_date']) if data.get('first_release_date') else None
    )

    # Handle genres
    if 'genres' in data:
        for genre_data in data['genres']:
            genre = Genre.query.filter_by(name=genre_data['name']).first()
            if not genre:
                genre = Genre(name=genre_data['name'])
                db.session.add(genre)
            new_game.genres.append(genre)

    db.session.add(new_game)
    db.session.commit()

    return jsonify({
        'id': new_game.id,
        'igdb_id': new_game.igdb_id,
        'title': new_game.title,
        'description': new_game.description,
        'cover_art_url': new_game.cover_art_url,
        'franchise': new_game.franchise,
        'studio': new_game.studio,
        'release_date': new_game.release_date.isoformat() if new_game.release_date else None,
        'genres': [{'id': genre.id, 'name': genre.name} for genre in new_game.genres]
    }), 201

@bp.route('/api/genres', methods=['GET'])
def get_genres():
    genres = Genre.query.all()
    return jsonify([{'id': genre.id, 'name': genre.name} for genre in genres])

@bp.route('/api/genres', methods=['POST'])
def create_genre():
    data = request.json
    new_genre = Genre(name=data['name'], description=data.get('description'))
    db.session.add(new_genre)
    db.session.commit()
    return jsonify({'id': new_genre.id, 'name': new_genre.name}), 201

@bp.route('/api/games/<int:game_id>', methods=['GET'])
def get_game_details(game_id):
    game = Game.query.get_or_404(game_id)

    # If we don't have all details, fetch from IGDB
    #if not game.franchise or not game.studio:
    #    igdb = IGDBApi()
    ##    igdb_details = igdb.get_game_details(game.igdb_id)
     #   if igdb_details:
    #        game.franchise = igdb_details.get('franchise')
    #        game.studio = igdb_details.get('studio')
    #        db.session.commit()

    comments = Comment.query.filter_by(game_id=game.id).order_by(Comment.created_at.asc()).all()

    return jsonify({
        'id': game.id,
        'title': game.title,
        'description': game.description,
        'cover_art_url': game.cover_art_url,
        'franchise': game.franchise,
        'studio': game.studio,
        'comments': [{
            'id': comment.id,
            'content': comment.content,
            'created_at': comment.created_at.isoformat(),
            'user': {
                'id': comment.user.id,
                'username': comment.user.username
            }
        } for comment in comments]
    })

@bp.route('/api/games/<int:game_id>/comments', methods=['POST'])
def add_comment(game_id):
    data = request.json
    user_id = data['user_id']  # You'd typically get this from the authenticated user
    content = data['content']

    new_comment = Comment(content=content, user_id=user_id, game_id=game_id)
    db.session.add(new_comment)
    db.session.commit()

    return jsonify({
        'id': new_comment.id,
        'content': new_comment.content,
        'created_at': new_comment.created_at.isoformat(),
        'user': {
            'id': new_comment.user.id,
            'username': new_comment.user.username
        }
    }), 201

@bp.route('/api/top-games', methods=['GET'])
def get_top_games():
    top_games = db.session.query(Game, func.count(User.id).label('player_count'))\
        .join(Game.current_players)\
        .group_by(Game.id)\
        .order_by(func.count(User.id).desc())\
        .limit(10)\
        .all()

    return jsonify([{
        'id': game.id,
        'title': game.title,
        'description': game.description,
        'cover_art_url': game.cover_art_url,
        'franchise': game.franchise,
        'studio': game.studio,
        'player_count': player_count
    } for game, player_count in top_games])

@bp.route('/api/users/<string:user_id>/library/<int:game_id>', methods=['POST', 'DELETE'])
@user_required
def manage_user_library(user_id,game_id, user=None):
    game = Game.query.get_or_404(game_id)

    if request.method == 'POST':
        if game not in user.owned_games:
            user.owned_games.append(game)
            db.session.commit()
            return jsonify({'message': 'Game added to library', 'in_library': True}), 200
        return jsonify({'message': 'Game already in library', 'in_library': True}), 200
    else:
        if game in user.owned_games:
            user.owned_games.remove(game)
            db.session.commit()
            return jsonify({'message': 'Game removed from library', 'in_library': False}), 200
        return jsonify({'message': 'Game not in library', 'in_library': False}), 200

@bp.route('/api/users/<string:user_id>/now_playing/<int:game_id>', methods=['POST', 'DELETE'])
@user_required
def manage_now_playing(user_id,game_id, user=None):
    game = Game.query.get_or_404(game_id)

    if request.method == 'POST':
        if game not in user.now_playing:
            user.now_playing.append(game)
            db.session.commit()
            return jsonify({'message': 'Game added to Now Playing', 'in_now_playing': True}), 200
        return jsonify({'message': 'Game already in Now Playing', 'in_now_playing': True}), 200
    else:
        if game in user.now_playing:
            user.now_playing.remove(game)
            db.session.commit()
            return jsonify({'message': 'Game removed from Now Playing', 'in_now_playing': False}), 200
        return jsonify({'message': 'Game not in Now Playing', 'in_now_playing': False}), 200


@bp.route('/api/users/game_status/<int:game_id>', methods=['GET'])
@user_required
def get_game_status(user, game_id):
    game = Game.query.get_or_404(game_id)

    in_library = game in user.owned_games
    in_now_playing = game in user.now_playing

    return jsonify({
        'in_library': in_library,
        'in_now_playing': in_now_playing
    }), 200




@bp.route('/api/search-games', methods=['GET'])
def search_games():
    query = request.args.get('query', '')
    if len(query) < 3:
        return jsonify([])

    igdb = IGDBApi()
    games = igdb.search_games(query)
    return jsonify(games)

@bp.route('/api/search-games-details/<int:game_id>', methods=['GET'])
def search_game_details(game_id):
    igdb = IGDBApi()
    game_details = igdb.get_game_details(game_id)
    if game_details:
        return jsonify(game_details), 200
    else:
        return jsonify({"error": "Game not found"}), 404

@bp.route('/api/users/library', methods=['GET'])
@user_required
def get_user_library(user):
    return jsonify([{
        'id': game.id,
        'title': game.title,
        'cover_art_url': game.cover_art_url
    } for game in user.owned_games])

@bp.route('/api/users/library/<int:game_id>', methods=['DELETE'])
@user_required
def remove_from_library(user, game_id):
    game = Game.query.get_or_404(game_id)
    if game in user.owned_games:
        user.owned_games.remove(game)
        db.session.commit()
        return jsonify({'message': 'Game removed from library'}), 200
    return jsonify({'message': 'Game not in library'}), 404

@bp.route('/api/users/now_playing', methods=['GET'])
@user_required
def get_user_now_playing(user):
    return jsonify([{
        'id': game.id,
        'title': game.title,
        'cover_art_url': game.cover_art_url
    } for game in user.now_playing])

@bp.route('/api/users/now_playing/<int:game_id>', methods=['DELETE'])
@user_required
def remove_from_now_playing(user, game_id):
    game = Game.query.get_or_404(game_id)
    if game in user.now_playing:
        user.now_playing.remove(game)
        db.session.commit()
        return jsonify({'message': 'Game removed from Now Playing'}), 200
    return jsonify({'message': 'Game not in Now Playing'}), 404
