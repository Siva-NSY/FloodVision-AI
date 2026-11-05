import React from 'react';

export default function About() {
  return (
    <section id="about" style={{
      padding: '56px 0 44px 0',
      background: 'var(--bg-secondary)',
      borderTop: '1px solid var(--border-subtle)'
    }}>
      <div className="container" style={{ maxWidth: '820px', textAlign: 'center' }}>
        <div style={{ fontSize: '11px', fontWeight: 700, color: 'var(--primary)', textTransform: 'uppercase', letterSpacing: '0.06em', marginBottom: '8px' }}>
          About FloodVision AI
        </div>
        <h3 style={{ fontSize: '22px', fontWeight: 700, color: 'var(--text-main)', marginBottom: '12px' }}>
          Lightweight Environmental Image Intelligence
        </h3>
        <p style={{ fontSize: '14px', color: 'var(--text-muted)', lineHeight: 1.65 }}>
          FloodVision AI develops lightweight classical machine learning models to identify flood-affected regions in aerial and terrestrial imagery. By combining multi-spectral color transformations with spatial feature engineering, it delivers efficient image segmentation without relying on computationally intensive neural networks.
        </p>
      </div>
    </section>
  );
}
