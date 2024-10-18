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

@bp.route('/api/users/<int:user_id>/owned_games', methods=['POST'])
def add_owned_game(user_id):
    """
    Add a game to a user's owned games list.

    This function retrieves a user and a game based on the provided user_id and game_id,
    adds the game to the user's owned_games list, and commits the change to the database.

    Args:
        user_id (int): The ID of the user to whom the game will be added.

    Returns:
        tuple: A tuple containing a JSON response and HTTP status code.
            The JSON response includes a success message.
            The HTTP status code is 200 if successful.

    Raises:
        404: If either the user or the game is not found in the database.
    """
    user = User.query.get_or_404(user_id)
    data = request.json
    game = Game.query.get_or_404(data['game_id'])
    user.owned_games.append(game)
    db.session.commit()
    return jsonify({'message': 'Game added to owned games'}), 200

@bp.route('/api/users/<int:user_id>/now_playing', methods=['POST'])
def add_now_playing(user_id):
    """
    Add a game to a user's 'now playing' list.

    This function retrieves a user and a game based on the provided user_id and game_id,
    adds the game to the user's now_playing list, and commits the change to the database.

    Args:
        user_id (int): The ID of the user to whom the game will be added.

    Returns:
        tuple: A tuple containing a JSON response and HTTP status code.
            The JSON response includes a success message.
            The HTTP status code is 200 if successful.

    Raises:
        404: If either the user or the game is not found in the database.
    """
    user = User.query.get_or_404(user_id)
    data = request.json
    game = Game.query.get_or_404(data['game_id'])
    user.now_playing.append(game)
    db.session.commit()
    return jsonify({'message': 'Game added to now playing'}), 200

@bp.route('/api/users/<int:user_id>', methods=['GET'])
def get_user(user_id):
    """
    Retrieve user information by user ID.

    This function handles GET requests to the '/api/users/<int:user_id>' endpoint.
    It retrieves a user from the database based on the provided user_id and
    returns a JSON response containing the user's information, including their
    owned games and currently playing games.

    Args:
        user_id (int): The ID of the user to retrieve.

    Returns:
        flask.Response: A JSON response containing the user's information.
        The response includes the following fields:
        - id: The user's ID
        - username: The user's username
        - email: The user's email address
        - owned_games: A list of games owned by the user (each game has 'id' and 'title')
        - now_playing: A list of games the user is currently playing (each game has 'id' and 'title')

    Raises:
        werkzeug.exceptions.NotFound: If no user with the given user_id is found in the database.

    """
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
    """
    Retrieve all games from the database.

    This function handles GET requests to the '/api/games' endpoint.
    It fetches all games from the database and returns them as a JSON response.

    Returns:
        flask.Response: A JSON response containing a list of all games.
        Each game in the list includes the following information:
        - id: The game's unique identifier
        - title: The title of the game
        - genres: A list of genres associated with the game, each containing:
            - id: The genre's unique identifier
            - name: The name of the genre

    Note:
        This endpoint does not require authentication and returns all games
        stored in the database without any filtering or pagination.
    """
    games = Game.query.all()
    return jsonify([{
        'id': game.id,
        'title': game.title,
        'genres': [{'id': genre.id, 'name': genre.name} for genre in game.genres]
    } for game in games])

@bp.route('/api/games', methods=['POST'])
def create_game():
    """
    Create a new game in the database.

    This function handles POST requests to the '/api/games' endpoint.
    It creates a new game entry in the database based on the provided JSON data.

    The function first checks if the game already exists in the database by its IGDB ID.
    If it does, it returns a conflict response. If not, it creates a new Game object
    with the provided data, including handling genres.

    Args:
        None (data is extracted from request.json)

    Returns:
        tuple: A tuple containing a JSON response and HTTP status code.
            - If successful, returns the created game's details and 201 status code.
            - If the game already exists, returns a conflict message and 409 status code.
            - If no data is provided, returns a bad request message and 400 status code.

    JSON Payload:
        - id (int): The IGDB ID of the game
        - name (str): The title of the game
        - summary (str, optional): The description of the game
        - cover_url (str, optional): URL of the game's cover art
        - franchise (str, optional): The franchise the game belongs to
        - studio (str, optional): The studio that developed the game
        - first_release_date (int, optional): Unix timestamp of the game's release date
        - genres (list, optional): List of genre dictionaries, each containing 'name'

    Raises:
        400: If no JSON data is provided in the request.
        409: If a game with the same IGDB ID already exists in the database.
    """
    data = request.json
    if not data:
        return jsonify({'message': 'Bad request!'}), 400

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
    """
    Retrieve all genres from the database.

    This function handles GET requests to the '/api/genres' endpoint.
    It fetches all genres from the database and returns them as a JSON response.

    Returns:
        flask.Response: A JSON response containing a list of all genres.
        Each genre in the list includes the following information:
        - id: The genre's unique identifier
        - name: The name of the genre

    Note:
        This endpoint does not require authentication and returns all genres
        stored in the database without any filtering or pagination.
    """
    genres = Genre.query.all()
    return jsonify([{'id': genre.id, 'name': genre.name} for genre in genres])

