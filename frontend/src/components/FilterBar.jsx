import React from 'react';
import './FilterBar.css';

function FilterBar({ categories, filters, onFilterChange }) {
  const handleCategoryChange = (e) => {
    onFilterChange({
      ...filters,
      category: e.target.value,
    });
  };

  const handleStartDateChange = (e) => {
    onFilterChange({
      ...filters,
      startDate: e.target.value,
    });
  };

  const handleEndDateChange = (e) => {
    onFilterChange({
      ...filters,
      endDate: e.target.value,
    });
  };

  const handleReset = () => {
    onFilterChange({
      category: '',
      startDate: '',
      endDate: '',
    });
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

  const hasActiveFilters = filters.category || filters.startDate || filters.endDate;

  return (
    <div className="filter-bar">
      <div className="filter-group">
        <label htmlFor="category">Category:</label>
        <select
          id="category"
          value={filters.category}
          onChange={handleCategoryChange}
          className="filter-select"
        >
          <option value="">All Categories</option>
          {categories.map((cat) => (
            <option key={cat.category} value={cat.category}>
              {getCategoryLabel(cat.category)} ({cat.count})
            </option>
          ))}
        </select>
      </div>

      <div className="filter-group">
        <label htmlFor="start-date">From:</label>
        <input
          id="start-date"
          type="date"
          value={filters.startDate}
          onChange={handleStartDateChange}
          className="filter-input"
        />
      </div>

      <div className="filter-group">
        <label htmlFor="end-date">To:</label>
        <input
          id="end-date"
          type="date"
          value={filters.endDate}
          onChange={handleEndDateChange}
          className="filter-input"
        />
      </div>

      {hasActiveFilters && (
        <button onClick={handleReset} className="reset-button">
          ✕ Clear Filters
        </button>
      )}
    </div>
  );
}

export default FilterBar;
