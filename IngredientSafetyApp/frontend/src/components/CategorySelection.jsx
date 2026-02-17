import React from 'react';
import { motion } from 'framer-motion';
import { Baby, User } from 'lucide-react';

const CategorySelection = ({ onSelect }) => {
    return (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6 p-6">
            <motion.button
                whileHover={{ scale: 1.05 }}
                whileTap={{ scale: 0.95 }}
                onClick={() => onSelect('adult')}
                className="flex flex-col items-center justify-center p-8 bg-white/10 backdrop-blur-lg rounded-2xl border border-white/20 hover:bg-white/20 transition-all cursor-pointer shadow-xl h-64"
            >
                <div className="bg-purple-500/20 p-4 rounded-full mb-4">
                    <User size={48} className="text-purple-300" />
                </div>
                <h3 className="text-2xl font-bold text-white mb-2">For Adults</h3>
                <p className="text-purple-200 text-center">Standard safety analysis for adults.</p>
            </motion.button>

            <motion.button
                whileHover={{ scale: 1.05 }}
                whileTap={{ scale: 0.95 }}
                onClick={() => onSelect('baby')}
                className="flex flex-col items-center justify-center p-8 bg-white/10 backdrop-blur-lg rounded-2xl border border-white/20 hover:bg-white/20 transition-all cursor-pointer shadow-xl h-64"
            >
                <div className="bg-pink-500/20 p-4 rounded-full mb-4">
                    <Baby size={48} className="text-pink-300" />
                </div>
                <h3 className="text-2xl font-bold text-white mb-2">For Baby</h3>
                <p className="text-pink-200 text-center">Stricter safety standards for sensitive skin.</p>
            </motion.button>
        </div>
    );
};

export default CategorySelection;
