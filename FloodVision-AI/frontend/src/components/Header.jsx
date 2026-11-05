import React from 'react';

export default function Header() {
  return (
    <header style={{
      background: 'rgba(250, 251, 248, 0.95)',
      backdropFilter: 'blur(8px)',
      borderBottom: '1px solid var(--border-subtle)',
      position: 'sticky',
      top: 0,
      zIndex: 100
    }}>
      <div className="container" style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', height: '72px' }}>
        <a href="#" style={{ display: 'flex', alignItems: 'center', gap: '10px', textDecoration: 'none', color: 'var(--text-main)' }}>
          <div style={{
            width: '36px',
            height: '36px',
            background: 'var(--primary)',
            borderRadius: '8px',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            color: '#FFFFFF'
          }}>
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.2" strokeLinecap="round" strokeLinejoin="round">
              <path d="M12 2.69l5.66 5.66a8 8 0 1 1-11.31 0z"></path>
            </svg>
          </div>
          <div>
            <div style={{ fontSize: '18px', fontWeight: 700, letterSpacing: '-0.02em', color: 'var(--text-main)' }}>
              FloodVision AI
            </div>
            <div style={{ fontSize: '11px', fontWeight: 600, color: 'var(--text-muted)', letterSpacing: '0.04em', textTransform: 'uppercase' }}>
              Environmental Image Intelligence
            </div>
          </div>
        </a>

        <nav style={{ display: 'flex', alignItems: 'center', gap: '28px' }}>
          <a href="#overview" style={{ fontSize: '14px', fontWeight: 500, color: 'var(--text-muted)', textDecoration: 'none', transition: 'color 0.15s ease' }}>Overview</a>
          <a href="#how-it-works" style={{ fontSize: '14px', fontWeight: 500, color: 'var(--text-muted)', textDecoration: 'none', transition: 'color 0.15s ease' }}>How It Works</a>
          <a href="#workspace" style={{ fontSize: '14px', fontWeight: 500, color: 'var(--text-muted)', textDecoration: 'none', transition: 'color 0.15s ease' }}>Image Analysis</a>
          <a href="#insights" style={{ fontSize: '14px', fontWeight: 500, color: 'var(--text-muted)', textDecoration: 'none', transition: 'color 0.15s ease' }}>Insights</a>
          <a href="#about" style={{ fontSize: '14px', fontWeight: 500, color: 'var(--text-muted)', textDecoration: 'none', transition: 'color 0.15s ease' }}>About</a>
          <a href="#creator" style={{ fontSize: '14px', fontWeight: 500, color: 'var(--text-muted)', textDecoration: 'none', transition: 'color 0.15s ease' }}>Creator</a>
        </nav>

        <div>
          <a
            href="#workspace"
            style={{
              fontSize: '13px',
              fontWeight: 600,
              padding: '9px 20px',
              background: 'var(--primary)',
              color: '#FFFFFF',
              borderRadius: '6px',
              textDecoration: 'none',
              transition: 'background-color 0.15s ease',
              display: 'inline-block'
            }}
          >
            Analyze an Image
          </a>
        </div>
      </div>
    </header>
  );
}
