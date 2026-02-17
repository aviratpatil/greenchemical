import React from 'react';
import { motion } from 'framer-motion';
import SafetyGauge from './SafetyGauge';
import IngredientBreakdown from './IngredientBreakdown';
import { RefreshCw, AlertTriangle, Printer } from 'lucide-react';
import RecommendationsCard from './RecommendationsCard';

const ResultsView = ({ data, onReset }) => {
    const { overall_safety_score, risk_level, key_concerns, ingredients_breakdown, missing_ingredients, recommendations } = data;

    return (
        <motion.div
            initial={{ opacity: 0, y: 50 }}
            animate={{ opacity: 1, y: 0 }}
            className="max-w-4xl mx-auto w-full pb-10"
        >
            <div className="grid grid-cols-1 md:grid-cols-2 gap-8 mb-8">

                {/* Score Card */}
                <div className="glass-card p-8 flex flex-col items-center justify-center">
                    <SafetyGauge score={overall_safety_score} />
                    <div className="mt-6 text-center">
                        <h2 className="text-3xl font-bold text-white mb-2">{risk_level}</h2>
                        <p className="text-gray-400">
                            Based on {ingredients_breakdown.length} ingredients
                        </p>
                    </div>
                </div>

                {/* Summary Card */}
                <div className="glass-card p-8">
                    <h3 className="text-xl font-semibold mb-4 text-white">Analysis Summary</h3>

                    {key_concerns && key_concerns.length > 0 ? (
                        <div className="space-y-3">
                            <p className="text-danger font-medium flex items-center gap-2">
                                <AlertTriangle size={18} /> Key Concerns Detected:
                            </p>
                            <ul className="list-disc list-inside text-gray-300 space-y-1">
                                {key_concerns.map((concern, i) => (
                                    <li key={i}>{concern}</li>
                                ))}
                            </ul>
                        </div>
                    ) : (
                        <div className="h-full flex flex-col justify-center">
                            <p className="text-primary font-medium mb-2">Clean Formulation</p>
                            <p className="text-gray-400">We didn't detect any restricted or highly hazardous chemicals in this list based on our database.</p>
                        </div>
                    )}
                </div>
            </div>

            {/* Recommendations Section */}
            {recommendations && recommendations.length > 0 && (
                <div className="mb-8">
                    <RecommendationsCard recommendations={recommendations} />
                </div>
            )}

            {missing_ingredients && missing_ingredients.length > 0 && (
                <div className="mb-6 bg-yellow-500/10 border border-yellow-500/20 p-4 rounded-xl flex items-center gap-3">
                    <AlertTriangle className="text-warning shrink-0" />
                    <p className="text-sm text-yellow-200">
                        <span className="font-bold">Unknown Ingredients:</span> We couldn't identify {missing_ingredients.length} item(s) ('{missing_ingredients[0]}'...). Results may be less accurate.
                    </p>
                </div>
            )}

            <IngredientBreakdown
                ingredients={ingredients_breakdown}
                category={data.category}
                targetAudience={data.target_audience}
            />

            <div className="mt-8 flex justify-center gap-4">
                <button
                    onClick={() => window.print()}
                    className="flex items-center gap-2 px-6 py-2 rounded-full border border-white/20 hover:bg-white/10 text-white transition-all bg-white/5"
                >
                    <Printer size={18} />
                    Print Report
                </button>
                <button
                    onClick={onReset}
                    className="flex items-center gap-2 px-6 py-2 rounded-full border border-white/20 hover:bg-white/10 text-white transition-all"
                >
                    <RefreshCw size={18} />
                    Scan Another Product
                </button>
            </div>

        </motion.div>
    );
};

export default ResultsView;
