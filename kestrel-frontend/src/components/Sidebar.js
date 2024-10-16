import React, { useEffect, useState } from 'react';
import { Link, useLocation } from 'react-router-dom';
import { useAuth0 } from '@auth0/auth0-react';
import './Sidebar.css';
import kestrelLogo from '../assets/kestrel.png';
import gamesIcon from '../assets/game.png';
import adminIcon from '../assets/admin.png';

const Sidebar = ({ isOpen, toggleSidebar }) => {
  const location = useLocation();
  const { isAuthenticated, getAccessTokenSilently } = useAuth0();
  const [userPermissions, setUserPermissions] = useState([]);

  useEffect(() => {
    
    const getUserPermissions = async () => {
      try {
        const token = await getAccessTokenSilently();
        

        // Decode the token
        const [header, payload, signature] = token.split('.');
        const decodedHeader = JSON.parse(atob(header));
        const decodedPayload = JSON.parse(atob(payload));
        
        const permissions = decodedPayload.permissions || [];
        setUserPermissions(permissions);
      } catch (error) {
        console.error('Error getting user permissions', error);
      }
    };

    if (isAuthenticated) {
      getUserPermissions();
    }
  }, [isAuthenticated, getAccessTokenSilently]);

  const hasAdminAccess = () => {
    return userPermissions.includes('post:tags');
  };

  const menuItems = [
    { 
      header: "Games", 
      icon: gamesIcon, 
      items: [
        { to: "/add-game", text: "Add a Game" },
        { to: "/now-playing", text: "Now Playing" },
        { to: "/library", text: "Library" },
        { to: "/advanced-search", text: "Advanced Search" },
        { to: "/recently-added", text: "Recently Added" },
        { to: "/tags", text: "Tags" },
        { to: "/random", text: "Random" },
      ]
    },
    { 
      header: "Admin", 
      icon: adminIcon,
      items: [
        { to: "/add-tag", text: "Add Tag" },
      ],
    },
  ];

  return (
    <div className={`sidebar ${isOpen ? '' : 'closed'}`}>
      <div className="sidebar-header">
        <img src={kestrelLogo} alt="Kestrel Logo" className="sidebar-logo" />
        <span className="sidebar-title">Kestrel</span>
      </div>
      <button className={`sidebar-close ${isOpen ? '' : 'open'}`} onClick={toggleSidebar}>
        {isOpen ? '×' : '>'}
      </button>
      <nav className="sidebar-menu">
        <Link to="/" className={`sidebar-menu-link ${location.pathname === '/' ? 'active' : ''}`}>
          Home
        </Link>
        {menuItems.map((section, sectionIndex) => (
          (section.header !== "Admin" || hasAdminAccess()) && (
            <React.Fragment key={sectionIndex}>
              <div className="sidebar-menu-header">
                {section.icon && <img src={section.icon} alt={`${section.header} icon`} className="sidebar-menu-icon" />}
                {section.header}
              </div>
              <ul>
                {section.items.map((item, itemIndex) => (
                  <li key={itemIndex} className="sidebar-menu-item">
                    <Link 
                      to={item.to} 
                      className={`sidebar-menu-link ${location.pathname === item.to ? 'active' : ''}`}
                    >
                      {item.text}
                    </Link>
                  </li>
                ))}
              </ul>
            </React.Fragment>
          )
        ))}
      </nav>
    </div>
  );
};

export default Sidebar;
