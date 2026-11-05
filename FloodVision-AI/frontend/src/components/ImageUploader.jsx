import React, { useRef } from 'react';

export default function ImageUploader({
  selectedFile,
  setSelectedFile,
  selectedSample,
  setSelectedSample,
  modelChoice,
  setModelChoice,
  threshold,
  setThreshold,
  onAnalyze,
  loading
}) {
  const fileInputRef = useRef(null);

  const samples = [
    { id: 'sample1', label: 'Urban', title: 'Urban Road Inundation', src: '/samples/sample1.jpg', fallback: '/static/samples/sample1.jpg' },
    { id: 'sample2', label: 'Street', title: 'Street Submergence', src: '/samples/sample2.jpg', fallback: '/static/samples/sample2.jpg' },
    { id: 'sample3', label: 'Aerial', title: 'Aerial Inundation', src: '/samples/sample3.jpg', fallback: '/static/samples/sample3.jpg' },
    { id: 'sample4', label: 'Rural', title: 'Rural Water Basin', src: '/samples/sample4.jpg', fallback: '/static/samples/sample4.jpg' },
  ];

  const handleFileChange = (e) => {
    if (e.target.files && e.target.files[0]) {
      setSelectedFile(e.target.files[0]);
      setSelectedSample(null);
    }
  };

  const handleDrop = (e) => {
    e.preventDefault();
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      setSelectedFile(e.dataTransfer.files[0]);
      setSelectedSample(null);
    }
  };

  const applyPreset = (modelKey, tauValue) => {
    setModelChoice(modelKey);
    setThreshold(tauValue);
  };

  return (
    <div>
      {/* Upload Dropzone */}
      <div
        onClick={() => fileInputRef.current.click()}
        onDragOver={(e) => e.preventDefault()}
        onDrop={handleDrop}
        style={{
          border: `2px dashed ${selectedFile ? 'var(--primary)' : 'var(--border-strong)'}`,
          background: selectedFile ? '#F0F6F1' : 'var(--bg-secondary)',
          borderRadius: '10px',
          padding: '24px 16px',
          textAlign: 'center',
          cursor: 'pointer',
          transition: 'all 0.2s ease'
        }}
      >
        <input
          ref={fileInputRef}
          type="file"
          accept="image/jpeg,image/png,image/jpg,image/webp"
          style={{ display: 'none' }}
          onChange={handleFileChange}
        />
        <svg width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" style={{ color: 'var(--primary)', marginBottom: '8px' }}>
          <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"></path>
          <polyline points="17 8 12 3 7 8"></polyline>
          <line x1="12" y1="3" x2="12" y2="15"></line>
        </svg>
        <div style={{ fontSize: '13px', fontWeight: 600, color: 'var(--text-main)', marginBottom: '2px' }}>
          {selectedFile ? (
            <span>Selected: <b>{selectedFile.name}</b> ({(selectedFile.size / 1024).toFixed(1)} KB)</span>
          ) : (
            <span><b>Drop flood photograph</b> or <span style={{ color: 'var(--primary)', textDecoration: 'underline' }}>Browse Files</span></span>
          )}
        </div>
        <div style={{ fontSize: '11px', color: 'var(--text-dim)' }}>
          JPG, JPEG, PNG, WEBP &bull; Auto-resized to 256×256
        </div>
      </div>

      {/* Benchmark Gallery */}
      <div style={{ marginTop: '16px' }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '11px', fontWeight: 700, textTransform: 'uppercase', letterSpacing: '0.04em', color: 'var(--text-dim)', marginBottom: '8px' }}>
          <span>Sample Benchmark Scenes:</span>
          <span style={{ color: 'var(--primary)' }}>1-Click Demo</span>
        </div>
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(4, 1fr)', gap: '8px' }}>
          {samples.map((s) => (
            <div
              key={s.id}
              onClick={() => { setSelectedSample(s.id); setSelectedFile(null); }}
              title={s.title}
              style={{
                position: 'relative',
                aspectRatio: '1',
                borderRadius: '6px',
                overflow: 'hidden',
                border: selectedSample === s.id && !selectedFile ? '2px solid var(--primary)' : '2px solid transparent',
                cursor: 'pointer',
                background: '#E5EAE5',
                transition: 'all 0.15s ease'
              }}
            >
              <img
                src={s.src}
                alt={s.label}
                style={{ width: '100%', height: '100%', objectFit: 'cover', display: 'block' }}
                onError={(e) => { e.target.src = s.fallback; }}
              />
              <span style={{
                position: 'absolute',
                bottom: 0,
                left: 0,
                right: 0,
                background: 'rgba(32, 41, 35, 0.85)',
                fontSize: '9px',
                fontWeight: 700,
                color: '#FFFFFF',
                textAlign: 'center',
                padding: '2px',
                textTransform: 'uppercase',
                letterSpacing: '0.03em'
              }}>
                {s.label}
              </span>
            </div>
          ))}
        </div>
      </div>

      {/* Workflow Controls */}
      <div style={{ marginTop: '18px', display: 'flex', flexDirection: 'column', gap: '14px' }}>
        <button
          onClick={onAnalyze}
          disabled={loading}
          style={{
            width: '100%',
            padding: '13px',
            background: 'var(--primary)',
            border: 'none',
            borderRadius: '8px',
            color: '#FFFFFF',
            fontFamily: 'var(--font-sans)',
            fontSize: '14px',
            fontWeight: 600,
            cursor: loading ? 'not-allowed' : 'pointer',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            gap: '8px',
            opacity: loading ? 0.65 : 1,
            transition: 'background-color 0.2s ease',
            boxShadow: 'var(--shadow-sm)'
          }}
        >
          {loading ? (
            <>
              <span style={{
                width: '14px',
                height: '14px',
                border: '2px solid rgba(255, 255, 255, 0.4)',
                borderTopColor: '#FFFFFF',
                borderRadius: '50%',
                display: 'inline-block',
                animation: 'spin 0.7s linear infinite'
              }} />
              <span>Analyzing Pixels...</span>
            </>
          ) : (
            <>
              <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                <polygon points="5 3 19 12 5 21 5 3"></polygon>
              </svg>
              <span>Analyze Image</span>
            </>
          )}
        </button>

        {/* Advanced Settings (Always Visible) */}
        <div style={{ borderTop: '1px solid var(--border-subtle)', paddingTop: '14px', marginTop: '4px' }}>
          <div style={{ fontSize: '12px', fontWeight: 700, textTransform: 'uppercase', letterSpacing: '0.04em', color: 'var(--text-dim)', marginBottom: '10px' }}>
            Advanced Settings
          </div>
          
          <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
            <div>
              <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '12px', fontWeight: 600, color: 'var(--text-main)', marginBottom: '4px' }}>
                <span>Inference Model</span>
              </div>
              <select
                value={modelChoice}
                onChange={(e) => setModelChoice(e.target.value)}
                style={{
                  width: '100%',
                  background: 'var(--bg-card)',
                  border: '1px solid var(--border-strong)',
                  borderRadius: '6px',
                  padding: '8px 10px',
                  fontFamily: 'var(--font-sans)',
                  fontSize: '12px',
                  color: 'var(--text-main)',
                  outline: 'none',
                  cursor: 'pointer'
                }}
              >
                <option value="rf_student">FloodVision Fast Model (Default, 40ms)</option>
                <option value="rf_teacher">High-Precision Extended Ensemble</option>
                <option value="km_student">Unsupervised Cluster Segmenter</option>
              </select>
            </div>

            <div>
              <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '12px', fontWeight: 600, color: 'var(--text-main)', marginBottom: '4px' }}>
                <span>Threshold Sensitivity (&tau;)</span>
                <span style={{ fontFamily: 'var(--font-mono)', fontSize: '11px', color: 'var(--primary)', fontWeight: 700 }}>
                  {threshold.toFixed(2)}
                </span>
              </div>
              <input
                type="range"
                min="0.20"
                max="0.80"
                step="0.05"
                value={threshold}
                onChange={(e) => setThreshold(parseFloat(e.target.value))}
                style={{ width: '100%', accentColor: 'var(--primary)', cursor: 'pointer' }}
              />
            </div>
          </div>

          {/* Helpful Usage Guide: Which settings should I use? */}
          <div style={{
            marginTop: '14px',
            background: 'var(--bg-secondary)',
            border: '1px solid var(--border-subtle)',
            borderRadius: '8px',
            padding: '12px 14px'
          }}>
            <div style={{ fontSize: '12px', fontWeight: 700, color: 'var(--text-main)', marginBottom: '6px', display: 'flex', alignItems: 'center', gap: '6px' }}>
              <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" style={{ color: 'var(--primary)' }}>
                <circle cx="12" cy="12" r="10"></circle>
                <line x1="12" y1="16" x2="12" y2="12"></line>
                <line x1="12" y1="8" x2="12.01" y2="8"></line>
              </svg>
              <span>Which settings should I use?</span>
            </div>

            {/* Model Guidance */}
            <div style={{ fontSize: '11px', color: 'var(--text-muted)', lineHeight: 1.45, marginBottom: '8px' }}>
              <div>&bull; <b>Fast Model (Default):</b> Best for rapid sub-40ms edge screening.</div>
              <div>&bull; <b>High-Precision Ensemble:</b> Best for maximum boundary quality (18 features).</div>
              <div>&bull; <b>Cluster Segmenter:</b> For exploratory clustering without ground-truth masks.</div>
            </div>

            {/* Threshold Guidance */}
            <div style={{ fontSize: '11px', color: 'var(--text-muted)', lineHeight: 1.45, paddingTop: '6px', borderTop: '1px solid var(--border-subtle)', marginBottom: '8px' }}>
              <div style={{ fontWeight: 600, color: 'var(--text-main)', marginBottom: '2px' }}>Threshold (&tau;) Sensitivity:</div>
              <div>&bull; <b>Lower (0.35–0.45):</b> Muddy/shadowed water or inclusive detection.</div>
              <div>&bull; <b>Default (0.50):</b> Balanced for clear daylight scenes.</div>
              <div>&bull; <b>Higher (0.55–0.65):</b> Suppresses bright glare, wet asphalt, or conservative calls.</div>
            </div>

            {/* Recommended Presets */}
            <div style={{ paddingTop: '6px', borderTop: '1px solid var(--border-subtle)' }}>
              <div style={{ fontSize: '10px', fontWeight: 700, textTransform: 'uppercase', letterSpacing: '0.04em', color: 'var(--text-dim)', marginBottom: '5px' }}>
                Recommended Starting Presets (Click to Apply):
              </div>
              <div style={{ display: 'flex', flexDirection: 'column', gap: '4px', fontSize: '11px' }}>
                <div
                  onClick={() => applyPreset('rf_student', 0.50)}
                  style={{
                    display: 'flex',
                    justifyContent: 'space-between',
                    alignItems: 'center',
                    background: '#FFFFFF',
                    padding: '4px 8px',
                    borderRadius: '4px',
                    border: '1px solid var(--border-subtle)',
                    cursor: 'pointer'
                  }}
                  title="Apply Clear Daylight settings"
                >
                  <span>☀️ <b>Clear Daylight:</b> Fast Model</span>
                  <span style={{ fontFamily: 'var(--font-mono)', fontWeight: 700, color: 'var(--primary)' }}>&tau;=0.50</span>
                </div>
                <div
                  onClick={() => applyPreset('rf_student', 0.40)}
                  style={{
                    display: 'flex',
                    justifyContent: 'space-between',
                    alignItems: 'center',
                    background: '#FFFFFF',
                    padding: '4px 8px',
                    borderRadius: '4px',
                    border: '1px solid var(--border-subtle)',
                    cursor: 'pointer'
                  }}
                  title="Apply Muddy / Shadowed settings"
                >
                  <span>🌧️ <b>Muddy / Shadowed:</b> Fast Model</span>
                  <span style={{ fontFamily: 'var(--font-mono)', fontWeight: 700, color: 'var(--primary)' }}>&tau;=0.40</span>
                </div>
                <div
                  onClick={() => applyPreset('rf_teacher', 0.60)}
                  style={{
                    display: 'flex',
                    justifyContent: 'space-between',
                    alignItems: 'center',
                    background: '#FFFFFF',
                    padding: '4px 8px',
                    borderRadius: '4px',
                    border: '1px solid var(--border-subtle)',
                    cursor: 'pointer'
                  }}
                  title="Apply Glare / Reflections settings"
                >
                  <span>✨ <b>Glare / Reflections:</b> High-Precision</span>
                  <span style={{ fontFamily: 'var(--font-mono)', fontWeight: 700, color: 'var(--primary)' }}>&tau;=0.60</span>
                </div>
              </div>
            </div>

            {/* Short Note */}
            <div style={{ fontSize: '10px', color: 'var(--text-dim)', fontStyle: 'italic', lineHeight: 1.35, margin_top: '8px', marginTop: '8px' }}>
              Recommended settings are starting points, not fixed rules. Experiment with the available options to find what works best for your image.
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
