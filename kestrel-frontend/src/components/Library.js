// kestrel-frontend/src/components/Library.js
import React, { useState, useEffect } from 'react';
import { useAuth0 } from '@auth0/auth0-react';
import { useNavigate } from 'react-router-dom';
import axios from 'axios';
import Sidebar from './Sidebar';
import './Library.css';
import gamesIcon from '../assets/game.png';

const API_BASE_URL = `${process.env.REACT_APP_API_URL}`;

const Library = () => {
    const [isSidebarOpen, setIsSidebarOpen] = useState(true);
    const [games, setGames] = useState([]);
    const [currentPage, setCurrentPage] = useState(1);
    const [usingFallback, setUsingFallback] = useState({});
    const { getAccessTokenSilently } = useAuth0();
    const navigate = useNavigate();
    const gamesPerPage = 10;

    const toggleSidebar = () => {
        setIsSidebarOpen(!isSidebarOpen);
    };

    const fetchLibrary = async () => {
        try {
            const token = await getAccessTokenSilently();
            const response = await axios.get(`${API_BASE_URL}/api/users/library`, {
                headers: { Authorization: `Bearer ${token}` }
            });
            setGames(response.data);
        } catch (error) {
            console.error('Error fetching library:', error);
        }
    };

    useEffect(() => {
        fetchLibrary();
    }, [getAccessTokenSilently]);

    const handleDeleteGame = async (gameId, event) => {
        event.stopPropagation();
        try {
            const token = await getAccessTokenSilently();
            await axios.delete(`${API_BASE_URL}/api/users/library/${gameId}`, {
                headers: { Authorization: `Bearer ${token}` }
            });
            fetchLibrary(); // Refresh the library after deletion
        } catch (error) {
            console.error('Error deleting game:', error);
        }
    };

    const handleGameClick = (gameId) => {
        navigate(`/games/${gameId}`);
    };

    const indexOfLastGame = currentPage * gamesPerPage;
    const indexOfFirstGame = indexOfLastGame - gamesPerPage;
    const currentGames = games.slice(indexOfFirstGame, indexOfLastGame);

    const paginate = (pageNumber) => setCurrentPage(pageNumber);

    return (
        <div className={`library-container ${isSidebarOpen ? 'sidebar-open' : ''}`}>
            <Sidebar isOpen={isSidebarOpen} toggleSidebar={toggleSidebar} />
            <div className={`library-main-content ${isSidebarOpen ? 'sidebar-open' : ''}`}>
                <h1>My Library</h1>
                <div className="library-grid">
                    {currentGames.map((game) => (
                        <div key={game.id} className="library-game-item" onClick={() => handleGameClick(game.id)}>
                            <img 
                                src={game.cover_art_url || gamesIcon} 
                                alt={game.title}
                                className={`game-cover-library ${usingFallback[game.id] ? 'fallback-icon' : ''}`}
                                onError={(e) => {
                                    e.target.onerror = null;
                                    e.target.src = gamesIcon;
                                    setUsingFallback(prev => ({...prev, [game.id]: true}));
                                }}
                            />
                            <span className="game-title">{game.title}</span>
                            <button 
                                className="delete-button" 
                                onClick={(e) => handleDeleteGame(game.id, e)}
                            >
                                ✕
                            </button>
                        </div>
                    ))}
                </div>
                <div className="pagination">
                    {Array.from({ length: Math.ceil(games.length / gamesPerPage) }, (_, i) => (
                        <button key={i} onClick={() => paginate(i + 1)}>
                            {i + 1}
                        </button>
                    ))}
                </div>
            </div>
        </div>
    );
};

export default Library;
