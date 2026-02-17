import React, { useState } from 'react';
import ImageScanner from './ImageScanner';
import { Search, X, Loader2, Type, Camera } from 'lucide-react';
import { motion } from 'framer-motion';

const ScannerInput = ({ onAnalyze, isLoading }) => {
    const [text, setText] = useState('');
    const [category, setCategory] = useState('shampoo');
    const [inputMode, setInputMode] = useState('text'); // 'text' or 'scan'

    const handleSubmit = (e) => {
        e.preventDefault();
        if (text.trim()) {
            onAnalyze(text, category);
        }
    };

    const handleScanComplete = (scannedText) => {
        if (scannedText) {
            setText(scannedText);
            setInputMode('text'); // Switch back to text mode to review
        }
    };

    return (
        <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            className="max-w-2xl mx-auto w-full"
        >
            <div className="glass-card p-6 md:p-8">
                <h2 className="text-2xl font-bold mb-4 text-center text-primary">
                    Safe or Nightmare?
                </h2>

                <p className="text-gray-300 text-center mb-6">
                    Paste the ingredient list below.
                </p>

                {/* Input Mode Tabs */}
                <div className="flex border-b border-white/10 mb-6">
                    <button
                        className={`flex-1 pb-3 text-sm font-medium transition-colors relative ${inputMode === 'text' ? 'text-primary' : 'text-gray-400 hover:text-white'}`}
                        onClick={() => setInputMode('text')}
                    >
                        <span className="flex items-center justify-center gap-2">
                            <Type size={18} /> Type / Paste
                        </span>
                        {inputMode === 'text' && (
                            <motion.div layoutId="activeTab" className="absolute bottom-0 left-0 right-0 h-0.5 bg-primary" />
                        )}
                    </button>
                    <button
                        className={`flex-1 pb-3 text-sm font-medium transition-colors relative ${inputMode === 'scan' ? 'text-primary' : 'text-gray-400 hover:text-white'}`}
                        onClick={() => setInputMode('scan')}
                    >
                        <span className="flex items-center justify-center gap-2">
                            <Camera size={18} /> Scan Image
                        </span>
                        {inputMode === 'scan' && (
                            <motion.div layoutId="activeTab" className="absolute bottom-0 left-0 right-0 h-0.5 bg-primary" />
                        )}
                    </button>
                </div>

                {inputMode === 'scan' ? (
                    <div className="mb-6">
                        <ImageScanner onScanComplete={handleScanComplete} isLoading={isLoading} />
                    </div>
                ) : (
                    <form onSubmit={handleSubmit} className="relative">
                        <textarea
                            value={text}
                            onChange={(e) => setText(e.target.value)}
                            className="w-full h-40 bg-black/20 border border-white/10 rounded-xl p-4 text-white placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-primary resize-none transition-all"
                            placeholder="Aqua, Sodium Lauryl Sulfate, Retinol 0.5%..."
                            disabled={isLoading}
                        />

                        {text && !isLoading && (
                            <button
                                type="button"
                                onClick={() => setText('')}
                                className="absolute top-4 right-4 text-gray-400 hover:text-white transition-colors"
                            >
                                <X size={20} />
                            </button>
                        )}

                        <div className="mt-6 flex justify-center">
                            <button
                                type="submit"
                                disabled={isLoading || !text.trim()}
                                className={`
                flex items-center gap-2 px-8 py-3 rounded-full font-semibold text-white transition-all transform
                ${isLoading || !text.trim()
                                        ? 'bg-gray-700 cursor-not-allowed opacity-50'
                                        : 'bg-gradient-to-r from-primary to-emerald-600 hover:scale-105 shadow-lg shadow-emerald-500/20'}
              `}
                            >
                                {isLoading ? (
                                    <>
                                        <Loader2 className="animate-spin" size={20} />
                                        Analyzing...
                                    </>
                                ) : (
                                    <>
                                        <Search size={20} />
                                        Analyze Safety
                                    </>
                                )}
                            </button>
                        </div>
                    </form>
                )}
            </div>
        </motion.div>
    );
};

export default ScannerInput;
