import React from 'react';
import { useAuth0 } from '@auth0/auth0-react';
import './LandingPage.css';

const LandingPage = () => {
  const { loginWithRedirect, isAuthenticated } = useAuth0();

  return (
    <div className="landing-page">
      <div className="landing-content">
        <h1>Welcome to Kestrel</h1>
        <p>Your game indexing and tracking app</p>
        {!isAuthenticated && (
          <button className="login-button" onClick={() => loginWithRedirect()}>Log In</button>
        )}
      </div>
    </div>
  );
};

export default LandingPage;
