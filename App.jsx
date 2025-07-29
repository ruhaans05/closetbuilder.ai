import React, { useState } from 'react';
import axios from 'axios';

const countries = ["United States", "India", "Canada", "Germany", "Brazil", "Japan"]; // Example list

export default function App() {
  const [formData, setFormData] = useState({
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

  const handleSubmit = async () => {
    setLoading(true);
    const res = await axios.post('/api/search', formData);
    setResults(res.data.results);
    setLoading(false);
  };

  return (
    <div className="p-6 max-w-3xl mx-auto space-y-4 font-sans">
      <h1 className="text-2xl font-bold">AI Clothing Finder</h1>

      <div>
        <label>Shirt Size:</label>
        <select onChange={e => setFormData({...formData, shirtSize: e.target.value})}>
          <option value="">Select</option>
          <option>XS</option><option>S</option><option>M</option><option>L</option><option>XL</option>
        </select>
      </div>

      <div>
        <label>Gender:</label>
        <select onChange={e => setFormData({...formData, gender: e.target.value})}>
          <option value="">Select</option>
          <option>Male</option><option>Female</option><option>Unisex</option><option>Kids</option>
        </select>
      </div>

      <div>
        <label>Shopping Preference:</label>
        <select onChange={e => setFormData({...formData, channel: e.target.value})}>
          <option value="">Select</option>
          <option>Online</option><option>In Person</option><option>Both</option>
        </select>
      </div>

      <div>
        <label>Country:</label>
        <input list="countries" onChange={e => setFormData({...formData, country: e.target.value})} />
        <datalist id="countries">
          {countries.map(c => <option key={c} value={c} />)}
        </datalist>
      </div>

      <div>
        <label>Price Range:</label>
        <input type="range" min="0" max="5000" value={formData.minPrice} 
               onChange={e => setFormData({...formData, minPrice: parseInt(e.target.value)})} />
        <span>Min: ${formData.minPrice}</span>
        <input type="range" min="0" max="5000" value={formData.maxPrice} 
               onChange={e => setFormData({...formData, maxPrice: parseInt(e.target.value)})} />
        <span>Max: ${formData.maxPrice}</span>
      </div>

      <div>
        <label>What are you looking for?</label>
        <input type="text" value={formData.query}
               onChange={e => setFormData({...formData, query: e.target.value})} />
      </div>

      <button className="bg-blue-500 text-white px-4 py-2" onClick={handleSubmit}>
        {loading ? "Searching..." : "Find Clothes"}
      </button>

      <div className="pt-6 space-y-4">
        {results.map((item, idx) => (
          <div key={idx} className="border p-4 rounded shadow-sm">
            <a href={item.link} target="_blank" rel="noopener noreferrer">
              <p className="font-semibold">{item.name}</p>
              <p>{item.size} - ${item.price}</p>
            </a>
          </div>
        ))}
      </div>
    </div>
  );
}
