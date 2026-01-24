import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import Header from './components/Header';
import NewsletterList from './components/NewsletterList';
import NewsletterDetail from './components/NewsletterDetail';
import './App.css';

function App() {
  return (
    <Router>
      <div className="app">
        <Header />
        <main className="main-content">
          <Routes>
            <Route path="/" element={<NewsletterList />} />
            <Route path="/newsletter/:id" element={<NewsletterDetail />} />
          </Routes>
        </main>
      </div>
    </Router>
  );
}

export default App;
