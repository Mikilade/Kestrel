"""Tests for backend endpoints."""
import unittest
import json
from flask import Flask
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from app import create_app
from app.extensions import db
from app.models import User, Game, Genre, Comment
from dotenv import load_dotenv
from sqlalchemy.exc import IntegrityError
import jwt
import time
from unittest.mock import patch

class KestrelAPITestCase(unittest.TestCase):
    load_dotenv
    def setUp(self):
        self.app = create_app(test_case=True)
        self.client = self.app.test_client
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def get_auth_header(self, token):
        return {'Authorization': f'Bearer {token}'}

    # Helper method to create a test user
    def create_test_user(self):
        with self.app.app_context():
            user = User.query.filter_by(auth0_id='auth0|123456').first()
            if user is None:
                user = User(username='testuser', email='test@example.com', auth0_id='auth0|123456')
                db.session.add(user)
                db.session.commit()
            return user.id  # Return the id instead of the object


    # Helper method to create a test game
    def create_test_game(self):
        with self.app.app_context():
            game = Game.query.filter_by(igdb_id=12345).first()
            if game is None:
                game = Game(title='Test Game', description='A test game', igdb_id=12345)
                db.session.add(game)
                db.session.commit()
            return game.id  # Return the id instead of the object

    # Test get user
    def test_get_user_success(self):
        with self.app.app_context():
            user_id = self.create_test_user()
            user = User.query.get(user_id)
            res = self.client().get(f'/api/users/{user.id}')
            data = json.loads(res.data)
            self.assertEqual(res.status_code, 200)
            self.assertEqual(data['username'], 'testuser')

    def test_get_user_error(self):
        res = self.client().get('/api/users/9999')  # Non-existent user
        self.assertEqual(res.status_code, 404)

    # Test get games
    def test_get_game_details_success(self):
        with self.app.app_context():
            game = self.create_test_game()
            game_id = game.id
            db.session.expunge_all()

            res = self.client().get(f'/api/games/{game_id}')
            data = json.loads(res.data)
            self.assertEqual(res.status_code, 200)
            self.assertEqual(data['title'], 'Test Game')

    # Test create game
    def test_create_game_success(self):
        res = self.client().post('/api/games', json={
            'id': 54321,
            'name': 'New Game',
            'summary': 'A new test game',
            'cover_url': 'http://example.com/cover.jpg'
        })
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 201)
        self.assertTrue(data['id'])
        self.assertEqual(data['title'], 'New Game')

    def test_create_game_error(self):
        # Test creating a game with missing required data
        res = self.client().post('/api/games', json={})
        self.assertEqual(res.status_code, 400)

    # Test get game details
    def test_get_game_details_success(self):
        with self.app.app_context():
            game_id = self.create_test_game()
            game = Game.query.get(game_id)
            res = self.client().get(f'/api/games/{game.id}')
            data = json.loads(res.data)
            self.assertEqual(res.status_code, 200)
            self.assertEqual(data['title'], 'Test Game')

    def test_get_game_details_error(self):
        res = self.client().get('/api/games/9999')  # Non-existent game
        self.assertEqual(res.status_code, 404)

    # Test add comment
    def test_add_comment_success(self):
        with self.app.app_context():
            user_id = self.create_test_user()
            game_id = self.create_test_game()
            user = User.query.get(user_id)
            game = Game.query.get(game_id)

            res = self.client().post(f'/api/games/{game.id}/comments', json={
                'user_id': user.id,
                'content': 'Great game!'
            })
            data = json.loads(res.data)
            self.assertEqual(res.status_code, 201)
            self.assertTrue(data['id'])
            self.assertEqual(data['content'], 'Great game!')

    def test_add_comment_error(self):
        res = self.client().post('/api/games/9999/comments', json={
            'user_id': 1,
            'content': 'Comment on non-existent game'
        })
        self.assertEqual(res.status_code, 404)

    # Test get top games
    def test_get_top_games_success(self):
        self.create_test_game()
        res = self.client().get('/api/top-games')
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 200)
        self.assertTrue(isinstance(data, list))

    # Test manage user library
    def test_manage_user_library_success(self):
        with self.app.app_context():
            user_id = self.create_test_user()
            game_id = self.create_test_game()
            
            # Fetch the user and game within this context
            user = User.query.get(user_id)
            game = Game.query.get(game_id)

            user_auth0_id = user.auth0_id

            res = self.client().post(f'/api/users/{user_auth0_id}/library/{game_id}',
                                    headers=self.get_auth_header(os.environ.get('USER_JWT')))
            data = json.loads(res.data)
            self.assertEqual(res.status_code, 200)
            self.assertTrue(data['in_library'])



    def test_manage_user_library_error(self):
        res = self.client().post('/api/users/non_existent/library/9999')
        self.assertEqual(res.status_code, 401)  # Unauthorized

    # Test manage now playing
    def test_manage_now_playing_success(self):
        with self.app.app_context():
            user_id = self.create_test_user()
            game_id = self.create_test_game()
            user = User.query.get(user_id)
            game = Game.query.get(game_id)

            res = self.client().post(f'/api/users/{user.auth0_id}/now_playing/{game.id}',
                                    headers=self.get_auth_header(os.environ.get('USER_JWT')))
            data = json.loads(res.data)
            self.assertEqual(res.status_code, 200)
            self.assertTrue(data['in_now_playing'])



    def test_manage_now_playing_error(self):
        res = self.client().post('/api/users/non_existent/now_playing/9999')
        self.assertEqual(res.status_code, 401)  # Unauthorized

    # Test search games
    def test_search_games_success(self):
        res = self.client().get('/api/search-games?query=test')
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 200)
        self.assertTrue(isinstance(data, list))

    def test_search_games_error(self):
        res = self.client().get('/api/search-games?query=a')  # Too short query
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data, [])

    def test_update_game_success(self):
        with self.app.app_context():
            game_id = self.create_test_game()
            game = Game.query.get(game_id)

            res = self.client().patch(f'/api/games/{game.id}',
                                    json={'title': 'Updated Game Title'},
                                    headers=self.get_auth_header(os.environ.get('ADMIN_JWT')))
            data = json.loads(res.data)
            self.assertEqual(res.status_code, 200)
            self.assertEqual(data['title'], 'Updated Game Title')

    def test_update_game_error(self):
        res = self.client().patch('/api/games/9999',
                                  json={'title': 'Updated Game Title'},
                                  headers=self.get_auth_header(os.environ.get('ADMIN_JWT')))
        self.assertEqual(res.status_code, 404)

    # Test delete game
    def test_delete_game_success(self):
        with self.app.app_context():
            game_id = self.create_test_game()
            game = Game.query.get(game_id)

            res = self.client().delete(f'/api/games/{game.id}',
                                    headers=self.get_auth_header(os.environ.get('ADMIN_JWT')))
            data = json.loads(res.data)
            self.assertEqual(res.status_code, 200)
            self.assertTrue(data['success'])
            self.assertEqual(data['deleted'], game.id)

    def test_delete_game_error(self):
        res = self.client().delete('/api/games/9999',
                                   headers=self.get_auth_header(os.environ.get('ADMIN_JWT')))
        self.assertEqual(res.status_code, 404)

if __name__ == "__main__":
    unittest.main()