@bp.route('/api/genres', methods=['POST'])
def create_genre():
    """
    Create a new genre in the database.

    This function handles POST requests to the '/api/genres' endpoint.
    It creates a new genre entry in the database based on the provided JSON data.

    Args:
        None (data is extracted from request.json)

    Returns:
        tuple: A tuple containing a JSON response and HTTP status code.
            The JSON response includes the id and name of the created genre.
            The HTTP status code is 201 if successful.

    JSON Payload:
        - name (str): The name of the genre (required)
        - description (str, optional): A description of the genre

    Raises:
        400: If no JSON data is provided in the request or if 'name' is missing.
    """
    data = request.json
    new_genre = Genre(name=data['name'], description=data.get('description'))
    db.session.add(new_genre)
    db.session.commit()
    return jsonify({'id': new_genre.id, 'name': new_genre.name}), 201

@bp.route('/api/games/<int:game_id>', methods=['GET'])
def get_game_details(game_id):
    """
    Retrieve detailed information about a specific game.

    This function handles GET requests to the '/api/games/<int:game_id>' endpoint.
    It fetches a game from the database based on the provided game_id, along with
    all comments associated with the game, and returns this information as a JSON response.

    Args:
        game_id (int): The unique identifier of the game to retrieve.

    Returns:
        flask.Response: A JSON response containing the game's details and associated comments.
        The response includes the following fields:
        - id: The game's unique identifier
        - title: The title of the game
        - description: A description of the game
        - cover_art_url: URL of the game's cover art
        - franchise: The franchise the game belongs to (if any)
        - studio: The studio that developed the game
        - comments: A list of comments associated with the game, each containing:
            - id: The comment's unique identifier
            - content: The text content of the comment
            - created_at: The timestamp when the comment was created (in ISO format)
            - user: Information about the user who made the comment:
                - id: The user's unique identifier
                - username: The username of the user

    Raises:
        werkzeug.exceptions.NotFound: If no game with the given game_id is found in the database.

    Note:
        Comments are ordered by their creation time in ascending order.
    """
    game = Game.query.get_or_404(game_id)

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
    """
    Add a new comment to a specific game.

    This function handles POST requests to the '/api/games/<int:game_id>/comments' endpoint.
    It creates a new comment for the game specified by game_id using the data provided in the JSON request.
    Args:
        game_id (int): The ID of the game to which the comment will be added.

    Returns:
        tuple: A tuple containing a JSON response and HTTP status code.
            If successful, returns the created comment's details and 201 status code.
            If the game is not found, returns an error message and 404 status code.

    JSON Payload:
        - user_id (int): The ID of the user making the comment.
        - content (str): The text content of the comment.

    Raises:
        404: If the game with the specified game_id is not found.

    Note:
        This function assumes that the User and Game with the provided IDs exist in the database.
        It does not perform explicit checks for their existence beyond the try-except block.
    """
    try:
        data = request.json
        user_id = data['user_id']
        content = data['content']

        new_comment = Comment(content=content, user_id=user_id, game_id=game_id)

        db.session.add(new_comment)
        db.session.commit()
    except:
        return jsonify({"error": "Game not found"}), 404

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
    """
    Retrieve the top 10 games based on the number of current players.

    This function handles GET requests to the '/api/top-games' endpoint.
    It queries the database to find the games with the most current players,
    limits the result to the top 10, and returns them as a JSON response.

    Returns:
        flask.Response: A JSON response containing a list of the top 10 games.
        Each game in the list includes the following information:
        - id: The game's unique identifier
        - title: The title of the game
        - description: A brief description of the game
        - cover_art_url: URL of the game's cover art
        - franchise: The franchise the game belongs to (if any)
        - studio: The studio that developed the game
        - player_count: The number of current players for this game

    Note:
        The games are ordered by the number of current players in descending order.
        This endpoint does not require authentication and returns the top 10 games
        based on the current player count in the database.
    """
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
    """
    Manage a user's game library by adding or removing a game.

    This function handles both POST and DELETE requests to add or remove a game
    from a user's library, respectively.

    Args:
        user_id (str): The ID of the user whose library is being managed.
        game_id (int): The ID of the game to be added or removed from the library.
        user (User, optional): The user object, provided by the @user_required decorator.

    Returns:
        tuple: A tuple containing a JSON response and HTTP status code.
            The JSON response includes a message and a boolean indicating
            whether the game is in the user's library after the operation.
            The HTTP status code is always 200.

    Raises:
        404: If the game with the specified game_id is not found.

    Note:
        This function is protected by the @user_required decorator, which
        ensures that only authenticated users can access this endpoint.
    """
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
    """
    Manage a user's 'Now Playing' list by adding or removing a game.

    This function handles both POST and DELETE requests to add or remove a game
    from a user's 'Now Playing' list, respectively.

    Args:
        user_id (str): The ID of the user whose 'Now Playing' list is being managed.
        game_id (int): The ID of the game to be added or removed from the 'Now Playing' list.
        user (User, optional): The user object, provided by the @user_required decorator.

    Returns:
        tuple: A tuple containing a JSON response and HTTP status code.
            The JSON response includes a message and a boolean indicating
            whether the game is in the user's 'Now Playing' list after the operation.
            The HTTP status code is always 200.

    Raises:
        404: If the game with the specified game_id is not found.

    Note:
        This function is protected by the @user_required decorator, which
        ensures that only authenticated users can access this endpoint.
    """
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
    """
    Get the status of a game for a specific user.

    This function handles GET requests to retrieve the status of a game
    for the authenticated user. It checks whether the game is in the user's
    library and if it's in their 'Now Playing' list.

    Args:
        user (User): The authenticated user object (provided by @user_required decorator).
        game_id (int): The ID of the game to check the status for.

    Returns:
        tuple: A tuple containing a JSON response and HTTP status code.
            The JSON response includes two boolean fields:
            - in_library: True if the game is in the user's library, False otherwise.
            - in_now_playing: True if the game is in the user's 'Now Playing' list, False otherwise.
            The HTTP status code is 200 if successful.

    Raises:
        404: If the game with the specified game_id is not found.

    Note:
        This function is protected by the @user_required decorator, which
        ensures that only authenticated users can access this endpoint.
    """
    game = Game.query.get_or_404(game_id)

    in_library = game in user.owned_games
    in_now_playing = game in user.now_playing

    return jsonify({
        'in_library': in_library,
        'in_now_playing': in_now_playing
    }), 200




