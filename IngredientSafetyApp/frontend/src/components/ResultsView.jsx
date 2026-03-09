import React from 'react';
import { motion } from 'framer-motion';
import SafetyGauge from './SafetyGauge';
import IngredientBreakdown from './IngredientBreakdown';
import { RefreshCw, AlertTriangle, Printer } from 'lucide-react';
import RecommendationsCard from './RecommendationsCard';

const ResultsView = ({ data, onReset }) => {
    // Handling both the old endpoint response (for safety) and the new endpoint
    const {
        overall_verdict,
        executive_summary,
        ingredients,
        ingredients_breakdown,
        combination_alerts,
        regulatory_flags,
        // Fallbacks for old format if needed temporarily:
        overall_safety_score, risk_level, key_concerns, missing_ingredients, recommendations
    } = data;

    // Convert string verdict to a number for the old gauge
    const fakeScore = overall_verdict === 'GREEN' ? 90 : overall_verdict === 'YELLOW' ? 60 : 20;
    const displayRisk = overall_verdict === 'GREEN' ? "SAFE" : overall_verdict === 'YELLOW' ? "CAUTION" : "WARNING";

    return (
        <motion.div
            initial={{ opacity: 0, y: 50 }}
            animate={{ opacity: 1, y: 0 }}
            className="max-w-4xl mx-auto w-full pb-10"
        >
            <div className="grid grid-cols-1 md:grid-cols-2 gap-8 mb-8">

                {/* Score Card */}
                <div className="glass-card p-8 flex flex-col items-center justify-center">
                    <SafetyGauge score={overall_safety_score !== undefined ? overall_safety_score : fakeScore} />
                    <div className="mt-6 text-center">
                        <h2 className="text-3xl font-bold text-white mb-2">{risk_level || displayRisk}</h2>
                        <p className="text-gray-400">
                            Based on {(ingredients || ingredients_breakdown || []).length} ingredients
                        </p>
                    </div>
                </div>

                {/* Summary Card */}
                <div className="glass-card p-8 flex flex-col justify-center">
                    <h3 className="text-xl font-semibold mb-4 text-white">Analysis Summary</h3>

                    {executive_summary ? (
                        <div className="text-gray-300 leading-relaxed text-sm lg:text-base">
                            {executive_summary}
                        </div>
                    ) : (
                        key_concerns && key_concerns.length > 0 ? (
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
                        )
                    )}
                </div>
            </div>

            {/* Recommendations Section */}
            {recommendations && recommendations.length > 0 && (
                <div className="mb-8">
                    <RecommendationsCard recommendations={recommendations} />
                </div>
            )}

            {/* NEW EXPERT UI: Combination Alerts */}
            {combination_alerts && combination_alerts.length > 0 && combination_alerts[0] !== "No significant interactions detected." && (
                <div className="mb-6 bg-primary/10 border border-primary/30 shadow-[0_0_15px_var(--color-primary)] p-5 rounded-xl">
                    <h3 className="text-lg font-semibold text-primary drop-shadow-[0_0_8px_var(--color-primary)] mb-3 flex items-center gap-2">
                        <RefreshCw size={18} className="animate-spin-slow" /> Chemistry Interaction Alerts
                    </h3>
                    <ul className="space-y-2">
                        {combination_alerts.map((alert, i) => (
                            <li key={i} className="text-sm text-gray-300 flex items-start gap-2">
                                <span className="text-primary mt-0.5 drop-shadow-[0_0_5px_var(--color-primary)]">•</span>
                                <span>{alert}</span>
                            </li>
                        ))}
                    </ul>
                </div>
            )}

            {/* NEW EXPERT UI: Regulatory Flags */}
            {regulatory_flags && regulatory_flags.length > 0 && regulatory_flags[0] !== "No mandatory regulatory flags triggered." && (
                <div className="mb-8 bg-danger/10 border border-danger/30 shadow-[0_0_15px_var(--color-danger)] p-5 rounded-xl">
                    <h3 className="text-lg font-semibold text-danger drop-shadow-[0_0_8px_var(--color-danger)] mb-3 flex items-center gap-2">
                        <AlertTriangle size={18} /> Regulatory Warnings ({data.region})
                    </h3>
                    <ul className="space-y-2">
                        {regulatory_flags.map((flag, i) => (
                            <li key={i} className="text-sm text-gray-300 flex items-start gap-2">
                                <span className="text-danger mt-0.5 drop-shadow-[0_0_5px_var(--color-danger)]">•</span>
                                <span className="leading-relaxed">{flag}</span>
                            </li>
                        ))}
                    </ul>
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
                ingredients={ingredients || ingredients_breakdown || []}
                category={data.product_type || data.category}
                targetAudience={data.target_group || data.target_audience}
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
