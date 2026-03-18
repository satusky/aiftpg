import { Routes, Route } from 'react-router-dom';
import Layout from './components/Layout';
import LeaderboardPage from './pages/LeaderboardPage';
import TeamDetailPage from './pages/TeamDetailPage';

export default function App() {
  return (
    <Routes>
      <Route element={<Layout />}>
        <Route path="/" element={<LeaderboardPage />} />
        <Route path="/teams/:teamName" element={<TeamDetailPage />} />
      </Route>
    </Routes>
  );
}
