import React from 'react';

export default function Insights({ history = [] }) {
  return (
    <section id="insights" style={{
      padding: '48px 0',
      borderTop: '1px solid var(--border-subtle)',
      background: '#FFFFFF'
    }}>
      <div className="container">
        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '16px' }}>
          <div>
            <div style={{ fontSize: '11px', fontWeight: 700, color: 'var(--primary)', textTransform: 'uppercase', letterSpacing: '0.06em', marginBottom: '4px' }}>
              Session Analytics
            </div>
            <h3 style={{ fontSize: '22px', fontWeight: 700, color: 'var(--text-main)', marginBottom: '4px' }}>
              Analysis History & Comparison
            </h3>
            <p style={{ fontSize: '13px', color: 'var(--text-muted)' }}>
              Review images evaluated during this session.
            </p>
          </div>
        </div>

        <div style={{ overflowX: 'auto' }}>
          <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: '13px', marginTop: '16px' }}>
            <thead>
              <tr>
                <th style={{ textAlign: 'left', padding: '10px 14px', background: 'var(--bg-secondary)', borderBottom: '1px solid var(--border-strong)', fontSize: '11px', fontWeight: 700, textTransform: 'uppercase', letterSpacing: '0.04em', color: 'var(--text-dim)' }}>Scene</th>
                <th style={{ textAlign: 'left', padding: '10px 14px', background: 'var(--bg-secondary)', borderBottom: '1px solid var(--border-strong)', fontSize: '11px', fontWeight: 700, textTransform: 'uppercase', letterSpacing: '0.04em', color: 'var(--text-dim)' }}>Resolution</th>
                <th style={{ textAlign: 'left', padding: '10px 14px', background: 'var(--bg-secondary)', borderBottom: '1px solid var(--border-strong)', fontSize: '11px', fontWeight: 700, textTransform: 'uppercase', letterSpacing: '0.04em', color: 'var(--text-dim)' }}>Flood Coverage (%)</th>
                <th style={{ textAlign: 'left', padding: '10px 14px', background: 'var(--bg-secondary)', borderBottom: '1px solid var(--border-strong)', fontSize: '11px', fontWeight: 700, textTransform: 'uppercase', letterSpacing: '0.04em', color: 'var(--text-dim)' }}>Non-Flood Coverage (%)</th>
                <th style={{ textAlign: 'left', padding: '10px 14px', background: 'var(--bg-secondary)', borderBottom: '1px solid var(--border-strong)', fontSize: '11px', fontWeight: 700, textTransform: 'uppercase', letterSpacing: '0.04em', color: 'var(--text-dim)' }}>Processing Time</th>
                <th style={{ textAlign: 'left', padding: '10px 14px', background: 'var(--bg-secondary)', borderBottom: '1px solid var(--border-strong)', fontSize: '11px', fontWeight: 700, textTransform: 'uppercase', letterSpacing: '0.04em', color: 'var(--text-dim)' }}>Model</th>
              </tr>
            </thead>
            <tbody>
              {history.length === 0 ? (
                <tr>
                  <td colSpan="6" style={{ textAlign: 'center', padding: '24px', color: 'var(--text-dim)', fontStyle: 'italic', borderBottom: '1px solid var(--border-subtle)' }}>
                    No analyses performed yet in this session. Select a sample or upload an image to begin.
                  </td>
                </tr>
              ) : (
                history.map((item, idx) => (
                  <tr key={idx} style={{ borderBottom: '1px solid var(--border-subtle)' }}>
                    <td style={{ padding: '12px 14px', fontWeight: 600 }}>{item.scene}</td>
                    <td style={{ padding: '12px 14px', fontFamily: 'var(--font-mono)', fontSize: '12px' }}>{item.resolution}</td>
                    <td style={{ padding: '12px 14px', fontFamily: 'var(--font-mono)', fontWeight: 700, color: 'var(--primary)' }}>
                      {item.flood_pct}%
                    </td>
                    <td style={{ padding: '12px 14px', fontFamily: 'var(--font-mono)' }}>
                      {item.dry_pct}%
                    </td>
                    <td style={{ padding: '12px 14px', fontFamily: 'var(--font-mono)', fontSize: '12px' }}>
                      {item.latency} ms
                    </td>
                    <td style={{ padding: '12px 14px', fontSize: '12px', color: 'var(--text-muted)' }}>
                      {item.model}
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      </div>
    </section>
  );
}

