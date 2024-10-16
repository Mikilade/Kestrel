import React, { useState, useEffect } from 'react';
import { useParams } from 'react-router-dom';
import { useAuth0 } from '@auth0/auth0-react';
import axios from 'axios';
import Sidebar from './Sidebar';
import './GameDetails.css';

const API_BASE_URL = 'http://localhost:5000';

const GameDetails = () => {
  const { gameId } = useParams();
  const { user, getAccessTokenSilently } = useAuth0();
  const [game, setGame] = useState(null);
  const [newComment, setNewComment] = useState('');
  const [inLibrary, setInLibrary] = useState(false);
  const [inNowPlaying, setInNowPlaying] = useState(false);
  const [isSidebarOpen, setIsSidebarOpen] = useState(true);

  // Add this helper function at the beginning of your component
  const formatText = (text) => {
    if (typeof text === 'string') {
      return text.replace(/[{}"']/g, '').trim().replace(/,(?=\S)/g, ', ');
    }
    if (Array.isArray(text)) {
      return text
        .map(item => item.replace(/[{}"']/g, '').trim())
        .join(', ');
    }
    return text;
  };

  const toggleSidebar = () => {
    setIsSidebarOpen(!isSidebarOpen);
  };

  useEffect(() => {
    const fetchGameDetails = async () => {
      try {
      const token = await getAccessTokenSilently();
        const [gameResponse, statusResponse] = await Promise.all([
          axios.get(`${API_BASE_URL}/api/games/${gameId}`, {
        headers: { Authorization: `Bearer ${token}` }
          }),
          axios.get(`${API_BASE_URL}/api/users/game_status/${gameId}`, {
        headers: { Authorization: `Bearer ${token}` }
          })
        ]);
        setGame(gameResponse.data);
        setInLibrary(statusResponse.data.in_library);
        setInNowPlaying(statusResponse.data.in_now_playing);
    } catch (error) {
        console.error('Error fetching game details:', error);
    }
  };

    fetchGameDetails();
  }, [gameId, getAccessTokenSilently]);
  const handleAddToLibrary = async () => {
    try {
      const token = await getAccessTokenSilently();
      const response = await axios.post(`${API_BASE_URL}/api/users/${user.sub}/library/${gameId}`, {}, {
        headers: { Authorization: `Bearer ${token}` }
      });
      setInLibrary(response.data.in_library);
    } catch (error) {
      console.error('Error adding game to library:', error);
    }
};

  const handleAddToNowPlaying = async () => {
    try {
      const token = await getAccessTokenSilently();
      const response = await axios.post(`${API_BASE_URL}/api/users/${user.sub}/now_playing/${gameId}`, {}, {
        headers: { Authorization: `Bearer ${token}` }
      });
      setInNowPlaying(response.data.in_now_playing);
    } catch (error) {
      console.error('Error adding game to Now Playing:', error);
    }
};

  const handleCommentSubmit = async (e) => {
    e.preventDefault();
    try {
      const token = await getAccessTokenSilently();
      const response = await axios.post(`/api/games/${gameId}/comments`, {
        content: newComment,
        user_id: user.sub
      }, {
        headers: { Authorization: `Bearer ${token}` }
      });
      setGame(prevGame => ({
        ...prevGame,
        comments: [...prevGame.comments, response.data]
      }));
      setNewComment('');
    } catch (error) {
      console.error('Error posting comment:', error);
    }
  };

  if (!game) return <div>Loading...</div>;

  return (
    <div className={`game-details-container ${isSidebarOpen ? 'sidebar-open' : ''}`}>
      <Sidebar isOpen={isSidebarOpen} toggleSidebar={toggleSidebar} />
      <div className="game-details-main-content">
        <div className="game-details-header-bg" style={{ '--bg-image': `url(${game.cover_art_url})` }}></div>
        <div className="game-details-header-content">
          <div className="game-details-cover-container">
            <img src={game.cover_art_url} alt={game.title} className="game-details-cover" />
            <div className="user-actions">
              <button 
                onClick={handleAddToLibrary} 
                className={`library-button ${inLibrary ? 'in-library' : ''}`}
              >
                {inLibrary ? 'In Library' : 'Add to Library'}
                {inLibrary && <span className="checkmark">✓</span>}
              </button>
              <button 
                onClick={handleAddToNowPlaying} 
                className={`now-playing-button ${inNowPlaying ? 'in-now-playing' : ''}`}
              >
                {inNowPlaying ? 'Now Playing' : 'Add to Now Playing'}
                {inNowPlaying && <span className="checkmark">✓</span>}
              </button>
            </div>
          </div>
          <div className="game-details-info">
            <h1>{game.title}</h1>
            <h2>{formatText(game.franchise)}</h2>
          </div>
          <div className="game-details-studio">
            <p>Studio: {formatText(game.studio)}</p>
          </div>
        </div>
        <div className="game-details-content">
          <p>{game.description}</p>
          
          <div className="comments-section">
            <h3>Comments</h3>
            {game.comments.map(comment => (
              <div key={comment.id} className="comment">
                <p>{comment.content}</p>
                <small>{comment.user.username} - {new Date(comment.created_at).toLocaleString()}</small>
              </div>
            ))}
            <form onSubmit={handleCommentSubmit}>
              <textarea
                value={newComment}
                onChange={(e) => setNewComment(e.target.value)}
                placeholder="Add a comment..."
              />
              <button type="submit">Post Comment</button>
            </form>
          </div>
        </div>
      </div>
    </div>
  );
};

export default GameDetails;