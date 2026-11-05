import React, { useState, useEffect } from 'react';
import Header from './components/Header.jsx';
import Hero from './components/Hero.jsx';
import HowItWorks from './components/HowItWorks.jsx';
import ImageUploader from './components/ImageUploader.jsx';
import AnalysisSummary from './components/AnalysisSummary.jsx';
import Insights from './components/Insights.jsx';
import About from './components/About.jsx';
import Creator from './components/Creator.jsx';
import Footer from './components/Footer.jsx';

export default function App() {
  const [selectedFile, setSelectedFile] = useState(null);
  const [selectedSample, setSelectedSample] = useState('sample1');
  const [modelChoice, setModelChoice] = useState('rf_student');
  const [threshold, setThreshold] = useState(0.50);
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);
  const [history, setHistory] = useState([]);

  const handleAnalyze = async () => {
    setLoading(true);
    const formData = new FormData();
    formData.append('model_choice', modelChoice);
    formData.append('threshold', threshold.toString());

    let sceneName = 'Benchmark Scene';
    if (selectedFile) {
      formData.append('image', selectedFile);
      sceneName = selectedFile.name;
    } else if (selectedSample) {
      formData.append('sample_id', selectedSample);
      sceneName = selectedSample.toUpperCase();
    } else {
      alert('Please select an image or benchmark scene.');
      setLoading(false);
      return;
    }

    try {
      const response = await fetch('/api/segment', {
        method: 'POST',
        body: formData
      });

      const data = await response.json();
      if (!response.ok || (data.success === false)) {
        alert(data.error || data.detail || 'Inference failed.');
      } else {
        setResult(data);
        if (data.analytics) {
          setHistory((prev) => [
            {
              scene: sceneName,
              resolution: data.analytics.processing_resolution || '256×256',
              flood_pct: data.analytics.flood_percentage,
              dry_pct: data.analytics.non_flood_percentage,
              latency: data.analytics.processing_time_ms,
              model: data.analytics.model_display_name || 'FloodVision Fast Model'
            },
            ...prev
          ]);
        }
      }
    } catch (err) {
      console.error(err);
      alert('Failed to connect to the backend API.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    handleAnalyze();
  }, []);

  return (
    <div>
      <Header />

      {/* Hero Showcase */}
      <Hero heroImage={result?.images?.overlay} />

      {/* How It Works & Capabilities */}
      <HowItWorks />

      {/* Live Workspace */}
      <section id="workspace" style={{ padding: '56px 0 64px 0' }}>
        <div className="container">
          <div style={{
            display: 'grid',
            gridTemplateColumns: 'minmax(320px, 380px) 1fr',
            gap: '28px',
            alignItems: 'start'
          }}>
            {/* Left Column: Image Ingestion */}
            <div style={{
              background: 'var(--bg-card)',
              border: '1px solid var(--border-subtle)',
              borderRadius: '12px',
              padding: '24px',
              boxShadow: 'var(--shadow-sm)'
            }}>
              <div style={{
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'space-between',
                paddingBottom: '14px',
                borderBottom: '1px solid var(--border-subtle)',
                marginBottom: '18px'
              }}>
                <h3 style={{ fontSize: '14px', fontWeight: 700, textTransform: 'uppercase', letterSpacing: '0.03em', color: 'var(--text-main)', margin: 0 }}>
                  Image Ingestion
                </h3>
                <span style={{ fontSize: '11px', fontFamily: 'var(--font-mono)', color: 'var(--primary)', fontWeight: 600 }}>
                  WORKSPACE
                </span>
              </div>

              <ImageUploader
                selectedFile={selectedFile}
                setSelectedFile={setSelectedFile}
                selectedSample={selectedSample}
                setSelectedSample={setSelectedSample}
                modelChoice={modelChoice}
                setModelChoice={setModelChoice}
                threshold={threshold}
                setThreshold={setThreshold}
                onAnalyze={handleAnalyze}
                loading={loading}
              />
            </div>

            {/* Right Column: Detailed Image Analysis Summary */}
            <div style={{
              background: 'var(--bg-card)',
              border: '1px solid var(--border-subtle)',
              borderRadius: '12px',
              padding: '24px',
              boxShadow: 'var(--shadow-sm)',
              minHeight: '560px'
            }}>
              <div style={{
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'space-between',
                paddingBottom: '14px',
                borderBottom: '1px solid var(--border-subtle)',
                marginBottom: '18px'
              }}>
                <h3 style={{ fontSize: '14px', fontWeight: 700, textTransform: 'uppercase', letterSpacing: '0.03em', color: 'var(--text-main)', margin: 0 }}>
                  Image Analysis Summary
                </h3>
                <span style={{ fontSize: '11px', fontFamily: 'var(--font-mono)', fontWeight: 600, color: 'var(--primary)' }}>
                  {loading ? 'PROCESSING' : result ? 'READY' : 'STANDBY'}
                </span>
              </div>

              <AnalysisSummary result={result} loading={loading} />
            </div>
          </div>
        </div>
      </section>

      {/* Insights History Table */}
      <Insights history={history} />

      {/* About Section */}
      <About />

      {/* About the Creator Section */}
      <Creator />

      {/* Professional Footer */}
      <Footer />
    </div>
  );
}