@bp.route('/api/search-games', methods=['GET'])
def search_games():
    """
    Search for games using the IGDB API.

    This function handles GET requests to the '/api/search-games' endpoint.
    It uses the 'query' parameter from the request to search for games
    using the IGDB API.

    Args:
        None (query is extracted from request.args)

    Returns:
        flask.Response: A JSON response containing a list of games that match the search query.
        If the query is less than 3 characters long, an empty list is returned.

    Query Parameters:
        query (str): The search term for finding games.

    Note:
        This function requires at least 3 characters in the search query to perform a search.
        The actual search is performed by the IGDBApi class, which is instantiated within this function.
    """
    query = request.args.get('query', '')
    if len(query) < 3:
        return jsonify([])

    igdb = IGDBApi()
    games = igdb.search_games(query)
    return jsonify(games)

@bp.route('/api/search-games-details/<int:game_id>', methods=['GET'])
def search_game_details(game_id):
    """
    Retrieve detailed information about a specific game from the IGDB API.

    This function handles GET requests to the '/api/search-games-details/<int:game_id>' endpoint.
    It uses the IGDB API to fetch detailed information about a game based on its ID.

    Args:
        game_id (int): The unique identifier of the game in the IGDB database.

    Returns:
        tuple: A tuple containing a JSON response and HTTP status code.
            If the game is found, returns the game details and a 200 status code.
            If the game is not found, returns an error message and a 404 status code.

    Note:
        This function relies on the IGDBApi class to interact with the IGDB API.
        The actual structure of the returned game details depends on the IGDB API response.
    """
    igdb = IGDBApi()
    game_details = igdb.get_game_details(game_id)
    if game_details:
        return jsonify(game_details), 200
    else:
        return jsonify({"error": "Game not found"}), 404

