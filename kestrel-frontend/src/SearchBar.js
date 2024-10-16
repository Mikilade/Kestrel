import React, { useState, useEffect } from 'react';
import axios from 'axios';
import './SearchBar.css';

const SearchBar = () => {
    const [query, setQuery] = useState('');
    const [results, setResults] = useState([]);
    const [isLoading, setIsLoading] = useState(false);

    useEffect(() => {
        const searchGames = async () => {
            if (query.length < 3) {
                setResults([]);
                return;
            }

            setIsLoading(true);
            try {
                const response = await axios.get(`/api/search-games?query=${query}`);
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
                        <li key={game.id} className="search-result-item">
                            <img src={game.cover_url} alt={game.name} className="game-cover" />
                            <span className="game-name">{game.name}</span>
                        </li>
                    ))}
                </ul>
            )}
        </div>
    );
};

export default SearchBar;
