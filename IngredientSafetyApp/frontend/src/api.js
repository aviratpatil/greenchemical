import axios from 'axios';

const API_URL = 'http://localhost:8000';

export const analyzeIngredients = async (text, category = "shampoo", target_audience = "adult") => {
    try {
        const response = await axios.post(`${API_URL}/analyze`, {
            text,
            category,
            target_audience
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
