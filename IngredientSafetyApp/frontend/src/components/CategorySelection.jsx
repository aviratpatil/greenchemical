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
                className="flex flex-col items-center justify-center p-8 bg-black/60 backdrop-blur-lg rounded-2xl border border-white/10 hover:border-primary hover:shadow-[0_0_20px_var(--color-primary)] transition-all duration-300 cursor-pointer shadow-xl h-64"
            >
                <div className="bg-primary/20 p-4 rounded-full mb-4 shadow-[0_0_10px_var(--color-primary)]">
                    <User size={48} className="text-primary drop-shadow-[0_0_8px_var(--color-primary)]" />
                </div>
                <h3 className="text-2xl font-bold text-white mb-2 group-hover:text-primary transition-colors">For Adults</h3>
                <p className="text-gray-300 text-center">Standard safety analysis for adults.</p>
            </motion.button>

            <motion.button
                whileHover={{ scale: 1.05 }}
                whileTap={{ scale: 0.95 }}
                onClick={() => onSelect('baby')}
                className="flex flex-col items-center justify-center p-8 bg-black/60 backdrop-blur-lg rounded-2xl border border-white/10 hover:border-pink-500 hover:shadow-[0_0_20px_#ec4899] transition-all duration-300 cursor-pointer shadow-xl h-64"
            >
                <div className="bg-pink-500/20 p-4 rounded-full mb-4 shadow-[0_0_10px_#ec4899]">
                    <Baby size={48} className="text-pink-500 drop-shadow-[0_0_8px_#ec4899]" />
                </div>
                <h3 className="text-2xl font-bold text-white mb-2 group-hover:text-pink-400 transition-colors">For Baby</h3>
                <p className="text-gray-300 text-center">Stricter safety standards for sensitive skin.</p>
            </motion.button>
        </div>
    );
};

export default CategorySelection;
