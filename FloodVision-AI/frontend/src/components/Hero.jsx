import React from 'react';

export default function Hero({ heroImage }) {
  return (
    <section id="overview" style={{ padding: '72px 0 54px 0', textAlign: 'center' }}>
      <div className="container">
        <div style={{
          display: 'inline-flex',
          alignItems: 'center',
          gap: '8px',
          padding: '6px 14px',
          background: 'var(--highlight-teal)',
          border: '1px solid #C1E8D7',
          borderRadius: '20px',
          fontSize: '12px',
          fontWeight: 600,
          color: 'var(--primary)',
          marginBottom: '24px'
        }}>
          <span style={{ width: '7px', height: '7px', borderRadius: '50%', background: 'var(--primary)' }} />
          <span>Environmental Image Intelligence Platform</span>
        </div>

        <h2 style={{
          fontSize: '48px',
          fontWeight: 800,
          letterSpacing: '-0.03em',
          lineHeight: 1.15,
          color: 'var(--text-main)',
          maxWidth: '820px',
          margin: '0 auto 18px auto'
        }}>
          See the water.<br />Understand the impact.
        </h2>

        <p style={{
          fontSize: '18px',
          fontWeight: 400,
          color: 'var(--text-muted)',
          maxWidth: '680px',
          margin: '0 auto 32px auto',
          lineHeight: 1.6
        }}>
          Transform flood imagery into clear visual insights with intelligent image segmentation and environmental image analysis.
        </p>

        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', gap: '14px', marginBottom: '48px' }}>
          <a
            href="#workspace"
            style={{
              display: 'inline-flex',
              alignItems: 'center',
              gap: '8px',
              padding: '12px 26px',
              background: 'var(--primary)',
              color: '#FFFFFF',
              fontSize: '15px',
              fontWeight: 600,
              borderRadius: '8px',
              textDecoration: 'none',
              boxShadow: 'var(--shadow-sm)'
            }}
          >
            <span>Analyze an Image</span>
            <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.2" strokeLinecap="round" strokeLinejoin="round">
              <line x1="5" y1="12" x2="19" y2="12"></line>
              <polyline points="12 5 19 12 12 19"></polyline>
            </svg>
          </a>
          <a
            href="#how-it-works"
            style={{
              display: 'inline-flex',
              alignItems: 'center',
              gap: '8px',
              padding: '12px 24px',
              background: 'var(--bg-card)',
              color: 'var(--text-main)',
              fontSize: '15px',
              fontWeight: 600,
              borderRadius: '8px',
              textDecoration: 'none',
              border: '1px solid var(--border-subtle)'
            }}
          >
            <span>Explore How It Works</span>
          </a>
        </div>

        {/* Authentic Model Output Showcase */}
        <div style={{
          background: 'var(--bg-card)',
          border: '1px solid var(--border-subtle)',
          borderRadius: '14px',
          padding: '16px',
          boxShadow: 'var(--shadow-lg)',
          maxWidth: '960px',
          margin: '0 auto'
        }}>
          <div style={{
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'space-between',
            paddingBottom: '12px',
            borderBottom: '1px solid var(--border-subtle)',
            marginBottom: '14px'
          }}>
            <div style={{
              fontSize: '12px',
              fontWeight: 600,
              color: 'var(--text-muted)',
              display: 'flex',
              alignItems: 'center',
              gap: '8px'
            }}>
              <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                <rect x="3" y="3" width="18" height="18" rx="2" ry="2"></rect>
                <circle cx="8.5" cy="8.5" r="1.5"></circle>
                <polyline points="21 15 16 10 5 21"></polyline>
              </svg>
              <span>Benchmark Analysis: Urban Inundation Scene (256×256)</span>
            </div>
            <span style={{ fontSize: '11px', fontSemiBold: 600, color: 'var(--primary)', textTransform: 'uppercase', fontWeight: 600 }}>
              Original vs Predicted Output
            </span>
          </div>

          <div style={{
            display: 'grid',
            gridTemplateColumns: 'repeat(auto-fit, minmax(280px, 1fr))',
            gap: '16px'
          }}>
            <div style={{ background: 'var(--bg-secondary)', borderRadius: '8px', overflow: 'hidden', border: '1px solid var(--border-subtle)' }}>
              <div style={{ padding: '8px 12px', fontSize: '11px', fontWeight: 600, color: 'var(--text-muted)', textTransform: 'uppercase', letterSpacing: '0.04em', background: '#FFFFFF', borderBottom: '1px solid var(--border-subtle)', textAlign: 'left' }}>
                Original Flood Photograph
              </div>
              <img
                src="/samples/sample1.jpg"
                alt="Original Flood Image"
                style={{ width: '100%', aspectRatio: '1', objectFit: 'cover', display: 'block' }}
                onError={(e) => { e.target.src = '/static/samples/sample1.jpg'; }}
              />
            </div>
            <div style={{ background: 'var(--bg-secondary)', borderRadius: '8px', overflow: 'hidden', border: '1px solid var(--border-subtle)' }}>
              <div style={{ padding: '8px 12px', fontSize: '11px', fontWeight: 600, color: 'var(--text-muted)', textTransform: 'uppercase', letterSpacing: '0.04em', background: '#FFFFFF', borderBottom: '1px solid var(--border-subtle)', textAlign: 'left' }}>
                Segmented Waterline Overlay (Model Output)
              </div>
              <img
                src={heroImage || "/samples/sample2.jpg"}
                alt="Segmented Map"
                style={{ width: '100%', aspectRatio: '1', objectFit: 'cover', display: 'block' }}
                onError={(e) => { e.target.src = '/static/samples/sample2.jpg'; }}
              />
            </div>
          </div>
        </div>
      </div>
    </section>
  );
}
