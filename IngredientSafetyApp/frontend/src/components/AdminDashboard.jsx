import React, { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, PieChart, Pie, Cell } from 'recharts';
import { Users, AlertTriangle, Database, Lock, Search } from 'lucide-react';
import axios from 'axios';

const AdminDashboard = () => {
    const [isAuthenticated, setIsAuthenticated] = useState(false);
    const [password, setPassword] = useState('');
    const [stats, setStats] = useState(null);
    const [popular, setPopular] = useState([]);
    const [recent, setRecent] = useState([]);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState('');

    const handleLogin = (e) => {
        e.preventDefault();
        if (password === 'admin123') {
            setIsAuthenticated(true);
            fetchData();
        } else {
            setError('Invalid Password');
        }
    };

    const fetchData = async () => {
        setLoading(true);
        try {
            const [statsRes, popularRes, recentRes] = await Promise.all([
                axios.get('http://localhost:8000/admin/stats'),
                axios.get('http://localhost:8000/admin/popular'),
                axios.get('http://localhost:8000/admin/recent')
            ]);

            setStats(statsRes.data);
            setPopular(popularRes.data);
            setRecent(recentRes.data);
        } catch (err) {
            console.error(err);
        } finally {
            setLoading(false);
        }
    };

    if (!isAuthenticated) {
        return (
            <div className="flex flex-col items-center justify-center min-h-[60vh]">
                <div className="glass-card p-8 max-w-md w-full">
                    <div className="flex justify-center mb-6">
                        <div className="p-4 bg-primary/20 rounded-full">
                            <Lock size={40} className="text-primary" />
                        </div>
                    </div>
                    <h2 className="text-2xl font-bold text-center text-white mb-6">Admin Access</h2>
                    <form onSubmit={handleLogin} className="space-y-4">
                        <input
                            type="password"
                            value={password}
                            onChange={(e) => setPassword(e.target.value)}
                            placeholder="Enter Admin Password"
                            className="w-full bg-black/40 border border-white/10 rounded-lg p-3 text-white focus:outline-none focus:border-primary"
                        />
                        {error && <p className="text-danger text-sm text-center">{error}</p>}
                        <button
                            type="submit"
                            className="w-full bg-primary text-black font-bold py-3 rounded-lg hover:bg-emerald-400 transition-colors"
                        >
                            Login
                        </button>
                    </form>
                </div>
            </div>
        );
    }

    if (loading || !stats) {
        return <div className="text-center text-white mt-20">Loading Dashboard Data...</div>;
    }

    const pieData = [
        { name: 'Safe', value: stats.total_ingredients - stats.hazardous_count },
        { name: 'Hazardous', value: stats.hazardous_count }
    ];
    const COLORS = ['#10B981', '#EF4444']; // Emerald-500, Red-500

    return (
        <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            className="max-w-6xl mx-auto pb-12"
        >
            <h1 className="text-3xl font-bold text-white mb-8 flex items-center gap-3">
                <Database className="text-primary" /> Admin Analytics Dashboard
            </h1>

            {/* Stats Grid */}
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
                <StatCard icon={<Database />} label="Total Ingredients" value={stats.total_ingredients} color="bg-blue-500/10 text-blue-400 border-blue-500/20" />
                <StatCard icon={<AlertTriangle />} label="Hazardous Chemicals" value={stats.hazardous_count} color="bg-red-500/10 text-red-400 border-red-500/20" />
                <StatCard icon={<Search />} label="Shampoo Data" value={stats.shampoo_count} color="bg-purple-500/10 text-purple-400 border-purple-500/20" />
            </div>

            <div className="grid grid-cols-1 lg:grid-cols-2 gap-8 mb-8">
                {/* Popular Ingredients Chart */}
                <div className="glass-card p-6">
                    <h3 className="text-xl font-semibold text-white mb-6">Top High-Risk Ingredients</h3>
                    <div className="h-64">
                        <ResponsiveContainer width="100%" height="100%">
                            <BarChart data={popular} layout="vertical" margin={{ left: 40 }}>
                                <XAxis type="number" hide />
                                <YAxis dataKey="name" type="category" width={150} tick={{ fill: '#9CA3AF', fontSize: 12 }} />
                                <Tooltip
                                    contentStyle={{ backgroundColor: '#1F2937', border: 'none', borderRadius: '8px' }}
                                    itemStyle={{ color: '#fff' }}
                                />
                                <Bar dataKey="score" fill="#EF4444" radius={[0, 4, 4, 0]} barSize={20} />
                            </BarChart>
                        </ResponsiveContainer>
                    </div>
                </div>

                {/* Safety Ratio Pie Chart */}
                <div className="glass-card p-6 flex flex-col items-center">
                    <h3 className="text-xl font-semibold text-white mb-2">Database Safety Ratio</h3>
                    <div className="h-64 w-full">
                        <ResponsiveContainer width="100%" height="100%">
                            <PieChart>
                                <Pie
                                    data={pieData}
                                    cx="50%"
                                    cy="50%"
                                    innerRadius={60}
                                    outerRadius={80}
                                    paddingAngle={5}
                                    dataKey="value"
                                >
                                    {pieData.map((entry, index) => (
                                        <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                                    ))}
                                </Pie>
                                <Tooltip contentStyle={{ backgroundColor: '#1F2937', border: 'none', borderRadius: '8px' }} />
                            </PieChart>
                        </ResponsiveContainer>
                    </div>
                    <div className="flex gap-4 mt-4">
                        <div className="flex items-center gap-2">
                            <div className="w-3 h-3 rounded-full bg-emerald-500"></div>
                            <span className="text-gray-300">Safe</span>
                        </div>
                        <div className="flex items-center gap-2">
                            <div className="w-3 h-3 rounded-full bg-red-500"></div>
                            <span className="text-gray-300">Hazardous</span>
                        </div>
                    </div>
                </div>
            </div>

            {/* Recent Scans Table */}
            <div className="glass-card p-6">
                <h3 className="text-xl font-semibold text-white mb-6">Most Recently Added Ingredients</h3>
                <div className="overflow-x-auto">
                    <table className="w-full text-left">
                        <thead>
                            <tr className="border-b border-white/10 text-gray-400 text-sm">
                                <th className="pb-3 pl-4">ID</th>
                                <th className="pb-3">Name</th>
                                <th className="pb-3">Category</th>
                                <th className="pb-3">Score</th>
                                <th className="pb-3">Status</th>
                            </tr>
                        </thead>
                        <tbody className="text-gray-300 text-sm">
                            {recent.map((item) => (
                                <tr key={item.id} className="border-b border-white/5 hover:bg-white/5 transition-colors">
                                    <td className="py-3 pl-4 text-gray-500">#{item.id}</td>
                                    <td className="py-3 font-medium text-white">{item.name}</td>
                                    <td className="py-3 capitalize">{item.category}</td>
                                    <td className="py-3">
                                        <span className={`font-bold ${item.score >= 7 ? 'text-red-400' : 'text-emerald-400'}`}>
                                            {item.score}/10
                                        </span>
                                    </td>
                                    <td className="py-3">
                                        {item.is_restricted ? (
                                            <span className="px-2 py-1 bg-red-500/20 text-red-400 rounded text-xs border border-red-500/20">Restricted</span>
                                        ) : (
                                            <span className="px-2 py-1 bg-emerald-500/20 text-emerald-400 rounded text-xs border border-emerald-500/20">Allowed</span>
                                        )}
                                    </td>
                                </tr>
                            ))}
                        </tbody>
                    </table>
                </div>
            </div>
        </motion.div>
    );
};

const StatCard = ({ icon, label, value, color }) => (
    <div className={`glass-card p-6 flex items-center gap-4 border ${color.split(' ')[2]} bg-opacity-10`}>
        <div className={`p-3 rounded-lg ${color.split(' ')[0]} ${color.split(' ')[1]}`}>
            {icon}
        </div>
        <div>
            <p className="text-gray-400 text-xs uppercase font-bold tracking-wider">{label}</p>
            <p className="text-2xl font-bold text-white">{value}</p>
        </div>
    </div>
);

export default AdminDashboard;
