import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { newsletterApi } from '../api';
import './SummaryView.css';

function SummaryView() {
  const [summary, setSummary] = useState(null);
  const [briefing, setBriefing] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [useAi, setUseAi] = useState(true);
  const [showBriefing, setShowBriefing] = useState(false);
  const [loadingBriefing, setLoadingBriefing] = useState(false);
  const [selectedDate, setSelectedDate] = useState(
    new Date().toISOString().split('T')[0]
  );
  const navigate = useNavigate();

  useEffect(() => {
    fetchSummary();
    setBriefing(null);
    setShowBriefing(false);
  }, [selectedDate, useAi]);

  const fetchSummary = async () => {
    setLoading(true);
    setError(null);
    try {
      const data = useAi
        ? await newsletterApi.getAiDailySummary(selectedDate)
        : await newsletterApi.getSummary(selectedDate);
      setSummary(data);
    } catch (err) {
      const message = err.response?.data?.detail || 'Failed to load summary. Please try again.';
      setError(message);
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const fetchBriefing = async () => {
    setLoadingBriefing(true);
    try {
      const data = await newsletterApi.getDailyBriefing(selectedDate);
      setBriefing(data);
      setShowBriefing(true);
    } catch (err) {
      const message = err.response?.data?.detail || 'Failed to generate briefing.';
      setError(message);
    } finally {
      setLoadingBriefing(false);
    }
  };

  const categoryOrder = ['product_ai', 'health_fitness', 'finance', 'sahil_bloom'];

  if (loading) {
    return (
      <div className="summary-view">
        <div className="loading">
          {useAi ? 'AI is reading your newsletters...' : 'Loading summary...'}
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="summary-view">
        <div className="error">{error}</div>
        <button onClick={() => setUseAi(false)} className="fallback-button">
          Try without AI
        </button>
      </div>
    );
  }

  // Render AI summary (one per category)
  const renderAiSummary = () => (
    <div className="categories-container">
      {categoryOrder.map((catKey) => {
        const category = summary.categories[catKey];
        if (!category) return null;

        return (
          <div key={catKey} className="category-section ai-category">
            <div className="category-header">
              <h3 className="category-title">
                {category.display_name}
                <span className="newsletter-count">
                  ({category.newsletter_count} newsletters)
                </span>
              </h3>
              {category.ai_generated && <span className="ai-badge-small">AI Summary</span>}
            </div>

            {category.summary && (
              <div className="category-summary">
                <p>{category.summary}</p>
              </div>
            )}

            {category.key_points && category.key_points.length > 0 && (
              <div className="key-points-section">
                <h4>Key Points</h4>
                <ul className="key-points-list">
                  {category.key_points.map((point, i) => (
                    <li key={i}>{point}</li>
                  ))}
                </ul>
              </div>
            )}

            {category.newsletters && category.newsletters.length > 0 && (
              <div className="newsletter-sources">
                <h4>Sources</h4>
                <div className="source-chips">
                  {category.newsletters.map((nl, i) => (
                    <div key={i} className="source-chip">
                      <span className="source-name">{nl.sender_name}</span>
                      {nl.one_liner && (
                        <span className="source-liner">{nl.one_liner}</span>
                      )}
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>
        );
      })}

      {/* Uncategorized */}
      {summary.categories.uncategorized && (
        <div className="category-section ai-category">
          <div className="category-header">
            <h3 className="category-title">
              Uncategorized
              <span className="newsletter-count">
                ({summary.categories.uncategorized.newsletter_count} newsletters)
              </span>
            </h3>
          </div>
          {summary.categories.uncategorized.summary && (
            <div className="category-summary">
              <p>{summary.categories.uncategorized.summary}</p>
            </div>
          )}
        </div>
      )}
    </div>
  );

  // Render basic summary (per newsletter cards)
  const renderBasicSummary = () => (
    <div className="categories-container">
      {categoryOrder.map((catKey) => {
        const category = summary.categories[catKey];
        if (!category) return null;

        return (
          <div key={catKey} className="category-section">
            <h3 className="category-title">
              {category.display_name}
              <span className="newsletter-count">
                ({category.newsletters.length})
              </span>
            </h3>
            <div className="newsletter-cards">
              {category.newsletters.map((nl) => (
                <div
                  key={nl.id}
                  className="newsletter-card"
                  onClick={() => navigate(`/newsletter/${nl.id}`)}
                >
                  <div className="card-header">
                    <span className="sender">{nl.sender_name}</span>
                    <span className="platform">{nl.platform}</span>
                  </div>
                  <h4 className="card-title">{nl.title || nl.subject}</h4>
                  {nl.parsed_content && (
                    <p className="card-preview">{nl.parsed_content}</p>
                  )}
                </div>
              ))}
            </div>
          </div>
        );
      })}
    </div>
  );

  return (
    <div className="summary-view">
      <div className="summary-header">
        <h2>Daily Newsletter Summary</h2>
        <div className="header-controls">
          <div className="ai-toggle">
            <label className="toggle-label">
              <input
                type="checkbox"
                checked={useAi}
                onChange={(e) => setUseAi(e.target.checked)}
              />
              <span className="toggle-text">AI Summary</span>
            </label>
          </div>
          <div className="date-picker">
            <input
              type="date"
              value={selectedDate}
              onChange={(e) => setSelectedDate(e.target.value)}
            />
          </div>
        </div>
      </div>

      <div className="summary-stats">
        <span className="stat-item">
          <strong>{summary.total_newsletters}</strong> newsletters on {summary.date}
          {summary.ai_generated && <span className="ai-badge">AI Generated</span>}
        </span>
        {summary.total_newsletters > 0 && useAi && (
          <button
            onClick={fetchBriefing}
            disabled={loadingBriefing}
            className="briefing-button"
          >
            {loadingBriefing ? 'Generating...' : 'Generate Podcast Script'}
          </button>
        )}
      </div>

      {showBriefing && briefing && (
        <div className="briefing-section">
          <div className="briefing-header">
            <h3>Daily Briefing</h3>
            <button onClick={() => setShowBriefing(false)} className="close-button">
              Close
            </button>
          </div>
          <div className="briefing-content">
            {briefing.briefing.split('\n').map((paragraph, i) => (
              paragraph.trim() && <p key={i}>{paragraph}</p>
            ))}
          </div>
        </div>
      )}

      {summary.total_newsletters === 0 ? (
        <div className="no-newsletters">
          <p>No newsletters found for this date.</p>
          <p>Try selecting a different date or extract new newsletters.</p>
        </div>
      ) : (
        useAi ? renderAiSummary() : renderBasicSummary()
      )}
    </div>
  );
}

export default SummaryView;