@bp.route('/api/users/library', methods=['GET'])
@user_required
def get_user_library(user):
    """
    Retrieve the user's game library.

    This function handles GET requests to the '/api/users/library' endpoint.
    It returns a list of games in the authenticated user's library.

    Args:
        user (User): The authenticated user object (provided by @user_required decorator).

    Returns:
        flask.Response: A JSON response containing a list of games in the user's library.
        Each game in the list includes the following information:
        - id: The game's unique identifier
        - title: The title of the game
        - cover_art_url: URL of the game's cover art

    Note:
        This function is protected by the @user_required decorator, which
        ensures that only authenticated users can access this endpoint.
    """
    return jsonify([{
        'id': game.id,
        'title': game.title,
        'cover_art_url': game.cover_art_url
    } for game in user.owned_games])

@bp.route('/api/users/library/<int:game_id>', methods=['DELETE'])
@user_required
def remove_from_library(user, game_id):
    """
    Remove a game from the user's library.

    This function handles DELETE requests to remove a specific game from the authenticated user's library.

    Args:
        user (User): The authenticated user object (provided by @user_required decorator).
        game_id (int): The ID of the game to be removed from the library.

    Returns:
        tuple: A tuple containing a JSON response and HTTP status code.
            If the game is successfully removed:
                - JSON: {'message': 'Game removed from library'}
                - Status code: 200
            If the game is not in the user's library:
                - JSON: {'message': 'Game not in library'}
                - Status code: 404

    Raises:
        404: If the game with the specified game_id is not found in the database.

    Note:
        This function is protected by the @user_required decorator, which
        ensures that only authenticated users can access this endpoint.
    """
    game = Game.query.get_or_404(game_id)
    if game in user.owned_games:
        user.owned_games.remove(game)
        db.session.commit()
        return jsonify({'message': 'Game removed from library'}), 200
    return jsonify({'message': 'Game not in library'}), 404

@bp.route('/api/users/now_playing', methods=['GET'])
@user_required
def get_user_now_playing(user):
    """
    Retrieve the list of games the user is currently playing.

    This function handles GET requests to the '/api/users/now_playing' endpoint.
    It returns a list of games that the authenticated user has marked as currently playing.

    Args:
        user (User): The authenticated user object (provided by @user_required decorator).

    Returns:
        flask.Response: A JSON response containing a list of games the user is currently playing.
        Each game in the list includes the following information:
        - id: The game's unique identifier
        - title: The title of the game
        - cover_art_url: URL of the game's cover art

    Note:
        This function is protected by the @user_required decorator, which
        ensures that only authenticated users can access this endpoint.
    """
    return jsonify([{
        'id': game.id,
        'title': game.title,
        'cover_art_url': game.cover_art_url
    } for game in user.now_playing])

@bp.route('/api/users/now_playing/<int:game_id>', methods=['DELETE'])
@user_required
def remove_from_now_playing(user, game_id):
    """
    Remove a game from the user's 'Now Playing' list.

    This function handles DELETE requests to remove a specific game from the authenticated user's 'Now Playing' list.

    Args:
        user (User): The authenticated user object (provided by @user_required decorator).
        game_id (int): The ID of the game to be removed from the 'Now Playing' list.

    Returns:
        tuple: A tuple containing a JSON response and HTTP status code.
            If the game is successfully removed:
                - JSON: {'message': 'Game removed from Now Playing'}
                - Status code: 200
            If the game is not in the user's 'Now Playing' list:
                - JSON: {'message': 'Game not in Now Playing'}
                - Status code: 404

    Raises:
        404: If the game with the specified game_id is not found in the database.

    Note:
        This function is protected by the @user_required decorator, which
        ensures that only authenticated users can access this endpoint.
    """
    game = Game.query.get_or_404(game_id)
    if game in user.now_playing:
        user.now_playing.remove(game)
        db.session.commit()
        return jsonify({'message': 'Game removed from Now Playing'}), 200
    return jsonify({'message': 'Game not in Now Playing'}), 404

