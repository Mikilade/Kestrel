// AddGame.js
import React, { useState } from 'react';
import axios from 'axios';
import Sidebar from './Sidebar';
import SearchBar from './SearchBar';
import './AddGame.css';
import { useNavigate } from 'react-router-dom';

const AddGame = () => {
    const [isSidebarOpen, setIsSidebarOpen] = useState(true);
    const [selectedGame, setSelectedGame] = useState(null);
    const [isLoading, setIsLoading] = useState(false);

    const toggleSidebar = () => {
        setIsSidebarOpen(!isSidebarOpen);
    };

    const handleGameSelect = async (game) => {
        setIsLoading(true);
        try {
            const response = await axios.get(`http://localhost:5000/api/search-games-details/${game.id}`);
            setSelectedGame(response.data);
        } catch (error) {
            console.error('Error fetching game details:', error);
        }
        setIsLoading(false);
    };

    const handleAddGame = async () => {
        try {
            const response = await axios.post('http://localhost:5000/api/games', selectedGame);
            alert('Game added successfully!');
            // Navigate to the new game's page
            navigate(`/games/${response.data.id}`);
        } catch (error) {
            console.error('Error adding game:', error);
            alert('Failed to add game. Please try again.');
        }
    };

    const navigate = useNavigate();

    return (
        <div className={`add-game-container ${isSidebarOpen ? 'sidebar-open' : ''}`}>
            <Sidebar isOpen={isSidebarOpen} toggleSidebar={toggleSidebar} />
            <div className={`main-content ${isSidebarOpen ? 'sidebar-open' : ''}`}>
                <h1>Add Game</h1>
                <SearchBar onGameSelect={handleGameSelect} />
                {isLoading && <p>Loading game details...</p>}
                {selectedGame && (
                    <div className="game-details-form">
                        <div className="game-details-layout">
                            <div className="game-cover-container">
                                {selectedGame.cover_url && (
                                    <img src={selectedGame.cover_url} alt={selectedGame.name} className="game-cover" />
                                )}
                            </div>
                            <div className="game-info">
                                <h2>{selectedGame.name}</h2>
                                <p><strong>IGDB ID:</strong> {selectedGame.id}</p>
                                <p><strong>Release Date:</strong> {new Date(selectedGame.first_release_date * 1000).toLocaleDateString()}</p>
                                <p>
                                    <strong>Franchise(s):</strong>{' '}
                                    {Array.isArray(selectedGame.franchise)
                                        ? selectedGame.franchise.join(', ') || 'N/A'
                                        : selectedGame.franchise || 'N/A'}
                                </p>
                                <p>
                                    <strong>Studio(s):</strong>{' '}
                                    {Array.isArray(selectedGame.studio)
                                        ? selectedGame.studio.join(', ') || 'N/A'
                                        : selectedGame.studio || 'N/A'}
                                </p>
                            </div>
                        </div>
                        <div className="game-summary">
                            <p><strong>Summary:</strong> {selectedGame.summary}</p>
                        </div>
                        <button onClick={handleAddGame} className="add-game-button">Add Game</button>
                    </div>
                )}
            </div>
        </div>
    );
};

export default AddGame;