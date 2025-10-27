/**
 * Dev Progress Page
 *
 * Simple visual dashboard showing PaiiD app construction progress
 * For non-technical users to track how the app is being built
 */

import { useEffect } from 'react';

export default function ProgressPage() {

  useEffect(() => {
    // Redirect to the HTML dashboard file
    window.location.href = '/PROGRESS_DASHBOARD.html';
  }, []);

  return (
    <div style={{
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'center',
      minHeight: '100vh',
      background: 'linear-gradient(135deg, #0f172a 0%, #1e293b 100%)',
      color: '#fff',
      fontFamily: 'system-ui, sans-serif'
    }}>
      <div style={{ textAlign: 'center' }}>
        <h1 style={{
          fontSize: '2em',
          marginBottom: '20px',
          background: 'linear-gradient(135deg, #10b981 0%, #059669 100%)',
          WebkitBackgroundClip: 'text',
          WebkitTextFillColor: 'transparent'
        }}>
          Loading Progress Dashboard...
        </h1>
        <p style={{ color: '#94a3b8' }}>Redirecting to app progress tracker</p>
      </div>
    </div>
  );
}