@bp.route('/api/games/<int:game_id>', methods=['PATCH'])
@requires_auth('patch:games')
def update_game(payload, game_id):
    """
    Update a game's information in the database.

    This function handles PATCH requests to the '/api/games/<int:game_id>' endpoint.
    It updates the specified game's information based on the provided JSON data.

    Args:
        payload (dict): The decoded JWT payload (provided by @requires_auth decorator).
        game_id (int): The ID of the game to be updated.

    Returns:
        tuple: A tuple containing a JSON response and HTTP status code.
            The JSON response includes the updated game's details.
            The HTTP status code is 200 if successful.

    Raises:
        404: If no game with the given game_id is found in the database.

    JSON Payload:
        - title (str, optional): The updated title of the game.
        - description (str, optional): The updated description of the game.
        - cover_art_url (str, optional): The updated URL for the game's cover art.
        - franchise (str, optional): The updated franchise the game belongs to.
        - studio (str, optional): The updated studio that developed the game.
        - release_date (str, optional): The updated release date of the game (in ISO format).
        - genres (list, optional): A list of genre names for the game.

    Note:
        This function requires authentication with the 'patch:games' permission.
        If genres are provided, all existing genres for the game are replaced with the new ones.
    """
    game = Game.query.get_or_404(game_id)
    data = request.json

    # Update game fields
    if 'title' in data:
        game.title = data['title']
    if 'description' in data:
        game.description = data['description']
    if 'cover_art_url' in data:
        game.cover_art_url = data['cover_art_url']
    if 'franchise' in data:
        game.franchise = data['franchise']
    if 'studio' in data:
        game.studio = data['studio']
    if 'release_date' in data:
        game.release_date = date.fromisoformat(data['release_date'])

    # Handle genres
    if 'genres' in data:
        game.genres = []  # Clear existing genres
        for genre_name in data['genres']:
            genre = Genre.query.filter_by(name=genre_name).first()
            if not genre:
                genre = Genre(name=genre_name)
                db.session.add(genre)
            game.genres.append(genre)

    db.session.commit()

    return jsonify({
        'id': game.id,
        'title': game.title,
        'description': game.description,
        'cover_art_url': game.cover_art_url,
        'franchise': game.franchise,
        'studio': game.studio,
        'release_date': game.release_date.isoformat() if game.release_date else None,
        'genres': [genre.name for genre in game.genres]
    }), 200

@bp.route('/api/games/<int:game_id>', methods=['DELETE'])
@requires_auth('delete:games')
def delete_game(payload, game_id):
    """
    Delete a game from the database.

    This function handles DELETE requests to the '/api/games/<int:game_id>' endpoint.
    It removes the specified game from the database, along with all associated data.

    Args:
        payload (dict): The decoded JWT payload (provided by @requires_auth decorator).
        game_id (int): The ID of the game to be deleted.

    Returns:
        tuple: A tuple containing a JSON response and HTTP status code.
            The JSON response includes:
            - success (bool): True if the deletion was successful.
            - deleted (int): The ID of the deleted game.
            The HTTP status code is 200 if successful.

    Raises:
        404: If no game with the given game_id is found in the database.

    Note:
        This function requires authentication with the 'delete:games' permission.
        It performs the following actions:
        1. Removes the game from all users' libraries and 'now playing' lists.
        2. Deletes all comments associated with the game.
        3. Deletes the game itself from the database.
    """
    game = Game.query.get_or_404(game_id)
    
    # Remove the game from users' libraries and now_playing lists
    for user in game.owners:
        user.owned_games.remove(game)
    for user in game.current_players:
        user.now_playing.remove(game)
    
    # Delete associated comments
    Comment.query.filter_by(game_id=game_id).delete()
    
    # Delete the game
    db.session.delete(game)
    db.session.commit()

    return jsonify({
        'success': True,
        'deleted': game_id
    }), 200

@bp.errorhandler(400)
def not_found(error):
    return jsonify({
        "success": False, 
        "error": 400,
        "message": "bad request!"
        }), 400

@bp.errorhandler(404)
def not_found(error):
    return jsonify({
        "success": False, 
        "error": 404,
        "message": "resource not found!"
        }), 404

@bp.errorhandler(405)
def not_allowed(error):
    return jsonify({
        "success": False,
        "error": 405,
        "message": "method not allowed!"
    })

@bp.errorhandler(409)
def conflict(error):
    return jsonify({
        "success": False,
        "error": 409,
        "message": "conflict!"
    })

@bp.errorhandler(422)
def unprocessable(error):
    return jsonify({
        "success": False,
        "error": 422,
        "message": "unprocessable!"
    }), 422

@bp.errorhandler(500)
def internal_server_error(error):
    return jsonify({
        "success": False,
        "error": 500,
        "message": "internal server error!"
    }), 500