'use client';
import { MapContainer, TileLayer, ZoomControl, LayersControl, WMSTileLayer } from 'react-leaflet';
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
    return (
        <MapContainer
            center={[39.8283, -98.5795]}
            zoom={4}
            className="h-full w-full bg-slate-900"
            zoomControl={false}
        >
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
                    <WMSTileLayer
                        url="https://mesonet.agron.iastate.edu/cgi-bin/wms/nexrad/n0r.cgi"
                        layers="nexrad-n0r-900913"
                        format="image/png"
                        transparent={true}
                        opacity={0.7}
                        attribution="Iowa State University"
                    />
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

            <ZoomControl position="bottomright" />
        </MapContainer>
    );
}
