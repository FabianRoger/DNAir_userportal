import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { AlertTriangle, CheckCircle, XCircle } from 'lucide-react';

const CloudTest = () => {
  const [status, setStatus] = useState('testing');
  const [message, setMessage] = useState('Testing cloud connection...');
  const [debugInfo, setDebugInfo] = useState({
    healthCheck: null,
    usersFetch: null,
    projectsFetch: null
  });
  
  useEffect(() => {
    const testConnection = async () => {
      const apiUrl = process.env.REACT_APP_API_URL;
      setDebugInfo(prev => ({ ...prev, apiUrl }));
      console.log('Testing connection to:', apiUrl);
      
      try {
        // Test health endpoint
        const healthResponse = await axios.get(`${apiUrl}/health`);
        setDebugInfo(prev => ({ ...prev, healthCheck: healthResponse.data }));
        
        if (healthResponse.data.status === 'healthy') {
          setMessage('Backend health check passed');
          
          // Test users endpoint
          try {
            const usersResponse = await axios.get(`${apiUrl}/users/`);
            setDebugInfo(prev => ({ ...prev, usersFetch: usersResponse.data }));
            setMessage('Connected to backend and fetched users');
            setStatus('success');
            
            // Test projects endpoint with first user if available
            if (usersResponse.data.length > 0) {
              try {
                const projectsResponse = await axios.get(`${apiUrl}/projects/${usersResponse.data[0].id}`);
                setDebugInfo(prev => ({ ...prev, projectsFetch: projectsResponse.data }));
                setMessage('All endpoints tested successfully');
              } catch (err) {
                console.error('Projects fetch error:', err);
                setStatus('warning');
                setMessage('Users endpoint working, but projects fetch failed');
              }
            }
          } catch (err) {
            console.error('Users fetch error:', err);
            setStatus('warning');
            setMessage('Health check passed but users fetch failed');
          }
        } else {
          setStatus('error');
          setMessage('Backend health check failed');
        }
      } catch (err) {
        console.error('Health check error:', err);
        setStatus('error');
        setMessage(`Failed to connect to backend: ${err.message}`);
      }
    };
    
    testConnection();
  }, []);

  const statusColors = {
    testing: 'bg-blue-100 text-blue-800',
    success: 'bg-green-100 text-green-800',
    warning: 'bg-yellow-100 text-yellow-800',
    error: 'bg-red-100 text-red-800'
  };

  const StatusIcon = () => {
    switch (status) {
      case 'success':
        return <CheckCircle className="w-5 h-5" />;
      case 'error':
        return <XCircle className="w-5 h-5" />;
      case 'warning':
        return <AlertTriangle className="w-5 h-5" />;
      default:
        return <AlertTriangle className="w-5 h-5 animate-spin" />;
    }
  };

  return (
    <div className="fixed top-4 right-4 max-w-md z-50">
      <div className={`p-4 rounded-lg shadow-lg ${statusColors[status]}`}>
        <div className="flex items-center gap-3">
          <StatusIcon />
          <span className="text-sm font-medium">{message}</span>
        </div>
        {(status === 'error' || status === 'warning') && (
          <div className="mt-2 p-2 bg-white bg-opacity-50 rounded text-xs font-mono whitespace-pre-wrap">
            {JSON.stringify(debugInfo, null, 2)}
          </div>
        )}
      </div>
    </div>
  );
};

export default CloudTest;