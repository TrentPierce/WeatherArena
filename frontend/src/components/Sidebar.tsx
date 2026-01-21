import { LucideTrophy, LucideTrendingUp, LucideInfo } from 'lucide-react';

export default function Sidebar() {
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
                            {['Temp', 'Wind', 'Dew'].map(c => (
                                <button key={c} className="px-2 py-0.5 text-[10px] rounded hover:bg-slate-700 text-slate-300">
                                    {c}
                                </button>
                            ))}
                        </div>
                    </div>

                    <div className="space-y-2">
                        {[
                            { name: 'HRRR', elo: 1350, rank: 1, change: '+12' },
                            { name: 'ECMWF', elo: 1320, rank: 2, change: '+5' },
                            { name: 'GFS', elo: 1280, rank: 3, change: '-3' },
                            { name: 'NAM (3km)', elo: 1210, rank: 4, change: '-8' },
                        ].map((model) => (
                            <div key={model.name} className="flex items-center justify-between p-3 rounded-lg glass-card hover:bg-white/5 transition cursor-pointer group">
                                <div className="flex items-center space-x-3">
                                    <span className={`font-mono font-bold ${model.rank === 1 ? 'text-yellow-400' : 'text-slate-300'}`}>#{model.rank}</span>
                                    <span className="font-medium group-hover:text-blue-300 transition">{model.name}</span>
                                </div>
                                <div className="text-right">
                                    <div className="font-bold text-sm bg-slate-800 px-2 py-0.5 rounded">{model.elo}</div>
                                    <div className={`text-[10px] mt-1 ${model.change.startsWith('+') ? 'text-green-400' : 'text-red-400'}`}>
                                        {model.change}
                                    </div>
                                </div>
                            </div>
                        ))}
                    </div>
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
