import React from 'react';
import Dashboard from './components/Dashboard';
import CloudTest from './components/CloudTest';
import './App.css';

function App() {
  return (
    <div className="App">
      <CloudTest />
      <Dashboard />
    </div>
  );
}

export default App;