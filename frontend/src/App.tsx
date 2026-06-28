import React, { useState } from 'react';
import ReactMarkdown from 'react-markdown';
import './App.css';

interface Source {
  source: string;
  category: string;
  excerpt: string;
}

interface ClinicalResponse {
  synthesis: string;
  retrieved_sources: Source[];
  disclaimer: string;
}

function App() {
  const [symptoms, setSymptoms] = useState('');
  const [labValues, setLabValues] = useState('');
  const [age, setAge] = useState('');
  const [medicalHistory, setMedicalHistory] = useState('');
  const [medications, setMedications] = useState('');
  const [response, setResponse] = useState<ClinicalResponse | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const handleSubmit = async () => {
    if (!symptoms.trim()) {
      setError('Please enter patient symptoms');
      return;
    }
    setError('');
    setLoading(true);
    setResponse(null);

    try {
      const res = await fetch('http://localhost:8000/query', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          symptoms,
          lab_values: labValues,
          age: age ? parseInt(age) : 0,
          medical_history: medicalHistory,
          current_medications: medications,
        }),
      });
      const data = await res.json();
      setResponse(data);
    } catch (err) {
      setError('Failed to connect to DocBrief API. Make sure the backend is running.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="app">
      {/* Header */}
      <header className="header">
        <div className="header-content">
          <div className="logo">
            <span className="logo-icon">⚕</span>
            <span className="logo-text">DocBrief</span>
          </div>
          <span className="logo-tagline">AI-Assisted Clinical Evidence Synthesis</span>
        </div>
      </header>

      <main className="main">
        <div className="container">
          {/* Input Panel */}
          <div className="input-panel">
            <h2 className="panel-title">Patient Presentation</h2>

            <div className="form-group">
              <label>Symptoms & Chief Complaint *</label>
              <textarea
                value={symptoms}
                onChange={e => setSymptoms(e.target.value)}
                placeholder="e.g. 65-year-old male presenting with chest pain radiating to left arm, diaphoresis, shortness of breath for 2 hours"
                rows={4}
              />
            </div>

            <div className="form-row">
              <div className="form-group">
                <label>Lab Values & Vitals</label>
                <textarea
                  value={labValues}
                  onChange={e => setLabValues(e.target.value)}
                  placeholder="e.g. BP 160/95, HR 88, Troponin 0.8, HbA1c 8.2%, FBG 210 mg/dL"
                  rows={3}
                />
              </div>
              <div className="form-group">
                <label>Age</label>
                <input
                  type="number"
                  value={age}
                  onChange={e => setAge(e.target.value)}
                  placeholder="Patient age"
                />
              </div>
            </div>

            <div className="form-group">
              <label>Medical History</label>
              <textarea
                value={medicalHistory}
                onChange={e => setMedicalHistory(e.target.value)}
                placeholder="e.g. Type 2 diabetes, hypertension, previous MI in 2019"
                rows={2}
              />
            </div>

            <div className="form-group">
              <label>Current Medications</label>
              <textarea
                value={medications}
                onChange={e => setMedications(e.target.value)}
                placeholder="e.g. Metformin 1000mg BID, Lisinopril 10mg daily, Aspirin 81mg"
                rows={2}
              />
            </div>

            {error && <div className="error">{error}</div>}

            <button
              className="submit-btn"
              onClick={handleSubmit}
              disabled={loading}
            >
              {loading ? (
                <span>Synthesizing Evidence...</span>
              ) : (
                <span>⚕ Synthesize Clinical Evidence</span>
              )}
            </button>
          </div>

          {/* Loading */}
          {loading && (
            <div className="results-panel">
              <div className="loading">
                <div className="spinner"></div>
                <p>Retrieving relevant clinical guidelines and synthesizing evidence...</p>
              </div>
            </div>
          )}

          {/* Results */}
          {response && (
            <div className="results-panel">
              <div className="disclaimer">
                {response.disclaimer}
              </div>

              <div className="synthesis">
                <h2>Clinical Evidence Synthesis</h2>
                <div className="synthesis-content">
                  <ReactMarkdown>{response.synthesis}</ReactMarkdown>
                </div>
              </div>

              <div className="sources">
                <h3>Retrieved Guidelines ({response.retrieved_sources.length})</h3>
                <div className="sources-grid">
                  {response.retrieved_sources.map((source, i) => (
                    <div key={i} className="source-card">
                      <div className="source-category">{source.category}</div>
                      <div className="source-name">{source.source}</div>
                      <div className="source-excerpt">{source.excerpt}</div>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          )}
        </div>
      </main>
    </div>
  );
}

export default App;
