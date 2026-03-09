import React, { useState, useEffect } from 'react';
import { BrowserRouter as Router, Routes, Route, Link } from 'react-router-dom';
import AdminDashboard from './components/AdminDashboard';
import ScannerInput from './components/ScannerInput';
import ResultsView from './components/ResultsView';
import RecentScansDrawer from './components/RecentScansDrawer';
import ResultsSkeleton from './components/ResultsSkeleton';
import { analyzeIngredients } from './api';
import { History } from 'lucide-react';

function App() {
  const [results, setResults] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [history, setHistory] = useState([]);
  const [isDrawerOpen, setIsDrawerOpen] = useState(false);
  const [targetAudience, setTargetAudience] = useState('adult'); // Default to adult

  useEffect(() => {
    const saved = localStorage.getItem('scanHistory');
    if (saved) {
      setHistory(JSON.parse(saved));
    }
  }, []);

  const saveToHistory = (data) => {
    const newScan = { ...data, timestamp: new Date().toLocaleDateString(), audience: targetAudience };
    const newHistory = [newScan, ...history].slice(0, 5); // Keep last 5
    setHistory(newHistory);
    localStorage.setItem('scanHistory', JSON.stringify(newHistory));
  };

  const handleAnalyze = async (text, category = "shampoo") => {
    setLoading(true);
    setError(null);
    try {
      const data = await analyzeIngredients(text, category, targetAudience);
      // Inject context into results so components know what we analyzed
      const enrichedData = { ...data, category, target_audience: targetAudience };

      // Add a small delay for effect if response is too fast
      setTimeout(() => {
        setResults(enrichedData);
        saveToHistory(enrichedData);
        setLoading(false);
      }, 800);
    } catch (err) {
      setError("Failed to analyze. Please ensure the backend is running.");
      setLoading(false);
    }
  };

  const handleReset = () => {
    setResults(null);
    setError(null);
  };

  const handleChangeCategory = () => {
    setResults(null);
    setError(null);
  }

  return (
    <Router>
      <div className="min-h-screen bg-transparent text-white p-4 md:p-8 font-sans">
        <header className="max-w-7xl mx-auto mb-12 flex items-center justify-between">
          <Link to="/" className="flex items-center gap-2 hover:opacity-80 transition-opacity" onClick={handleChangeCategory}>
            <div className="w-8 h-8 rounded-lg bg-primary shadow-[0_0_10px_var(--color-primary)] flex items-center justify-center font-bold text-lg text-black">
              IS
            </div>
            <h1 className="text-xl font-bold tracking-tight text-white">Ingredient Safety</h1>
          </Link>
          <div className="flex gap-4">
            <Link to="/admin" className="p-2 hover:bg-white/10 rounded-lg transition-colors text-gray-300 hover:text-white" title="Admin Dashboard">
              <div className="flex items-center gap-1 font-medium text-sm">
                <span className="hidden md:inline">Admin</span>
              </div>
            </Link>
            <button
              onClick={() => setIsDrawerOpen(true)}
              className="p-2 hover:bg-white/10 rounded-lg transition-colors text-gray-300 hover:text-white"
              title="Recent Scans"
            >
              <History size={24} />
            </button>
          </div>
        </header>

        <main className="container mx-auto">
          <Routes>
            <Route path="/admin" element={<AdminDashboard />} />
            <Route path="/" element={
              <>
                {error && (
                  <div className="max-w-2xl mx-auto mb-8 bg-red-500/10 border border-red-500/20 p-4 rounded-xl text-red-200 text-center">
                    {error}
                  </div>
                )}

                {loading ? (
                  <ResultsSkeleton />
                ) : !results ? (
                  <div className="flex flex-col items-center">
                    <ScannerInput onAnalyze={handleAnalyze} isLoading={loading} />
                  </div>
                ) : (
                  <ResultsView data={results} onReset={handleReset} />
                )}
              </>
            } />
          </Routes>
        </main>

        <RecentScansDrawer
          isOpen={isDrawerOpen}
          onClose={() => setIsDrawerOpen(false)}
          scans={history}
          onLoadScan={(scan) => {
            setResults(scan);
            setIsDrawerOpen(false);
          }}
        />

        <footer className="fixed bottom-4 right-4 text-xs text-gray-600">
          v1.0.0 • Built with FastAPI & React
        </footer>
      </div>
    </Router>
  );
}

export default App;
