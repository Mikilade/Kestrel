import React, { useState, useEffect } from 'react';
import axios from 'axios';
import './SearchBar.css';
import gamesIcon from '../assets/game.png';

const SearchBar = ({ onGameSelect }) => {
    const [query, setQuery] = useState('');
    const [results, setResults] = useState([]);
    const [isLoading, setIsLoading] = useState(false);
    const [usingFallback, setUsingFallback] = useState({});

    useEffect(() => {
        const searchGames = async () => {
            if (query.length < 3) {
                setResults([]);
                return;
            }

            setIsLoading(true);
            try {
                const response = await axios.get(`http://localhost:5000/api/search-games?query=${query}`);
                setResults(response.data);
            } catch (error) {
                console.error('Error searching games:', error);
            }
            setIsLoading(false);
        };

        const debounce = setTimeout(() => {
            searchGames();
        }, 300);

        return () => clearTimeout(debounce);
    }, [query]);

    const handleGameSelect = (game) => {
        onGameSelect(game);
        setQuery('');  // Clear the search query
        setResults([]); // Clear the search results
    };


    return (
        <div className="search-bar">
            <input
                type="text"
                value={query}
                onChange={(e) => setQuery(e.target.value)}
                placeholder="Search for a game..."
            />
            {isLoading && <div className="loading">Loading...</div>}
            {results.length > 0 && (
                <ul className="search-results">
                    {results.map((game) => (
                        <li key={game.id} className="search-result-item" onClick={() => handleGameSelect(game)}>
                            <img 
                                src={game.cover_url || gamesIcon} 
                                alt={game.name}
                                className={`game-cover-search ${usingFallback[game.id] ? 'fallback-icon' : ''}`}
                                onError={(e) => {
                                    e.target.onerror = null; // prevents looping
                                    e.target.src = gamesIcon;
                                    setUsingFallback(prev => ({...prev, [game.id]: true}));
                                }}
                            />
                            <span className="game-name">{game.name}</span>
                        </li>
                    ))}
                </ul>
            )}
        </div>
    );
};

export default SearchBar;
