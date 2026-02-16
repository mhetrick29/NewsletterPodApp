import React, { useState } from 'react';
import { newsletterApi } from '../api';
import './DailyFlow.css';

const today = () => new Date().toISOString().slice(0, 10);
const tenDaysAgo = () => {
  const d = new Date();
  d.setDate(d.getDate() - 10);
  return d.toISOString().slice(0, 10);
};

export default function DailyFlow() {
  const [step, setStep] = useState('welcome'); // welcome | fetching | fetched | generating | done
  const [date, setDate] = useState(today());
  const [newsletters, setNewsletters] = useState([]);
  const [stats, setStats] = useState(null);
  const [error, setError] = useState(null);

  const reset = () => {
    setStep('welcome');
    setDate(today());
    setNewsletters([]);
    setStats(null);
    setError(null);
  };

  const handleFetch = async () => {
    setError(null);
    setStep('fetching');
    try {
      const extractResult = await newsletterApi.extractNewsletters(date);
      setStats(extractResult.stats);

      const listResult = await newsletterApi.getNewsletters(date);
      setNewsletters(listResult.newsletters);
      setStep('fetched');
    } catch (e) {
      setError(e.response?.data?.detail || e.message);
      setStep('welcome');
    }
  };

  const handleGeneratePdf = async () => {
    setError(null);
    setStep('generating');
    try {
      await newsletterApi.downloadSummaryPdf(date);
      setStep('done');
    } catch (e) {
      setError(e.response?.data?.detail || e.message);
      setStep('fetched');
    }
  };

  return (
    <div className="daily-flow">
      <h1 className="daily-flow__title">Newsletter Summary</h1>

      {error && <div className="daily-flow__error">{error}</div>}

      {/* Step 1: Welcome — pick a date and fetch */}
      {step === 'welcome' && (
        <div className="daily-flow__card">
          <label className="daily-flow__label" htmlFor="date-picker">
            Choose a date
          </label>
          <input
            id="date-picker"
            className="daily-flow__date"
            type="date"
            value={date}
            min={tenDaysAgo()}
            max={today()}
            onChange={(e) => setDate(e.target.value)}
          />
          <button className="daily-flow__btn" onClick={handleFetch}>
            Fetch Newsletters for {date}
          </button>
        </div>
      )}

      {/* Step 2: Fetching */}
      {step === 'fetching' && (
        <div className="daily-flow__card daily-flow__card--loading">
          <div className="daily-flow__spinner" />
          <p>Fetching newsletters for {date}...</p>
        </div>
      )}

      {/* Step 3: Fetched — show results, offer PDF */}
      {step === 'fetched' && (
        <div className="daily-flow__card">
          <h2 className="daily-flow__subtitle">
            {newsletters.length} newsletter{newsletters.length !== 1 ? 's' : ''} found for {date}
          </h2>

          {newsletters.length > 0 && (
            <ul className="daily-flow__list">
              {newsletters.map((nl) => (
                <li key={nl.id} className="daily-flow__list-item">
                  <span className="daily-flow__sender">{nl.sender_name}</span>
                  <span className="daily-flow__subject">{nl.subject}</span>
                </li>
              ))}
            </ul>
          )}

          {newsletters.length > 0 ? (
            <button className="daily-flow__btn daily-flow__btn--accent" onClick={handleGeneratePdf}>
              Generate PDF Summary
            </button>
          ) : (
            <button className="daily-flow__btn" onClick={reset}>
              Try a different date
            </button>
          )}
        </div>
      )}

      {/* Step 4: Generating PDF */}
      {step === 'generating' && (
        <div className="daily-flow__card daily-flow__card--loading">
          <div className="daily-flow__spinner" />
          <p>Generating PDF summary (this may take a minute)...</p>
        </div>
      )}

      {/* Step 5: Done */}
      {step === 'done' && (
        <div className="daily-flow__card daily-flow__card--success">
          <h2 className="daily-flow__subtitle">PDF Downloaded!</h2>
          <p>Your newsletter summary for {date} has been saved.</p>
          <button className="daily-flow__btn" onClick={reset}>
            Start Over
          </button>
        </div>
      )}
    </div>
  );
}
