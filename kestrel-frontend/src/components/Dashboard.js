import React, { useState, useEffect, useCallback } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth0 } from '@auth0/auth0-react';
import axios from 'axios';
import './Dashboard.css'
import Sidebar from './Sidebar';

const API_BASE_URL = 'http://localhost:5000';

const Dashboard = () => {
    const [topGames, setTopGames] = useState([]);
    const [currentGameIndex, setCurrentGameIndex] = useState(0);
    const [direction, setDirection] = useState(null);
    const { getAccessTokenSilently } = useAuth0();
    const navigate = useNavigate();
    const [isSidebarOpen, setIsSidebarOpen] = useState(true);
  
    const toggleSidebar = () => {
      setIsSidebarOpen(!isSidebarOpen);
    };

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

  useEffect(() => {
    const fetchTopGames = async () => {
      try {
        const token = await getAccessTokenSilently();
        const response = await axios.get(`${API_BASE_URL}/api/top-games`, {
          headers: { Authorization: `Bearer ${token}` }
        });
        setTopGames(response.data);
      } catch (error) {
        console.error('Error fetching top games:', error);
      }
  };

    fetchTopGames();
  }, [getAccessTokenSilently]);

  const [autoScrollActive, setAutoScrollActive] = useState(true);
  const changeGame = useCallback((newDirection) => {
    setAutoScrollActive(false); // Deactivate auto-scrolling
    setDirection(newDirection);
    setCurrentGameIndex((prevIndex) => {
      if (newDirection === 'next') {
        return (prevIndex + 1) % topGames.length;
      } else {
        return (prevIndex - 1 + topGames.length) % topGames.length;
      }
    });
    
    setTimeout(() => {
      setDirection(null);
    }, 500);
  }, [topGames.length]);

  useEffect(() => {
    let interval;
    if (autoScrollActive) {
      interval = setInterval(() => {
        changeGame('next');
      }, 5000);
    }
  
    return () => {
      if (interval) {
        clearInterval(interval);
      }
    };
  }, [changeGame, autoScrollActive]);
  const handleGameClick = (gameId) => {
    navigate(`/games/${gameId}`);
  };

  const renderFeaturedGame = (game, index) => {
    if (!game) return null;
    
    const isActive = index === currentGameIndex;
    const isPrev = (index === currentGameIndex - 1) || (currentGameIndex === 0 && index === topGames.length - 1);
    const isNext = (index === currentGameIndex + 1) || (currentGameIndex === topGames.length - 1 && index === 0);
    
    let className = "featured-game";
    if (isActive) className += " active";
    if (isPrev) className += " prev";
    if (isNext) className += " next";
    if (direction === 'next' && isPrev) className += " slide-left";
    if (direction === 'prev' && isNext) className += " slide-right";
  return (
      <div 
        key={game.id}
        className={className}
        style={{
          '--bg-image': `url(${game.cover_art_url})`
        }}
      >
        <div className="featured-game-content" onClick={() => handleGameClick(game.id)}>
          <img src={game.cover_art_url} alt={game.title} className="game-details-cover" />
          <div className="game-info">
            <h1>{game.title}</h1>
            <h3>{formatText(game.franchise)}</h3>
            <p>{game.description}</p>
            {game.studio && <p className="studio">{formatText(game.studio)}</p>}
          </div>
        </div>
        </div>
  );
};

  return (
    <div className={`dashboard-container ${isSidebarOpen ? 'sidebar-open' : ''}`}>
      <Sidebar isOpen={isSidebarOpen} toggleSidebar={toggleSidebar} />
      <div className={`main-content ${isSidebarOpen ? 'sidebar-open' : ''}`}>
        <div className="featured-game-container">
          <h2 className="featured-game-heading">Everyone's Now Playing</h2>
          {topGames.map((game, index) => renderFeaturedGame(game, index))}
          <div className="navigation-arrows">
            <button className="arrow-button" onClick={() => { setAutoScrollActive(false); changeGame('prev'); }}>&lt;</button>
            <button className="arrow-button" onClick={() => { setAutoScrollActive(false); changeGame('next'); }}>&gt;</button>

          </div>
        </div>
        
        {/* Additional dashboard content */}
        <div style={{ marginLeft: '80px' }}>
            <h1>Dashboard Content</h1>
            <p>This is the main dashboard area. It will be pushed to the right when the sidebar is open.</p>
            {/* ... more dashboard content ... */}
        </div>
      </div>
    </div>
  );
};

export default Dashboard;