import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { newsletterApi } from '../api';
import './NewsletterDetail.css';

function NewsletterDetail() {
  const { id } = useParams();
  const navigate = useNavigate();
  const [newsletter, setNewsletter] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    loadNewsletter();
  }, [id]);

  const loadNewsletter = async () => {
    setLoading(true);
    setError(null);
    
    try {
      const data = await newsletterApi.getNewsletter(id);
      setNewsletter(data);
    } catch (err) {
      setError('Failed to load newsletter details.');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const getCategoryLabel = (category) => {
    const labels = {
      'product_ai': 'Product & AI',
      'health_fitness': 'Health & Fitness',
      'finance': 'Finance',
      'sahil_bloom': 'Sahil Bloom',
    };
    return labels[category] || category;
  };

  const getCategoryColor = (category) => {
    const colors = {
      'product_ai': '#3498db',
      'health_fitness': '#2ecc71',
      'finance': '#f39c12',
      'sahil_bloom': '#9b59b6',
    };
    return colors[category] || '#95a5a6';
  };

  const formatDate = (dateString) => {
    const date = new Date(dateString);
    return date.toLocaleString('en-US', {
      year: 'numeric',
      month: 'long',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
    });
  };

  if (loading) {
    return (
      <div className="loading">
        <div className="spinner"></div>
        <span>Loading newsletter...</span>
      </div>
    );
  }

  if (error || !newsletter) {
    return (
      <div className="error">
        <h3>Error</h3>
        <p>{error || 'Newsletter not found'}</p>
        <button onClick={() => navigate('/')}>← Back to List</button>
      </div>
    );
  }

  return (
    <div className="newsletter-detail">
      <button onClick={() => navigate('/')} className="back-button">
        ← Back to List
      </button>

      <div className="detail-header">
        <div className="detail-badges">
          <span
            className="category-badge"
            style={{ backgroundColor: getCategoryColor(newsletter.category) }}
          >
            {getCategoryLabel(newsletter.category)}
          </span>
          <span className="platform-badge">{newsletter.platform}</span>
          {newsletter.needs_review && (
            <span className="review-badge">⚠️ Needs Review</span>
          )}
        </div>

        <h1 className="detail-title">{newsletter.title || newsletter.subject}</h1>
        
        <div className="detail-meta">
          <div className="meta-item">
            <span className="meta-label">From:</span>
            <span className="meta-value">{newsletter.sender_name}</span>
          </div>
          <div className="meta-item">
            <span className="meta-label">Email:</span>
            <span className="meta-value">{newsletter.sender_email}</span>
          </div>
          <div className="meta-item">
            <span className="meta-label">Date:</span>
            <span className="meta-value">{formatDate(newsletter.date)}</span>
          </div>
        </div>
      </div>

      <div className="detail-content">
        {newsletter.sections && newsletter.sections.length > 0 ? (
          <div className="sections">
            <h2>Sections</h2>
            {newsletter.sections.map((section, index) => (
              <div key={index} className="section">
                <h3>{section.heading}</h3>
                <p>{section.content || section.items?.join(' • ')}</p>
              </div>
            ))}
          </div>
        ) : null}

        <div className="full-content">
          <h2>Full Content</h2>
          <div className="content-text">
            {newsletter.parsed_content}
          </div>
        </div>

        {newsletter.links && newsletter.links.length > 0 && (
          <div className="links-section">
            <h2>Links ({newsletter.links.length})</h2>
            <ul className="links-list">
              {newsletter.links.slice(0, 20).map((link, index) => (
                <li key={index}>
                  <a href={link.url} target="_blank" rel="noopener noreferrer">
                    {link.text || link.url}
                  </a>
                </li>
              ))}
              {newsletter.links.length > 20 && (
                <li className="more-links">
                  ... and {newsletter.links.length - 20} more links
                </li>
              )}
            </ul>
          </div>
        )}

        {newsletter.metadata && Object.keys(newsletter.metadata).length > 0 && (
          <div className="metadata-section">
            <h2>Metadata</h2>
            <pre>{JSON.stringify(newsletter.metadata, null, 2)}</pre>
          </div>
        )}
      </div>
    </div>
  );
}

export default NewsletterDetail;
