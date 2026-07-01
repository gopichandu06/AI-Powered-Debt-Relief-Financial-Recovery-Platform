import React from 'react';
import { Link } from 'react-router-dom';
import { AlertCircle } from 'lucide-react';

export default function NotFound() {
  return (
    <div className="page-container animate-fade-in" style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', height: '100vh' }}>
      <AlertCircle size={64} style={{ color: 'var(--accent-danger)', marginBottom: '1rem' }} />
      <h1 className="page-title">404 - Page Not Found</h1>
      <p className="page-subtitle" style={{ marginBottom: '2rem' }}>The page you are looking for does not exist.</p>
      <Link to="/dashboard" className="btn btn-primary">Go to Dashboard</Link>
    </div>
  );
}
