import React from 'react';
import { Routes, Route, Navigate } from 'react-router-dom';
import { useAuth } from './context/AuthContext';
import AppLayout from './components/layout/AppLayout';

import Login from './pages/Auth/Login';
import Register from './pages/Auth/Register';
import Dashboard from './pages/Dashboard/Dashboard';
import Profile from './pages/Profile/Profile';
import Loans from './pages/Loans/Loans';
import Analysis from './pages/Analysis/Analysis';
import Settlement from './pages/Settlement/Settlement';
import Letters from './pages/Letters/Letters';
import History from './pages/History/History';
import BorrowerRights from './pages/Rights/BorrowerRights';
import NotFound from './pages/NotFound';

function ProtectedRoute({ children }) {
  const { isAuthenticated, isLoading } = useAuth();
  
  if (isLoading) return <div className="loading-screen">Loading...</div>;
  if (!isAuthenticated) return <Navigate to="/login" replace />;
  
  return children;
}

export default function App() {
  const { isAuthenticated } = useAuth();

  return (
    <Routes>
      <Route path="/" element={isAuthenticated ? <Navigate to="/dashboard" replace /> : <Navigate to="/login" replace />} />
      <Route path="/login" element={<Login />} />
      <Route path="/register" element={<Register />} />
      
      <Route element={<ProtectedRoute><AppLayout /></ProtectedRoute>}>
        <Route path="/dashboard" element={<Dashboard />} />
        <Route path="/profile" element={<Profile />} />
        <Route path="/loans" element={<Loans />} />
        <Route path="/analysis" element={<Analysis />} />
        <Route path="/settlement" element={<Settlement />} />
        <Route path="/letters" element={<Letters />} />
        <Route path="/history" element={<History />} />
        <Route path="/rights" element={<BorrowerRights />} />
      </Route>

      <Route path="*" element={<NotFound />} />
    </Routes>
  );
}
