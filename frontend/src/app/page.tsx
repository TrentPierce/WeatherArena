import MapWrapper from '../components/MapWrapper';
import Sidebar from '../components/Sidebar';

export default function Home() {
  return (
    <main className="relative h-screen w-full overflow-hidden">
      <Sidebar />
      <div className="absolute inset-0 z-0">
        <MapWrapper />
      </div>
    </main>
  );
}
