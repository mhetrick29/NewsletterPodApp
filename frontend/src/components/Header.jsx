import React, { useState } from 'react';
import { newsletterApi } from '../api';
import './Header.css';

function Header() {
  const [extracting, setExtracting] = useState(false);
  const [message, setMessage] = useState(null);

  const handleExtract = async () => {
    setExtracting(true);
    setMessage(null);

    try {
      const result = await newsletterApi.extractNewsletters(1, 100);
      setMessage({
        type: 'success',
        text: result.message,
        stats: result.stats,
      });
      
      // Reload page after 2 seconds to show new newsletters
      setTimeout(() => {
        window.location.reload();
      }, 2000);
    } catch (error) {
      setMessage({
        type: 'error',
        text: error.response?.data?.detail || 'Failed to extract newsletters. Make sure you have credentials.json and have authorized the app.',
      });
    } finally {
      setExtracting(false);
    }
  };

  return (
    <header className="header">
      <div className="header-content">
        <div className="header-left">
          <h1>📧 Newsletter Podcast Agent</h1>
          <p className="subtitle">Phase 1: Newsletter Viewer</p>
        </div>
        <div className="header-right">
          <button
            onClick={handleExtract}
            disabled={extracting}
            className="extract-button"
          >
            {extracting ? '🔄 Extracting...' : '📥 Extract Newsletters'}
          </button>
        </div>
      </div>
      
      {message && (
        <div className={`message ${message.type}`}>
          <p>{message.text}</p>
          {message.stats && (
            <div className="stats-summary">
              <span>Fetched: {message.stats.total_fetched}</span>
              <span>New: {message.stats.newly_parsed}</span>
              <span>Already exists: {message.stats.already_exists}</span>
              {message.stats.parse_errors > 0 && (
                <span className="errors">Errors: {message.stats.parse_errors}</span>
              )}
            </div>
          )}
        </div>
      )}
    </header>
  );
}

export default Header;
