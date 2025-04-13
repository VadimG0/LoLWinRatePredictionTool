import './App.css';
import React, { useState } from 'react';
import axios from 'axios';


function App() {
  const [name, setName] = useState('');
  const [greeting, setGreeting] = useState('');

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      const response = await axios.get(`http://localhost:8000/greet/${name}`);
      setGreeting(response.data.message);
    } catch (err) {
      console.log(err);
      setGreeting('Something went wrong!');
    }
  }

  
  return (
    <div className="App">
      <h1>Greeting Simulator</h1>
      <form onSubmit={handleSubmit}>
        <input
          type="text" 
          value={name}
          onChange={(e) => setName(e.target.value)}
          placeholder="Enter your name"
        />
        <button type="submit">Submit</button> 
      </form>
      {/* conditional? if greeting exist */}
      {greeting && <p className="greeting">{greeting}</p>}
    </div>
  );
}

export default App;
