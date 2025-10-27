/**
 * My Account Page
 *
 * Simple visual dashboard showing your trading account performance
 * Clean line graph + big numbers - no technical jargon!
 */

import SimpleFinancialChart from '../components/SimpleFinancialChart';

export default function MyAccountPage() {
  return (
    <div style={{
      minHeight: '100vh',
      background: 'linear-gradient(135deg, #0f172a 0%, #1e293b 100%)',
      padding: '40px 20px',
    }}>
      <div style={{
        maxWidth: '1200px',
        margin: '0 auto',
      }}>
        {/* Header */}
        <div style={{
          textAlign: 'center',
          marginBottom: '40px',
        }}>
          <h1 style={{
            fontSize: '3em',
            background: 'linear-gradient(135deg, #10b981 0%, #059669 100%)',
            WebkitBackgroundClip: 'text',
            WebkitTextFillColor: 'transparent',
            marginBottom: '10px',
          }}>
            💰 My Account
          </h1>
          <p style={{
            color: '#94a3b8',
            fontSize: '1.2em',
          }}>
            How you&apos;re doing
          </p>
        </div>

        {/* Simple Financial Chart */}
        <SimpleFinancialChart />
      </div>
    </div>
  );
}
