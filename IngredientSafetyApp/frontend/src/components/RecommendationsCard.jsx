import React from 'react';
import { Leaf, ArrowRight } from 'lucide-react';

const RecommendationsCard = ({ recommendations }) => {
    if (!recommendations || recommendations.length === 0) return null;

    return (
        <div className="glass-card p-8 bg-gradient-to-br from-emerald-900/40 to-black/40 border-emerald-500/30">
            <h3 className="text-xl font-semibold mb-6 text-emerald-400 flex items-center gap-2">
                <Leaf size={24} />
                Smart Recommendations
            </h3>

            <div className="space-y-6">
                {recommendations.map((rec, idx) => (
                    <div key={idx} className="bg-emerald-950/30 p-4 rounded-xl border border-emerald-500/20">
                        <div className="flex flex-col md:flex-row md:items-center gap-2 md:gap-4 mb-3">
                            <span className="text-red-300 font-medium line-through decoration-red-500/50">
                                {rec.bad_ingredient}
                            </span>
                            <ArrowRight className="hidden md:block text-emerald-500" size={20} />
                            <span className="text-emerald-300 font-bold">
                                {rec.alternatives[0]}
                            </span>
                        </div>

                        <p className="text-sm text-gray-300 mb-2">
                            <span className="text-emerald-400 font-medium">Why switch? </span>
                            {rec.reason}
                        </p>

                        <div className="flex flex-wrap gap-2 mt-3">
                            <span className="text-xs text-gray-500 uppercase font-bold tracking-wider">Also look for:</span>
                            {rec.alternatives.slice(1).map((alt, i) => (
                                <span key={i} className="text-xs px-2 py-1 rounded-md bg-emerald-500/10 text-emerald-400 border border-emerald-500/20">
                                    {alt}
                                </span>
                            ))}
                        </div>
                    </div>
                ))}
            </div>

            <p className="text-xs text-center text-gray-500 mt-6">
                * Recommendations based on dermatological research for gentler alternatives.
            </p>
        </div>
    );
};

export default RecommendationsCard;
