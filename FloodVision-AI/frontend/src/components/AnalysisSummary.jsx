import React, { useState } from 'react';

export default function AnalysisSummary({ result, loading }) {
  const [showTech, setShowTech] = useState(false);

  if (loading) {
    return (
      <div style={{ flex: 1, display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', minHeight: '380px', textAlign: 'center', color: 'var(--text-dim)' }}>
        <div style={{
          width: '32px',
          height: '32px',
          border: '3px solid var(--border-subtle)',
          borderTopColor: 'var(--primary)',
          borderRadius: '50%',
          animation: 'spin 0.7s linear infinite',
          marginBottom: '14px'
        }} />
        <div style={{ fontSize: '14px', fontWeight: 600, color: 'var(--text-main)', marginBottom: '4px' }}>
          Segmenting Image Features...
        </div>
        <div style={{ fontSize: '12px', maxWidth: '300px' }}>
          Extracting multi-spectral spatial priors and classifying pixel boundaries.
        </div>
      </div>
    );
  }

  if (!result || !result.analytics) {
    return (
      <div style={{ flex: 1, display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', minHeight: '380px', textAlign: 'center', color: 'var(--text-dim)' }}>
        <svg width="40" height="40" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round" style={{ marginBottom: '12px', color: 'var(--text-muted)' }}>
          <rect x="3" y="3" width="18" height="18" rx="2" ry="2"></rect>
          <circle cx="8.5" cy="8.5" r="1.5"></circle>
          <polyline points="21 15 16 10 5 21"></polyline>
        </svg>
        <div style={{ fontSize: '14px', fontWeight: 600, color: 'var(--text-main)', marginBottom: '4px' }}>
          Awaiting Image Ingestion
        </div>
        <div style={{ fontSize: '12px', maxWidth: '320px' }}>
          Upload a flood photograph or select a benchmark scene on the left, then click Analyze Image.
        </div>
      </div>
    );
  }

  const { analytics, images } = result;
  const spatial = analytics.spatial_distribution || {};
  const quads = spatial.quadrants || {};

  const handlePrint = () => {
    window.print();
  };

  const handleExportJson = () => {
    const blob = new Blob([JSON.stringify(analytics, null, 2)], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `floodvision_telemetry_${Date.now()}.json`;
    a.click();
    URL.revokeObjectURL(url);
  };

  return (
    <div>
      {/* A. Dynamic Factual Analysis Overview Statement */}
      <div style={{
        background: 'var(--bg-secondary)',
        border: '1px solid var(--border-subtle)',
        borderLeft: '4px solid var(--primary)',
        borderRadius: '8px',
        padding: '16px 18px',
        marginBottom: '22px'
      }}>
        <h4 style={{ fontSize: '14px', fontWeight: 700, color: 'var(--text-main)', marginBottom: '4px' }}>
          Analysis Overview
        </h4>
        <p style={{ fontSize: '13px', color: 'var(--text-muted)', lineHeight: 1.5 }}>
          {analytics.summary_statement || `The model identified flood-class regions covering ${analytics.flood_percentage}% (${analytics.flood_pixels?.toLocaleString()} pixels) of the uploaded image. The remaining ${analytics.non_flood_percentage}% were classified as non-flood.`}
        </p>
      </div>

      {/* B. Key Statistics Ribbon */}
      <div style={{
        display: 'grid',
        gridTemplateColumns: 'repeat(auto-fit, minmax(140px, 1fr))',
        gap: '12px',
        marginBottom: '24px'
      }}>
        <div style={{ background: 'var(--bg-secondary)', border: '1px solid var(--border-subtle)', borderRadius: '8px', padding: '12px 14px' }}>
          <div style={{ fontSize: '10px', fontWeight: 700, textTransform: 'uppercase', letterSpacing: '0.04em', color: 'var(--text-dim)', marginBottom: '4px' }}>
            Flood Coverage
          </div>
          <div style={{ fontFamily: 'var(--font-mono)', fontSize: '18px', fontWeight: 700, color: 'var(--primary)' }}>
            {analytics.flood_percentage}%
          </div>
          <div style={{ fontSize: '11px', color: 'var(--text-muted)', marginTop: '2px' }}>
            {analytics.flood_pixels?.toLocaleString()} pixels
          </div>
        </div>

        <div style={{ background: 'var(--bg-secondary)', border: '1px solid var(--border-subtle)', borderRadius: '8px', padding: '12px 14px' }}>
          <div style={{ fontSize: '10px', fontWeight: 700, textTransform: 'uppercase', letterSpacing: '0.04em', color: 'var(--text-dim)', marginBottom: '4px' }}>
            Non-Flood Coverage
          </div>
          <div style={{ fontFamily: 'var(--font-mono)', fontSize: '18px', fontWeight: 700, color: 'var(--text-main)' }}>
            {analytics.non_flood_percentage}%
          </div>
          <div style={{ fontSize: '11px', color: 'var(--text-muted)', marginTop: '2px' }}>
            {analytics.non_flood_pixels?.toLocaleString()} pixels
          </div>
        </div>

        <div style={{ background: 'var(--bg-secondary)', border: '1px solid var(--border-subtle)', borderRadius: '8px', padding: '12px 14px' }}>
          <div style={{ fontSize: '10px', fontWeight: 700, textTransform: 'uppercase', letterSpacing: '0.04em', color: 'var(--text-dim)', marginBottom: '4px' }}>
            Total Evaluated
          </div>
          <div style={{ fontFamily: 'var(--font-mono)', fontSize: '18px', fontWeight: 700, color: 'var(--text-main)' }}>
            65,536
          </div>
          <div style={{ fontSize: '11px', color: 'var(--text-muted)', marginTop: '2px' }}>
            256×256 pixels
          </div>
        </div>

        <div style={{ background: 'var(--bg-secondary)', border: '1px solid var(--border-subtle)', borderRadius: '8px', padding: '12px 14px' }}>
          <div style={{ fontSize: '10px', fontWeight: 700, textTransform: 'uppercase', letterSpacing: '0.04em', color: 'var(--text-dim)', marginBottom: '4px' }}>
            Processing Time
          </div>
          <div style={{ fontFamily: 'var(--font-mono)', fontSize: '18px', fontWeight: 700, color: 'var(--text-main)' }}>
            {analytics.processing_time_ms} ms
          </div>
          <div style={{ fontSize: '11px', color: 'var(--text-muted)', marginTop: '2px' }}>
            {analytics.fps} FPS throughput
          </div>
        </div>
      </div>

      {/* C. Visualization Display Grid */}
      <div style={{
        display: 'grid',
        gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))',
        gap: '16px',
        marginBottom: '28px'
      }}>
        <div style={{ background: '#FFFFFF', border: '1px solid var(--border-subtle)', borderRadius: '8px', overflow: 'hidden', display: 'flex', flexDirection: 'column' }}>
          <div style={{ padding: '8px 12px', fontSize: '11px', fontWeight: 600, color: 'var(--text-muted)', textTransform: 'uppercase', letterSpacing: '0.03em', background: 'var(--bg-secondary)', borderBottom: '1px solid var(--border-subtle)', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
            <span>1. Original Image</span>
            <a href={images.original} download="original_input.jpg" style={{ fontSize: '10px', fontWeight: 600, color: 'var(--text-main)', background: '#FFFFFF', border: '1px solid var(--border-strong)', padding: '2px 7px', borderRadius: '4px', textDecoration: 'none' }}>Download</a>
          </div>
          <div style={{ aspectRatio: '1', background: '#111827', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
            <img src={images.original} alt="Original Photograph" style={{ width: '100%', height: '100%', objectFit: 'contain', display: 'block' }} />
          </div>
        </div>

        <div style={{ background: '#FFFFFF', border: '1px solid var(--border-subtle)', borderRadius: '8px', overflow: 'hidden', display: 'flex', flexDirection: 'column' }}>
          <div style={{ padding: '8px 12px', fontSize: '11px', fontWeight: 600, color: 'var(--text-muted)', textTransform: 'uppercase', letterSpacing: '0.03em', background: 'var(--bg-secondary)', borderBottom: '1px solid var(--border-subtle)', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
            <span>2. Binary Mask</span>
            <a href={images.mask} download="flood_binary_mask.png" style={{ fontSize: '10px', fontWeight: 600, color: 'var(--text-main)', background: '#FFFFFF', border: '1px solid var(--border-strong)', padding: '2px 7px', borderRadius: '4px', textDecoration: 'none' }}>PNG</a>
          </div>
          <div style={{ aspectRatio: '1', background: '#111827', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
            <img src={images.mask} alt="Binary Segmentation Mask" style={{ width: '100%', height: '100%', objectFit: 'contain', display: 'block' }} />
          </div>
        </div>

        <div style={{ background: '#FFFFFF', border: '1px solid var(--border-subtle)', borderRadius: '8px', overflow: 'hidden', display: 'flex', flexDirection: 'column' }}>
          <div style={{ padding: '8px 12px', fontSize: '11px', fontWeight: 600, color: 'var(--text-muted)', textTransform: 'uppercase', letterSpacing: '0.03em', background: 'var(--bg-secondary)', borderBottom: '1px solid var(--border-subtle)', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
            <span>3. Colored Overlay</span>
            <a href={images.overlay} download="flood_overlay_map.jpg" style={{ fontSize: '10px', fontWeight: 600, color: 'var(--text-main)', background: '#FFFFFF', border: '1px solid var(--border-strong)', padding: '2px 7px', borderRadius: '4px', textDecoration: 'none' }}>JPG</a>
          </div>
          <div style={{ aspectRatio: '1', background: '#111827', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
            <img src={images.overlay} alt="Colored Overlay Map" style={{ width: '100%', height: '100%', objectFit: 'contain', display: 'block' }} />
          </div>
        </div>
      </div>

      {/* Visual Color Legend */}
      <div style={{
        display: 'flex',
        flexWrap: 'wrap',
        alignItems: 'center',
        gap: '20px',
        padding: '12px 16px',
        background: 'var(--bg-secondary)',
        border: '1px solid var(--border-subtle)',
        borderRadius: '8px',
        marginBottom: '28px',
        fontSize: '12px'
      }}>
        <span style={{ fontWeight: 700, color: 'var(--text-dim)', textTransform: 'uppercase', fontSize: '11px' }}>Color Legend:</span>
        <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
          <div style={{ width: '14px', height: '14px', borderRadius: '3px', background: '#38bdf8', border: '1px solid #0284c7' }}></div>
          <span><b>Sky Blue:</b> Classified Flood Water</span>
        </div>
        <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
          <div style={{ width: '14px', height: '14px', borderRadius: '3px', background: '#ef4444', border: '1px solid #dc2626' }}></div>
          <span><b>Red Contour:</b> Detected Waterline Shore</span>
        </div>
        <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
          <div style={{ width: '14px', height: '14px', borderRadius: '3px', background: '#111827' }}></div>
          <span><b>Black (in Mask):</b> Non-Flood / Dry Terrain</span>
        </div>
        <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
          <div style={{ width: '14px', height: '14px', borderRadius: '3px', background: '#ffffff', border: '1px solid #d1d5db' }}></div>
          <span><b>White (in Mask):</b> Flood-Class Pixels</span>
        </div>
      </div>

      {/* Understanding This Result (Limitations & Meaning) */}
      <div style={{
        background: '#FFFFFF',
        border: '1px solid var(--border-subtle)',
        borderRadius: '8px',
        padding: '16px',
        marginBottom: '24px'
      }}>
        <h5 style={{ fontSize: '13px', fontWeight: 700, color: 'var(--text-main)', marginBottom: '4px' }}>
          Understanding This Result
        </h5>
        <p style={{ fontSize: '12px', color: 'var(--text-muted)', lineHeight: 1.5 }}>
          The flood coverage value represents the proportion of image pixels classified as flood by the model. It does not represent actual land area, water depth, or real-time emergency hazard status. Results depend on image quality, illumination, water turbidity, and specular surface reflections.
        </p>
      </div>

      {/* E. Collapsible Technical Analysis Details */}
      <div style={{ marginBottom: '24px' }}>
        <div
          onClick={() => setShowTech(!showTech)}
          style={{
            fontSize: '12px',
            fontWeight: 600,
            color: 'var(--text-muted)',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'space-between',
            cursor: 'pointer',
            padding: '10px 0 6px 0',
            borderTop: '1px solid var(--border-subtle)',
            userSelect: 'none'
          }}
        >
          <span>Technical Analysis Details</span>
          <span style={{ fontWeight: 700 }}>{showTech ? '−' : '+'}</span>
        </div>

        {showTech && (
          <div style={{ fontSize: '12px', color: 'var(--text-muted)', background: 'var(--bg-secondary)', padding: '14px', borderRadius: '6px', marginTop: '8px', display: 'flex', flexDirection: 'column', gap: '6px' }}>
            <div><b>Model:</b> {analytics.model_display_name || 'FloodVision Image Segmentation Model'}</div>
            <div><b>Feature Representation:</b> {analytics.technical_details?.feature_space_dimensions || 6} dimensions (RGB, Color Context, Edge Gradient, Vertical Row Prior)</div>
            <div><b>Model Size:</b> {analytics.technical_details?.model_footprint_kb || 444} KB</div>
            <div><b>Threshold Applied:</b> {analytics.technical_details?.threshold_applied || 0.50}</div>
            <div><b>Preprocessing:</b> Bilinear resizing to 256×256 matrix, StandardScaler normalization</div>
            <div><b>Spatial Filtering:</b> 3×3 median noise-suppression filter</div>
          </div>
        )}
      </div>

      {/* Export Bar */}
      <div style={{ display: 'flex', justifyContent: 'flex-end', gap: '10px' }}>
        <button
          onClick={handlePrint}
          style={{
            display: 'inline-flex',
            alignItems: 'center',
            gap: '8px',
            padding: '8px 16px',
            background: 'var(--bg-card)',
            color: 'var(--text-main)',
            fontSize: '13px',
            fontWeight: 600,
            borderRadius: '6px',
            border: '1px solid var(--border-subtle)',
            cursor: 'pointer'
          }}
        >
          <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
            <polyline points="6 9 6 2 18 2 18 9"></polyline>
            <path d="M6 18H4a2 2 0 0 1-2-2v-5a2 2 0 0 1 2-2h16a2 2 0 0 1 2 2v5a2 2 0 0 1-2 2h-2"></path>
            <rect x="6" y="14" width="12" height="8"></rect>
          </svg>
          <span>Print / Save PDF Report</span>
        </button>

        <button
          onClick={handleExportJson}
          style={{
            display: 'inline-flex',
            alignItems: 'center',
            gap: '8px',
            padding: '8px 16px',
            background: 'var(--primary)',
            color: '#FFFFFF',
            fontSize: '13px',
            fontWeight: 600,
            borderRadius: '6px',
            border: 'none',
            cursor: 'pointer'
          }}
        >
          <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
            <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"></path>
            <polyline points="7 10 12 15 17 10"></polyline>
            <line x1="12" y1="15" x2="12" y2="3"></line>
          </svg>
          <span>Export Analysis Data (JSON)</span>
        </button>
      </div>
    </div>
  );
}

