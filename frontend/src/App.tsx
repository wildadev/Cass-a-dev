import { useState, useEffect } from 'react';
import Sidebar from './components/Sidebar';
import type { PanelName } from './components/Sidebar';
import { checkOnboarding } from './api/client';
import Dashboard from './components/Dashboard';
import ChatPanel from './components/ChatPanel';
import EmailViewer from './components/EmailViewer';
import CalendarView from './components/CalendarView';
import TaskBoard from './components/TaskBoard';
import ActivityLog from './components/ActivityLog';
import Onboarding from './components/Onboarding';

const panels: Record<PanelName, React.ComponentType> = {
  dashboard: Dashboard,
  chat: ChatPanel,
  email: EmailViewer,
  calendar: CalendarView,
  tasks: TaskBoard,
  activity: ActivityLog,
};

export default function App() {
  const [activePanel, setActivePanel] = useState<PanelName>('dashboard');
  const [showOnboarding, setShowOnboarding] = useState(false);

  useEffect(() => {
    checkOnboarding()
      .then((status) => {
        if (!status.completed) {
          setShowOnboarding(true);
        }
      })
      .catch(() => {
        // If the API is not available yet, skip onboarding check
      });
  }, []);

  const ActiveComponent = panels[activePanel];

  return (
    <div className="flex min-h-screen w-full bg-[#1e1e2e]">
      <Sidebar activePanel={activePanel} onNavigate={setActivePanel} />

      {/* Main content area */}
      <main className="flex-1 flex flex-col min-h-screen pb-16 md:pb-0">
        <ActiveComponent />
      </main>

      {/* Onboarding modal */}
      {showOnboarding && (
        <Onboarding onComplete={() => setShowOnboarding(false)} />
      )}
    </div>
  );
}
