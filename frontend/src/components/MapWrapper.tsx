'use client';
import dynamic from 'next/dynamic';

const Map = dynamic(() => import('./Map'), {
    ssr: false,
    loading: () => (
        <div className="h-full w-full bg-slate-900 flex items-center justify-center">
            <div className="text-slate-500 animate-pulse">Loading Map Engine...</div>
        </div>
    )
});

export default Map;
