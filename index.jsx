import React, { useState } from 'react';
import ReactDOM from 'react-dom/client';
import './style.css';
import axios from 'axios';

const App = () => {
  const [form, setForm] = useState({
    shirtSize: '',
    gender: '',
    channel: '',
    country: '',
    minPrice: 0,
    maxPrice: 5000,
    query: ''
  });

  const [results, setResults] = useState([]);
  const [loading, setLoading] = useState(false);

  const update = (key, val) => setForm({ ...form, [key]: val });

  const handleSubmit = async () => {
    setLoading(true);
    const res = await axios.post('/api/search', form);
    setResults(res.data.results);
    setLoading(false);
  };

  return (
    <div className="main">
      <h1>🧠 AI Clothing Finder</h1>

      <label>Shirt Size:
        <select onChange={e => update("shirtSize", e.target.value)}>
          <option value="">Select</option><option>XS</option><option>S</option><option>M</option><option>L</option><option>XL</option>
        </select>
      </label>

      <label>Gender:
        <select onChange={e => update("gender", e.target.value)}>
          <option value="">Select</option><option>Male</option><option>Female</option><option>Unisex</option><option>Kids</option>
        </select>
      </label>

      <label>Shopping Preference:
        <select onChange={e => update("channel", e.target.value)}>
          <option value="">Select</option><option>Online</option><option>In Person</option><option>Both</option>
        </select>
      </label>

      <label>Country:
        <input type="text" placeholder="Start typing..." onChange={e => update("country", e.target.value)} />
      </label>

      <label>Price Range:
        <input type="number" value={form.minPrice} onChange={e => update("minPrice", e.target.value)} /> to
        <input type="number" value={form.maxPrice} onChange={e => update("maxPrice", e.target.value)} />
      </label>

      <label>What are you looking for?
        <input type="text" placeholder="e.g. black hoodie" onChange={e => update("query", e.target.value)} />
      </label>

      <button onClick={handleSubmit} disabled={loading}>{loading ? 'Searching...' : 'Search'}</button>

      {results.length > 0 && (
        <div className="results">
          {results.map((item, i) => (
            <div key={i} className="result">
              <a href={item.link} target="_blank" rel="noreferrer">
                <strong>{item.name}</strong><br />
                Size: {item.size} — ${item.price}
              </a>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};

ReactDOM.createRoot(document.getElementById('root')).render(<App />);
