import React from 'react';
import { Route, Routes, Navigate } from 'react-router-dom';
import { useAuth0 } from '@auth0/auth0-react';
import LandingPage from './components/LandingPage';
import Dashboard from './components/Dashboard';
import GameDetails from './components/GameDetails';
import Loading from './components/Loading';
import AddGame from './components/AddGame';
import Library from './components/Library';
import NowPlaying from './components/NowPlaying';

function App() {
  const { isLoading, isAuthenticated } = useAuth0();

  if (isLoading) {
    return <Loading />;
  }

  return (
    <div className="App">
      <Routes>
        <Route 
          path="/" 
          element={isAuthenticated ? <Dashboard /> : <LandingPage />} 
        />
        <Route 
          path="/dashboard" 
          element={isAuthenticated ? <Dashboard /> : <Navigate to="/" replace />} 
        />
        <Route 
          path="/games/:gameId" 
          element={isAuthenticated ? <GameDetails /> : <Navigate to="/" replace />} 
        />
        <Route 
          path="/add-game" 
          element={isAuthenticated ? <AddGame /> : <Navigate to="/" replace />} 
        />
        <Route 
          path="/library" 
          element={isAuthenticated ? <Library /> : <Navigate to="/" replace />} 
        />
        <Route 
          path="/now-playing" 
          element={isAuthenticated ? <NowPlaying /> : <Navigate to="/" replace />} 
        />
      </Routes>
    </div>
  );
}

export default App;