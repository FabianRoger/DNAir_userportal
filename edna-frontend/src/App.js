import React from 'react';
import ProjectSummary from './components/ProjectSummary';
import CloudTest from './components/CloudTest';
import './App.css';

function App() {
  return (
    <div className="App">
      <CloudTest />
      <ProjectSummary />
    </div>
  );
}

export default App;