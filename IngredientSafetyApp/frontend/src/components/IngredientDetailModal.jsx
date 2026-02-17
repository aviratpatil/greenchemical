import React from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { X, Sparkles, AlertTriangle, ShieldCheck, Info } from 'lucide-react';
import ReactMarkdown from 'react-markdown';

const IngredientDetailModal = ({ isOpen, onClose, ingredient, details, isLoading }) => {
    if (!isOpen) return null;

    return (
        <AnimatePresence>
            <div className="fixed inset-0 z-50 flex items-center justify-center p-4">
                {/* Backdrop */}
                <motion.div
                    initial={{ opacity: 0 }}
                    animate={{ opacity: 1 }}
                    exit={{ opacity: 0 }}
                    onClick={onClose}
                    className="absolute inset-0 bg-black/60 backdrop-blur-sm"
                />

                {/* Modal Content */}
                <motion.div
                    initial={{ opacity: 0, scale: 0.9, y: 20 }}
                    animate={{ opacity: 1, scale: 1, y: 0 }}
                    exit={{ opacity: 0, scale: 0.9, y: 20 }}
                    className="relative bg-gray-900 border border-white/10 rounded-2xl w-full max-w-2xl max-h-[80vh] overflow-hidden shadow-2xl flex flex-col"
                >
                    {/* Header */}
                    <div className="p-6 border-b border-white/10 flex justify-between items-start bg-gray-800/50">
                        <div>
                            <div className="flex items-center gap-2 mb-1">
                                <Sparkles className="w-5 h-5 text-purple-400" />
                                <span className="text-xs font-mono text-purple-400 uppercase tracking-wider">Smart Analysis</span>
                            </div>
                            <h2 className="text-2xl font-bold text-white">{ingredient?.name}</h2>
                            {ingredient?.input_quantity && (
                                <span className="text-sm text-gray-400">Concentration: {ingredient.input_quantity}%</span>
                            )}
                        </div>
                        <button
                            onClick={onClose}
                            className="p-2 hover:bg-white/10 rounded-full transition-colors text-gray-400 hover:text-white"
                        >
                            <X className="w-5 h-5" />
                        </button>
                    </div>

                    {/* Body */}
                    <div className="p-6 overflow-y-auto custom-scrollbar flex-1">
                        {isLoading ? (
                            <div className="flex flex-col items-center justify-center py-12 space-y-4">
                                <div className="w-8 h-8 border-2 border-purple-500 border-t-transparent rounded-full animate-spin" />
                                <p className="text-gray-400 animate-pulse">Consulting the AI knowledge base...</p>
                            </div>
                        ) : details ? (
                            <div className="prose prose-invert prose-sm max-w-none">
                                <ReactMarkdown
                                    components={{
                                        h2: ({ node, ...props }) => <h3 className="text-xl font-semibold text-white mt-6 mb-3 flex items-center gap-2" {...props} />,
                                        h3: ({ node, ...props }) => <h4 className="text-lg font-medium text-gray-200 mt-4 mb-2" {...props} />,
                                        strong: ({ node, ...props }) => <span className="font-bold text-purple-300" {...props} />,
                                        ul: ({ node, ...props }) => <ul className="list-disc pl-5 space-y-1 text-gray-300" {...props} />,
                                        p: ({ node, ...props }) => <p className="text-gray-300 leading-relaxed mb-4" {...props} />,
                                    }}
                                >
                                    {details}
                                </ReactMarkdown>
                            </div>
                        ) : (
                            <div className="text-center py-8 text-gray-500">
                                <AlertTriangle className="w-8 h-8 mx-auto mb-2 opacity-50" />
                                <p>No details available.</p>
                            </div>
                        )}
                    </div>

                    {/* Footer */}
                    <div className="p-4 border-t border-white/10 bg-gray-800/30 text-xs text-gray-500 text-center">
                        AI-generated content. Verify with official sources for medical advice.
                    </div>
                </motion.div>
            </div>
        </AnimatePresence>
    );
};

export default IngredientDetailModal;
