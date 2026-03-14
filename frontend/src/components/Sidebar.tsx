import {
  LayoutDashboard,
  MessageSquare,
  Mail,
  Calendar,
  CheckSquare,
  Activity,
} from 'lucide-react';

export type PanelName = 'dashboard' | 'chat' | 'email' | 'calendar' | 'tasks' | 'activity';

interface NavItem {
  id: PanelName;
  label: string;
  icon: React.ComponentType<{ size?: number; className?: string }>;
}

const navItems: NavItem[] = [
  { id: 'dashboard', label: 'Dashboard', icon: LayoutDashboard },
  { id: 'chat', label: 'Chat', icon: MessageSquare },
  { id: 'email', label: 'Email', icon: Mail },
  { id: 'calendar', label: 'Calendar', icon: Calendar },
  { id: 'tasks', label: 'Tasks', icon: CheckSquare },
  { id: 'activity', label: 'Activity', icon: Activity },
];

interface SidebarProps {
  activePanel: PanelName;
  onNavigate: (panel: PanelName) => void;
}

export default function Sidebar({ activePanel, onNavigate }: SidebarProps) {
  return (
    <>
      {/* Desktop sidebar */}
      <aside className="hidden md:flex flex-col w-60 min-h-screen bg-slate-900 border-r border-slate-700/50">
        {/* Brand */}
        <div className="flex items-center gap-3 px-5 py-5 border-b border-slate-700/50">
          <div className="w-8 h-8 rounded-lg bg-indigo-600 flex items-center justify-center text-white font-bold text-sm">
            C
          </div>
          <span className="text-lg font-semibold text-slate-100 tracking-tight">
            Cass
          </span>
        </div>

        {/* Nav items */}
        <nav className="flex-1 flex flex-col gap-1 px-3 py-4">
          {navItems.map((item) => {
            const isActive = activePanel === item.id;
            const Icon = item.icon;
            return (
              <button
                key={item.id}
                onClick={() => onNavigate(item.id)}
                className={`
                  flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm font-medium
                  transition-colors duration-150 cursor-pointer w-full text-left
                  ${
                    isActive
                      ? 'bg-indigo-600/20 text-indigo-400'
                      : 'text-slate-400 hover:text-slate-200 hover:bg-slate-800'
                  }
                `}
              >
                <Icon size={20} />
                <span>{item.label}</span>
              </button>
            );
          })}
        </nav>

        {/* Footer */}
        <div className="px-5 py-4 border-t border-slate-700/50">
          <p className="text-xs text-slate-500">Executive Assistant</p>
        </div>
      </aside>

      {/* Mobile bottom tab bar */}
      <nav className="md:hidden fixed bottom-0 left-0 right-0 z-50 flex items-center justify-around bg-slate-900 border-t border-slate-700/50 px-2 py-2 safe-bottom">
        {navItems.slice(0, 5).map((item) => {
          const isActive = activePanel === item.id;
          const Icon = item.icon;
          return (
            <button
              key={item.id}
              onClick={() => onNavigate(item.id)}
              className={`
                flex flex-col items-center gap-1 px-3 py-1.5 rounded-lg
                transition-colors duration-150 cursor-pointer
                ${
                  isActive
                    ? 'text-indigo-400'
                    : 'text-slate-500 hover:text-slate-300'
                }
              `}
            >
              <Icon size={20} />
              <span className="text-[10px] font-medium">{item.label}</span>
            </button>
          );
        })}
      </nav>
    </>
  );
}
