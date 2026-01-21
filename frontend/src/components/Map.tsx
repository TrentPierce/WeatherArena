'use client';
import { MapContainer, TileLayer, ZoomControl, LayersControl, WMSTileLayer, Marker, Tooltip, useMap } from 'react-leaflet';
import { useState, useEffect } from 'react';
import 'leaflet/dist/leaflet.css';
import L from 'leaflet';

// Fix for default markers
// eslint-disable-next-line @typescript-eslint/no-explicit-any
delete (L.Icon.Default.prototype as any)._getIconUrl;
L.Icon.Default.mergeOptions({
    iconRetinaUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-icon-2x.png',
    iconUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-icon.png',
    shadowUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-shadow.png',
});

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

export default function Map() {
    const [radarTime, setRadarTime] = useState(new Date().getTime());
    const [currentRadar, setCurrentRadar] = useState('composite'); // 'composite' or radar code like 'bmx'

    const radarSites = [
        { name: 'Birmingham, AL', id: 'bmx', lat: 33.172, lon: -86.770 },
        { name: 'Jackson, MS', id: 'jan', lat: 32.318, lon: -90.078 },
        { name: 'New York, NY', id: 'okx', lat: 40.865, lon: -72.863 },
        { name: 'Los Angeles, CA', id: 'vqx', lat: 34.412, lon: -119.179 },
        { name: 'Chicago, IL', id: 'lot', lat: 41.604, lon: -88.085 },
    ];

    const activeSite = radarSites.find(s => s.id === currentRadar);

    // Custom Radar Icon
    const radarIcon = L.divIcon({
        className: 'radar-marker-icon',
        html: `<div class="w-4 h-4 rounded-full bg-emerald-500 border-2 border-white shadow-[0_0_10px_rgba(16,185,129,0.8)] animate-pulse"></div>`,
        iconSize: [16, 16],
        iconAnchor: [8, 8]
    });

    const [viewCenter, setViewCenter] = useState<[number, number]>([39.8283, -98.5795]);
    const [viewZoom, setViewZoom] = useState(4);

    useEffect(() => {
        const interval = setInterval(() => {
            setRadarTime(new Date().getTime());
        }, 5 * 60 * 1000); // Update every 5 minutes
        return () => clearInterval(interval);
    }, []);

    const handleRadarChange = (siteId: string) => {
        setCurrentRadar(siteId);
        const site = radarSites.find(s => s.id === siteId);
        if (site) {
            setViewCenter([site.lat, site.lon]);
            setViewZoom(8);
        } else {
            setViewCenter([39.8283, -98.5795]);
            setViewZoom(4);
        }
    };

    // Component to sync map view
    function ViewSync() {
        const map = useMap();
        useEffect(() => {
            map.setView(viewCenter, viewZoom, { animate: true, duration: 1.5 });
        }, [viewCenter, viewZoom]);
        return null;
    }

    return (
        <div className="relative h-full w-full">
            <MapContainer
                center={viewCenter}
                zoom={viewZoom}
                className="h-full w-full bg-slate-900"
                zoomControl={false}
            >
                <ViewSync />
                <LayersControl position="topright">
                    <LayersControl.BaseLayer checked name="Dark Matter">
                        <TileLayer
                            attribution='&copy; OpenStreetMap contributors & CartoDB'
                            url="https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png"
                        />
                    </LayersControl.BaseLayer>

                    <LayersControl.BaseLayer name="OpenStreetMap">
                        <TileLayer
                            attribution='&copy; OpenStreetMap contributors'
                            url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
                        />
                    </LayersControl.BaseLayer>

                    <LayersControl.Overlay name="Radar (NEXRAD)" checked>
                        {currentRadar === 'composite' ? (
                            <WMSTileLayer
                                key={`${radarTime}-${currentRadar}`}
                                url="https://mesonet.agron.iastate.edu/cgi-bin/wms/nexrad/n0q.cgi"
                                layers="nexrad-n0q"
                                format="image/png"
                                transparent={true}
                                opacity={0.7}
                                attribution="Iowa State University"
                            />
                        ) : (
                            <WMSTileLayer
                                key={`${radarTime}-${currentRadar}`}
                                url={`https://mesonet.agron.iastate.edu/cgi-bin/wms/nexrad/ridge.cgi?sector=${activeSite?.id}&prod=N0Q`}
                                layers="single"
                                format="image/png"
                                transparent={true}
                                opacity={0.8}
                                attribution="Iowa State University RIDGE"
                            />
                        )}
                    </LayersControl.Overlay>

                    <LayersControl.Overlay name="HRRR Temperature (2m)">
                        <TileLayer
                            url={`${API_URL}/tiles/hrrr/{z}/{x}/{y}.png`}
                            opacity={0.6}
                        />
                    </LayersControl.Overlay>

                    <LayersControl.Overlay name="GFS Temperature (2m)">
                        <TileLayer
                            url={`${API_URL}/tiles/gfs/{z}/{x}/{y}.png`}
                            opacity={0.6}
                        />
                    </LayersControl.Overlay>

                </LayersControl>

                {radarSites.map((site) => (
                    <Marker
                        key={site.id}
                        position={[site.lat, site.lon]}
                        icon={radarIcon}
                        eventHandlers={{
                            click: () => handleRadarChange(site.id)
                        }}
                    >
                        <Tooltip direction="top" offset={[0, -8]} opacity={1} permanent={false}>
                            <div className="bg-slate-900 text-white p-2 rounded border border-white/10 text-[10px] font-bold uppercase tracking-tighter cursor-pointer">
                                {site.name}
                                {currentRadar === site.id && <div className="text-emerald-400 mt-1 animate-pulse">● LIVE SCAN</div>}
                            </div>
                        </Tooltip>
                    </Marker>
                ))}

                <ZoomControl position="bottomright" />
            </MapContainer>

            {/* Radar Site Selector */}
            <div className="absolute bottom-6 left-6 z-[500] glass rounded-xl p-3 shadow-2xl border border-white/10 w-48">
                <div className="text-[10px] uppercase tracking-wider text-slate-400 font-bold mb-2 px-1 flex items-center justify-between">
                    <span>Radar Source</span>
                    <div className="flex items-center space-x-2">
                        <span className="w-1.5 h-1.5 rounded-full bg-emerald-500 animate-pulse"></span>
                        {currentRadar !== 'composite' && (
                            <button
                                onClick={() => handleRadarChange('composite')}
                                className="text-[8px] bg-slate-700 px-1 rounded hover:bg-slate-600 transition text-slate-300"
                            >
                                RESET
                            </button>
                        )}
                    </div>
                </div>
                <div className="space-y-1 max-h-48 overflow-y-auto custom-scrollbar">
                    <button
                        onClick={() => setCurrentRadar('composite')}
                        className={`w-full text-left px-2 py-1.5 rounded text-xs transition-all duration-200 border ${currentRadar === 'composite'
                            ? 'bg-emerald-500/20 text-emerald-300 border-emerald-500/30 font-semibold'
                            : 'text-slate-300 hover:bg-white/5 border-transparent'
                            }`}
                    >
                        CONUS Composite
                    </button>
                    {radarSites.map((site) => (
                        <button
                            key={site.id}
                            onClick={() => handleRadarChange(site.id)}
                            className={`w-full text-left px-2 py-1.5 rounded text-xs transition-all duration-200 border ${currentRadar === site.id
                                ? 'bg-emerald-500/20 text-emerald-300 border-emerald-500/30 font-semibold'
                                : 'text-slate-300 hover:bg-white/5 border-transparent'
                                }`}
                        >
                            {site.name}
                        </button>
                    ))}
                </div>
            </div>
        </div>
    );
}
