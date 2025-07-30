import React, { useState } from 'react';
import axios from 'axios';

const countries = [
  "Afghanistan", "Albania", "Algeria", "Andorra", "Angola", "Antigua and Barbuda", "Argentina", "Armenia", "Australia", "Austria",
  "Azerbaijan", "Bahamas", "Bahrain", "Bangladesh", "Barbados", "Belarus", "Belgium", "Belize", "Benin", "Bhutan",
  "Bolivia", "Bosnia and Herzegovina", "Botswana", "Brazil", "Brunei", "Bulgaria", "Burkina Faso", "Burundi", "Cabo Verde", "Cambodia",
  "Cameroon", "Canada", "Central African Republic", "Chad", "Chile", "China", "Colombia", "Comoros", "Congo (Brazzaville)", "Congo (Kinshasa)",
  "Costa Rica", "Croatia", "Cuba", "Cyprus", "Czech Republic", "Denmark", "Djibouti", "Dominica", "Dominican Republic", "Ecuador",
  "Egypt", "El Salvador", "Equatorial Guinea", "Eritrea", "Estonia", "Eswatini", "Ethiopia", "Fiji", "Finland", "France",
  "Gabon", "Gambia", "Georgia", "Germany", "Ghana", "Greece", "Grenada", "Guatemala", "Guinea", "Guinea-Bissau",
  "Guyana", "Haiti", "Honduras", "Hungary", "Iceland", "India", "Indonesia", "Iran", "Iraq", "Ireland",
  "Israel", "Italy", "Ivory Coast", "Jamaica", "Japan", "Jordan", "Kazakhstan", "Kenya", "Kiribati", "Korea, North",
  "Korea, South", "Kosovo", "Kuwait", "Kyrgyzstan", "Laos", "Latvia", "Lebanon", "Lesotho", "Liberia", "Libya",
  "Liechtenstein", "Lithuania", "Luxembourg", "Madagascar", "Malawi", "Malaysia", "Maldives", "Mali", "Malta", "Marshall Islands",
  "Mauritania", "Mauritius", "Mexico", "Micronesia", "Moldova", "Monaco", "Mongolia", "Montenegro", "Morocco", "Mozambique",
  "Myanmar", "Namibia", "Nauru", "Nepal", "Netherlands", "New Zealand", "Nicaragua", "Niger", "Nigeria", "North Macedonia",
  "Norway", "Oman", "Pakistan", "Palau", "Palestine", "Panama", "Papua New Guinea", "Paraguay", "Peru", "Philippines",
  "Poland", "Portugal", "Qatar", "Romania", "Russia", "Rwanda", "Saint Kitts and Nevis", "Saint Lucia", "Saint Vincent and the Grenadines", "Samoa",
  "San Marino", "Sao Tome and Principe", "Saudi Arabia", "Senegal", "Serbia", "Seychelles", "Sierra Leone", "Singapore", "Slovakia", "Slovenia",
  "Solomon Islands", "Somalia", "South Africa", "South Sudan", "Spain", "Sri Lanka", "Sudan", "Suriname", "Sweden", "Switzerland",
  "Syria", "Taiwan", "Tajikistan", "Tanzania", "Thailand", "Timor-Leste", "Togo", "Tonga", "Trinidad and Tobago", "Tunisia",
  "Turkey", "Turkmenistan", "Tuvalu", "Uganda", "Ukraine", "United Arab Emirates", "United Kingdom", "United States", "Uruguay", "Uzbekistan",
  "Vanuatu", "Vatican City", "Venezuela", "Vietnam", "Yemen", "Zambia", "Zimbabwe"
];

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
  const [error, setError] = useState('');

  const handleSubmit = async () => {
    setLoading(true);
    setError('');
    setResults([]);

    try {
      const res = await axios.post('/api/search', formData);
      if (res.data.results && Array.isArray(res.data.results)) {
        setResults(res.data.results);
      } else {
        setError("AI responded with no results.");
      }
    } catch (err) {
      const msg = err.response?.data?.message || "Something went wrong with the AI request.";
      setError(msg);
      console.error("Search error:", err.response?.data || err.message);
    }

    setLoading(false);
  };

  return (
    <div className="p-6 max-w-3xl mx-auto space-y-4 font-sans">
      <h1 className="text-2xl font-bold">AI Clothing Finder</h1>

      <div>
        <label>Shirt Size:</label>
        <select onChange={e => setFormData({ ...formData, shirtSize: e.target.value })}>
          <option value="">Select</option>
          <option>XS</option><option>S</option><option>M</option><option>L</option><option>XL</option>
        </select>
      </div>

      <div>
        <label>Gender:</label>
        <select onChange={e => setFormData({ ...formData, gender: e.target.value })}>
          <option value="">Select</option>
          <option>Male</option><option>Female</option><option>Unisex</option><option>Kids</option>
        </select>
      </div>

      <div>
        <label>Shopping Preference:</label>
        <select onChange={e => setFormData({ ...formData, channel: e.target.value })}>
          <option value="">Select</option>
          <option>Online</option><option>In Person</option><option>Both</option>
        </select>
      </div>

      <div>
        <label>Country:</label>
        <input
          type="text"
          list="countries"
          placeholder="Start typing..."
          value={formData.country}
          onChange={e => setFormData({ ...formData, country: e.target.value })}
        />
        <datalist id="countries">
          {countries.map((c) => <option key={c} value={c} />)}
        </datalist>
      </div>

      <div>
        <label>Price Range:</label>
        <input
          type="range"
          min="0"
          max="5000"
          value={formData.minPrice}
          onChange={e => setFormData({ ...formData, minPrice: parseInt(e.target.value) })}
        />
        <span>Min: ${formData.minPrice}</span>
        <input
          type="range"
          min="0"
          max="5000"
          value={formData.maxPrice}
          onChange={e => setFormData({ ...formData, maxPrice: parseInt(e.target.value) })}
        />
        <span>Max: ${formData.maxPrice}</span>
      </div>

      <div>
        <label>What are you looking for?</label>
        <input
          type="text"
          value={formData.query}
          placeholder="e.g. black hoodie, soccer jersey"
          onChange={e => setFormData({ ...formData, query: e.target.value })}
        />
      </div>

      <button className="bg-blue-500 text-white px-4 py-2" onClick={handleSubmit} disabled={loading}>
        {loading ? "Searching..." : "Find Clothes"}
      </button>

      {error && (
        <div className="text-red-600 font-semibold mt-4">
          ⚠️ {error}
        </div>
      )}

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
