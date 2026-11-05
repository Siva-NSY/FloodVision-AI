import React from 'react';

export default function Creator() {
  return (
    <section id="creator" style={{
      padding: '56px 0 64px 0',
      background: '#FFFFFF',
      borderTop: '1px solid var(--border-subtle)'
    }}>
      <div className="container" style={{ maxWidth: '740px' }}>
        <div style={{ textAlign: 'center', marginBottom: '28px' }}>
          <div style={{ fontSize: '11px', fontWeight: 700, color: 'var(--primary)', textTransform: 'uppercase', letterSpacing: '0.06em', marginBottom: '8px' }}>
            About the Creator
          </div>
          <h3 style={{ fontSize: '24px', fontWeight: 700, color: 'var(--text-main)', marginBottom: '6px' }}>
            Siva Yaswanth
          </h3>
          <div style={{ fontSize: '13px', fontWeight: 600, color: 'var(--primary)', letterSpacing: '0.02em' }}>
            Computer Science Undergraduate &bull; IIT Patna
          </div>
        </div>

        <div style={{
          background: 'var(--bg-secondary)',
          border: '1px solid var(--border-subtle)',
          borderRadius: '12px',
          padding: '28px 32px',
          textAlign: 'center',
          boxShadow: 'var(--shadow-sm)'
        }}>
          <p style={{
            fontSize: '15px',
            color: 'var(--text-main)',
            lineHeight: 1.7,
            marginBottom: '22px',
            maxWidth: '620px',
            marginLeft: 'auto',
            marginRight: 'auto'
          }}>
            &ldquo;I'm Siva Yaswanth, a Computer Science undergraduate at IIT Patna with an interest in solving real world problems &rdquo;
          </p>

          <div style={{ display: 'flex', alignItems: 'center', justifySelf: 'center', justifyContent: 'center', gap: '14px', flexWrap: 'wrap' }}>
            <a
              href="https://github.com/Siva-NSY"
              target="_blank"
              rel="noopener noreferrer"
              style={{
                display: 'inline-flex',
                alignItems: 'center',
                gap: '8px',
                padding: '8px 18px',
                background: '#FFFFFF',
                border: '1px solid var(--border-strong)',
                borderRadius: '6px',
                fontSize: '13px',
                fontWeight: 600,
                color: 'var(--text-main)',
                textDecoration: 'none',
                transition: 'all 0.15s ease'
              }}
            >
              <svg width="16" height="16" viewBox="0 0 24 24" fill="currentColor">
                <path d="M12 0C5.37 0 0 5.37 0 12c0 5.31 3.435 9.795 8.205 11.385.6.105.825-.255.825-.57 0-.285-.015-1.23-.015-2.235-3.015.555-3.795-.735-4.035-1.41-.135-.345-.72-1.41-1.23-1.695-.42-.225-1.02-.78-.015-.795.945-.015 1.62.87 1.845 1.23 1.08 1.815 2.805 1.305 3.495.99.105-.78.42-1.305.765-1.605-2.67-.3-5.46-1.335-5.46-5.925 0-1.305.465-2.385 1.23-3.225-.12-.3-.54-1.53.12-3.18 0 0 1.005-.315 3.3 1.23.96-.27 1.98-.405 3-.405s2.04.135 3 .405c2.295-1.56 3.3-1.23 3.3-1.23.66 1.65.24 2.88.12 3.18.765.84 1.23 1.905 1.23 3.225 0 4.605-2.805 5.625-5.475 5.925.435.375.81 1.095.81 2.22 0 1.605-.015 2.895-.015 3.3 0 .315.225.69.825.57A12.02 12.02 0 0024 12c0-6.63-5.37-12-12-12z"/>
              </svg>
              <span>GitHub</span>
            </a>

            <a
              href="https://www.linkedin.com/in/siva-yaswanth-nallangari-155902324/"
              target="_blank"
              rel="noopener noreferrer"
              style={{
                display: 'inline-flex',
                alignItems: 'center',
                gap: '8px',
                padding: '8px 18px',
                background: '#FFFFFF',
                border: '1px solid var(--border-strong)',
                borderRadius: '6px',
                fontSize: '13px',
                fontWeight: 600,
                color: 'var(--text-main)',
                textDecoration: 'none',
                transition: 'all 0.15s ease'
              }}
            >
              <svg width="16" height="16" viewBox="0 0 24 24" fill="currentColor">
                <path d="M19 0h-14c-2.761 0-5 2.239-5 5v14c0 2.761 2.239 5 5 5h14c2.762 0 5-2.239 5-5v-14c0-2.761-2.238-5-5-5zm-11 19h-3v-11h3v11zm-1.5-12.268c-.966 0-1.75-.79-1.75-1.764s.784-1.764 1.75-1.764 1.75.79 1.75 1.764-.783 1.764-1.75 1.764zm13.5 12.268h-3v-5.604c0-3.368-4-3.113-4 0v5.604h-3v-11h3v1.765c1.396-2.586 7-2.777 7 2.476v6.759z"/>
              </svg>
              <span>LinkedIn</span>
            </a>
          </div>
        </div>
      </div>
    </section>
  );
}

