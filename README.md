# Kestrel

*This project fulfills the final project requirements for the Udacity Full Stack Web Developer course.*

Kestrel is a web application inspired by the UI for the popular manga-reading site MangaDex (https://mangadex.org), but made for video games.

It's often difficult to catalogue all of your collection, especially when spread across multiple platforms, even if libraries like Steam have good built-in categorization options. Kestrel aims to consolidate the tracking of your collection into one place.

Additionally, Kestrel aims to organize your collection via a *tag* system similar to how MangaDex catalogues their offerings. Tags are community-defined groupings of games aimed to find you a more specialized genre of game that fits the vibe you're looking for, as opposed to typical user definitions like "Action" or "Adventure" that are not descriptive at all in this age of gaming. Tags might be something like `Cozy` or `esport`, or `Souls-like` for example. (*Note: the tag feature is still in development.*)

## Features

As of the current build submitted for this project, Kestrel can do the following:
- Support individual user accounts (currently limited to Google accounts thru Auth0)
- Utilize the IGDB API to search for games in Twitch's database of games and add them to Kestrel's database.
- Add games in Kestrel's database to your "Library", a full list of games you own
- Add games in Kestrel's database to your "Now Playing", a full list of games you're currently playing.
- Rank games according to the number of players now playing them. The top 10 games get featured on the Dashboard of the app homepage for easy discovery.

## Usage

On the application login screen, sign up for an account with either your email or Google. Then you can add a game to Kestrel's database with the `Add a Game` page, add it to your `Library` and `Now Playing`, and see your collection by these two categories currently!

![](./demo/kestrel.gif)

## Structure

Kestrel's stack is comprised of the following:

> Frontend: ReactJS

> Database: PostgreSQL

> Backend: Python (Flask)

All of the Python backend code is located in the `app` folder. All of the ReactJS (including CSS) frontend code is located in the `kestrel-frontend` folder. Necessary environment variables can be defined in a `.env` file or on the platform hosting the app (Heroku in this case).

### Backend

The deliverables for this project. Comprised of multiple items that will be expounded upon below. `SQLAlchemy ORM` is used to talk to the `PostgreSQL` database.

`__init__.py`
- Creates the app from a Config file and sets up the database and CORS.
  - The app gets constructed from a `blueprint` defined in the `routes` submodule.
- A mock database is configured if the app is started with a test flag.

`decorators.py`
- To be expanded upon in the future, this module defines decorators for the app (excluding auth, which is handled in its own submodule).
- The main function here is the `user_required` function that checks if a user was logged in properly and if not creates an actual entry for their account in the app database.
  - The base user permission `get:games` is needed here. Auth0 grants this permission to all users of the app by default thanks to a custom action executed on user signup that grants the `User` role to everyone.
- Tracking custom usernames and email is an intended feature eventually, but dummy entries are used right now until this gets implemented.

`extensions.py`
- Imports additional extensions needed to power the backend through database setup.

`models.py`
- Defines the database models for the app.
- Association tables are created for many-to-many relationships that are required for certain features.
- The `User` class is the main model for the app: it contains various parameters but in particular the owned games (library) and now playing lists for each user.
- The `Game` class contains all of the games within the app's database. Most of its fields get directly 1:1 imported from the details fetched for the game through the Twitch IGDB API in `search_engine`.
- The `Genre` class is still a WIP. It will eventually be the main way to filter games in the app database but is partially setup in this initial version of the app.
- The `Comments` class handles comments for a game's entry in the app. It populates the comments list eventually, but is still a WIP and not fully implemented yet.

`routes.py`
- Defines the various routes for the app.
   - Uses `blueprints` to do this.
- There are many endpoints for the app, consult the actual `routes.py` file for information on all of them as the docstrings for each clearly detail what all of them do.
- A few endpoints that are special: `/api/games/<int:game_id>` for both `PATCH` and `DELETE` requests require the `patch:games` and `delete:games` permissions respectively. **These are admin-scoped and granted permissions**, so only users with the `Admin` role can make these requests to the backend endpoint. The `Admin` role is granted to specific users manually within the app Auth0 dashboard, and normal users have no way to get the role autonomously.
- Error handlers for expected common errors most users (or the frontend, rather) would make to the backend are created.
- All routes that commit something to the database are wrapped in a `try/except/finally` block to handle 500 errors and rollback the database if needed, along with always closing the database connection to free up the connection pool.

`search_engine.py`
- This module handles connecting to and querying information for games from the Twitch IGDB API.
- Browse the documentation for this module directly from the code itself as all functions have associated docstrings.
- The module is run primarily through the `IGDBApi` class defined in the code.
- A note: queries to the IGDB API from this module are limited to 30 results to prevent IGDB's too many requests lockout.
- A `__name__ == '__main__'` block is included to allow for testing of the module's functionality.

`test_kestrel_backend.py`
- This module is used to test the backend functionality for the endpoints.
  - It uses the `unittest` library.
- It requires `.env` variables pointing to `User` and `Admin` JWTs specifically to be work properly. (These will be provided in the Udacity submission comments for reference)

### Database

The `PostgreSQL` database is setup with the following commands based on the existing migration folder in the app.
> flask db init

> flask db migrate

> flask db upgrade

A `.env` file with the appropriate pointers to the database location along with user and password needs to be used to properly point the app to the database (or define these variables on the platform, like Heroku).

### Frontend

The frontend is a `React` app styled with `CSS`. The exact specifics of the frontend will not be expounded upon in this README but the tree diagram will be provided below for an idea of how the frontend is structured.

```
kestrel-frontend/
│
├── public/
│   ├── index.html
│   ├── manifest.json
│   └── robots.txt
│
├── src/
│   ├── assets/
│   │   ├── game.png
│   │   ├── admin.png
│   │   └── kestrel.png
│   │
│   ├── components/
│   │   ├── AddGame.js
│   │   ├── AddGame.css
│   │   ├── Dashboard.js
│   │   ├── Dashboard.css
│   │   ├── GameDetails.js
│   │   ├── GameDetails.css
│   │   ├── LandingPage.js
│   │   ├── LandingPage.css
│   │   ├── Library.js
│   │   ├── Library.css
│   │   ├── Loading.js
│   │   ├── Loading.css
│   │   ├── NowPlaying.js
│   │   ├── NowPlaying.css
│   │   ├── SearchBar.js
│   │   ├── SearchBar.css
│   │   ├── Sidebar.js
│   │   └── Sidebar.css
│   │
│   ├── App.js
│   ├── App.css
│   ├── App.test.js
│   ├── auth0-config.js
│   ├── index.js
│   ├── index.css
│   ├── reportWebVitals.js
│   └── setupTests.js
│
├── package.json
```