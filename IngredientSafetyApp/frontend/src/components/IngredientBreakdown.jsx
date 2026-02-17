import React, { useState } from 'react';
import { AlertCircle, CheckCircle, ShieldAlert } from 'lucide-react';
import IngredientDetailModal from './IngredientDetailModal';
import { fetchIngredientDetails } from '../api';

const IngredientBreakdown = ({ ingredients, category = "shampoo", targetAudience = "adult" }) => {
    const [selectedIngredient, setSelectedIngredient] = useState(null);
    const [details, setDetails] = useState(null);
    const [isLoading, setIsLoading] = useState(false);
    const [isModalOpen, setIsModalOpen] = useState(false);

    const handleIngredientClick = async (ing) => {
        setSelectedIngredient(ing);
        setIsModalOpen(true);
        setIsLoading(true);
        setDetails(null);

        try {
            const data = await fetchIngredientDetails(
                ing.name,
                category,
                targetAudience,
                ing.input_quantity
            );
            setDetails(data.details);
        } catch (error) {
            setDetails("Failed to load details. Please try again.");
        } finally {
            setIsLoading(false);
        }
    };

    const handleCloseModal = () => {
        setIsModalOpen(false);
        setSelectedIngredient(null);
        setDetails(null);
    };

    return (
        <div className="glass-card p-6 mt-6">
            <h3 className="text-xl font-semibold mb-4 text-white">Ingredient Breakdown <span className="text-xs font-normal text-gray-400 ml-2">(Click ingredient for AI analysis)</span></h3>
            <div className="space-y-4 max-h-[400px] overflow-y-auto pr-2 custom-scrollbar">
                {ingredients.map((ing, idx) => {
                    // Calculate max score for color coding if not present
                    const scores = ing.scores || { general: ing.hazard_score || 0 };
                    let maxScore = 5;
                    // Handle scores being a string (JSON) or object
                    if (typeof scores === 'string') {
                        try {
                            const parsed = JSON.parse(scores);
                            maxScore = Math.max(...Object.values(parsed).filter(v => typeof v === 'number'));
                        } catch (e) { maxScore = 5; }
                    } else {
                        maxScore = Math.max(...Object.values(scores).filter(v => typeof v === 'number'));
                    }
                    if (!isFinite(maxScore)) maxScore = 5;


                    return (
                        <div
                            key={idx}
                            onClick={() => handleIngredientClick(ing)}
                            className="flex items-start gap-4 p-3 rounded-lg hover:bg-white/10 transition-colors border border-transparent hover:border-purple-500/30 cursor-pointer group"
                        >
                            {/* Icon based on max score */}
                            <div className="mt-1">
                                {maxScore >= 7 ? (
                                    <ShieldAlert className="text-danger" size={24} />
                                ) : maxScore >= 4 ? (
                                    <AlertCircle className="text-warning" size={24} />
                                ) : (
                                    <CheckCircle className="text-primary" size={24} />
                                )}
                            </div>

                            <div className="flex-1">
                                <div className="flex justify-between items-start">
                                    <h4 className="font-medium text-white group-hover:text-purple-300 transition-colors">{ing.name}</h4>
                                    <span
                                        className={`text-xs px-2 py-1 rounded-full font-bold
                        ${maxScore >= 7 ? 'bg-danger/20 text-danger' :
                                                maxScore >= 4 ? 'bg-warning/20 text-warning' :
                                                    'bg-primary/20 text-primary'}
                      `}
                                    >
                                        Max Hazard: {maxScore}/10
                                    </span>
                                </div>
                                <p className="text-sm text-gray-400 mt-1">{ing.description}</p>

                                {ing.quantity_validation && (
                                    <p className={`text-xs mt-1 font-semibold ${ing.quantity_validation.includes('Exceeds') ? 'text-danger' : 'text-primary'}`}>
                                        {ing.quantity_validation}
                                    </p>
                                )}

                                {/* Detailed Scores */}
                                <div className="mt-2 flex flex-wrap gap-2">
                                    {Object.entries(typeof scores === 'string' ? JSON.parse(scores) : scores).map(([key, value]) => (
                                        <div key={key} className="text-xs bg-white/5 px-2 py-1 rounded border border-white/10">
                                            <span className="text-gray-400 capitalize">{key.replace('_', ' ')}: </span>
                                            <span className={`font-bold ${value > 0 ? 'text-white' : 'text-gray-500'}`}>{value}</span>
                                        </div>
                                    ))}
                                </div>

                                {ing.is_restricted && (
                                    <p className="text-xs text-danger mt-1 font-semibold uppercase tracking-wider">
                                        Restricted / Banned
                                    </p>
                                )}
                                {ing.regulation && (
                                    <p className="text-xs text-gray-500 mt-1">
                                        Regulation: {ing.regulation}
                                    </p>
                                )}
                            </div>
                        </div>
                    );
                })}
            </div>

            <IngredientDetailModal
                isOpen={isModalOpen}
                onClose={handleCloseModal}
                ingredient={selectedIngredient}
                details={details}
                isLoading={isLoading}
            />
        </div>
    );
};

export default IngredientBreakdown;
