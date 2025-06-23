import { Routes, Route, Navigate } from 'react-router-dom';
import Home from './pages/Home';
import QueryEditor from './pages/QueryEditor';
import Results from './pages/Results';
import History from './pages/History';

export default function App() {
  return (
    <div className="min-h-screen bg-gray-50 text-gray-900 font-sans">
      <Routes>
        <Route path="/" element={<Home />} />
        <Route path="/editor" element={<QueryEditor />} />
        <Route path="/results" element={<Results />} />
        <Route path="/history" element={<History />} />
        <Route path="*" element={<Navigate to="/" />} />
      </Routes>
    </div>
  );
}
