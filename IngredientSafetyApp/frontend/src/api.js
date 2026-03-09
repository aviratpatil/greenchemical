import axios from 'axios';

const API_URL = 'http://localhost:8000';

export const analyzeIngredients = async (text, category = "shampoo", target_audience = "adult") => {
    // 1. Process text to array of ingredients
    const cleanText = text.replace(/^(Ingredients:|Contains:)\s*/i, '');
    const items = cleanText.split(/[,•\n]+/).map(i => i.trim()).filter(Boolean);

    try {
        const response = await axios.post(`${API_URL}/analyze/formulation`, {
            ingredient_list: items,
            product_type: category,
            region: "EU", // Defaulting to EU strict rules as per engine
            target_group: target_audience
        });
        return response.data;
    } catch (error) {
        console.error("Analysis failed:", error);
        throw error;
    }
};

export const fetchIngredientDetails = async (ingredient, category, target_audience, quantity = null) => {
    try {
        const response = await axios.post(`${API_URL}/analyze/details`, {
            ingredient,
            category,
            target_audience,
            quantity
        });
        return response.data;
    } catch (error) {
        console.error("Details fetch failed:", error);
        throw error;
    }
};
