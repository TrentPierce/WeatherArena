import { LucideTrophy, LucideTrendingUp, LucideInfo, LucideLoader2 } from 'lucide-react';
import { useState, useEffect } from 'react';
import { supabase } from '@/lib/supabase';

type Ranking = {
    model_name: string;
    elo_score: number;
    elo_temp?: number;
    elo_wind?: number;
    elo_dewpoint?: number;
    total_verifications: number;
    last_updated: string;
};

type Metric = 'Composite' | 'Temp' | 'Wind' | 'Dew';

export default function Sidebar() {
    const [rankings, setRankings] = useState<Ranking[]>([]);
    const [loading, setLoading] = useState(true);
    const [metric, setMetric] = useState<Metric>('Temp');

    useEffect(() => {
        fetchRankings();

        // Subscribe to real-time changes
        const subscription = supabase
            .channel('public:model_rankings')
            .on('postgres_changes', { event: '*', schema: 'public', table: 'model_rankings' }, fetchRankings)
            .subscribe();

        return () => {
            subscription.unsubscribe();
        };
    }, []);

    const fetchRankings = async () => {
        try {
            const { data, error } = await supabase
                .from('model_rankings')
                .select('*')
                .order('elo_score', { ascending: false });

            if (error) throw error;
            if (data) setRankings(data);
        } catch (e) {
            console.error('Error fetching rankings:', e);
        } finally {
            setLoading(false);
        }
    };

    const getSortedRankings = () => {
        return [...rankings].sort((a, b) => {
            let scoreA = a.elo_score;
            let scoreB = b.elo_score;

            if (metric === 'Temp') {
                scoreA = a.elo_temp || 1200;
                scoreB = b.elo_temp || 1200;
            } else if (metric === 'Wind') {
                scoreA = a.elo_wind || 1200;
                scoreB = b.elo_wind || 1200;
            } else if (metric === 'Dew') {
                scoreA = a.elo_dewpoint || 1200;
                scoreB = b.elo_dewpoint || 1200;
            }
            return scoreB - scoreA;
        });
    };

    const sortedRankings = getSortedRankings();

    return (
        <div className="absolute top-4 left-4 z-[500] w-80 glass rounded-xl p-4 text-white shadow-2xl overflow-y-auto max-h-[90vh]">
            <div className="flex items-center space-x-2 mb-6">
                <LucideTrendingUp className="text-blue-400" />
                <h1 className="text-xl font-bold bg-clip-text text-transparent bg-gradient-to-r from-blue-400 to-teal-400">
                    WeatherArena
                </h1>
            </div>

            <div className="space-y-6">
                <section>
                    <div className="flex items-center justify-between mb-3">
                        <h2 className="text-sm uppercase tracking-wider text-slate-400 font-semibold flex items-center">
                            <LucideTrophy className="w-4 h-4 mr-2 text-yellow-500" /> Leaderboard
                        </h2>
                        <div className="flex bg-slate-800 rounded p-1">
                            {(['Temp', 'Wind', 'Dew'] as Metric[]).map(c => (
                                <button
                                    key={c}
                                    onClick={() => setMetric(c)}
                                    className={`px-2 py-0.5 text-[10px] rounded hover:bg-slate-700 transition ${metric === c ? 'bg-slate-600 text-white' : 'text-slate-400'}`}
                                >
                                    {c}
                                </button>
                            ))}
                        </div>
                    </div>

                    {loading ? (
                        <div className="flex justify-center py-8">
                            <LucideLoader2 className="animate-spin text-slate-500" />
                        </div>
                    ) : sortedRankings.length === 0 ? (
                        <div className="text-center py-4 text-slate-500 text-xs italic">
                            No rankings available yet.
                        </div>
                    ) : (
                        <div className="space-y-2">
                            {sortedRankings.map((model, index) => {
                                let displayScore = model.elo_score;
                                if (metric === 'Temp') displayScore = model.elo_temp || 1200;
                                else if (metric === 'Wind') displayScore = model.elo_wind || 1200;
                                else if (metric === 'Dew') displayScore = model.elo_dewpoint || 1200;

                                return (
                                    <div key={model.model_name} className="flex items-center justify-between p-3 rounded-lg glass-card hover:bg-white/5 transition cursor-pointer group">
                                        <div className="flex items-center space-x-3">
                                            <span className={`font-mono font-bold ${index === 0 ? 'text-yellow-400' : 'text-slate-300'}`}>#{index + 1}</span>
                                            <span className="font-medium group-hover:text-blue-300 transition">{model.model_name}</span>
                                        </div>
                                        <div className="text-right">
                                            <div className="font-bold text-sm bg-slate-800 px-2 py-0.5 rounded">{displayScore.toFixed(0)}</div>
                                            <div className="text-[10px] mt-1 text-slate-500">
                                                {model.total_verifications} matches
                                            </div>
                                        </div>
                                    </div>
                                );
                            })}
                        </div>
                    )}
                </section>

                <section>
                    <h2 className="text-sm uppercase tracking-wider text-slate-400 mb-3 font-semibold flex items-center">
                        <LucideInfo className="w-4 h-4 mr-2 text-blue-400" /> Controls
                    </h2>
                    <div className="p-3 bg-slate-800/50 rounded-lg">
                        <div className="text-xs text-slate-400 mb-2">Lead Time</div>
                        <div className="flex space-x-1">
                            {['1h', '6h', '12h', '24h'].map(t => (
                                <button key={t} className="px-3 py-1 rounded bg-slate-700 hover:bg-slate-600 text-xs transition">
                                    {t}
                                </button>
                            ))}
                        </div>
                    </div>
                </section>
            </div>
        </div>
    );
}
