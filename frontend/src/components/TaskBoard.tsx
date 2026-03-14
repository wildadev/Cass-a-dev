import { useState, useEffect } from 'react';
import {
  CheckCircle,
  XCircle,
  Clock,
  Loader2,
  ChevronDown,
  ChevronUp,
  Filter,
  ListChecks,
  PlayCircle,
  CheckSquare,
} from 'lucide-react';
import { fetchTasks, approveTask, rejectTask, type Task } from '../api/client';

type TabName = 'pending' | 'in_progress' | 'completed';

function PriorityBadge({ priority }: { priority: string }) {
  const colors: Record<string, string> = {
    high: 'bg-red-600/20 text-red-400',
    medium: 'bg-yellow-600/20 text-yellow-400',
    low: 'bg-green-600/20 text-green-400',
  };
  return (
    <span
      className={`inline-block rounded-full px-2 py-0.5 text-xs font-medium ${colors[priority] ?? 'bg-slate-700 text-slate-300'}`}
    >
      {priority}
    </span>
  );
}

function TypeBadge({ type }: { type: string }) {
  return (
    <span className="inline-block rounded-full bg-indigo-600/20 px-2 py-0.5 text-xs font-medium text-indigo-400">
      {type.replace(/_/g, ' ')}
    </span>
  );
}

function TaskCard({
  task,
  onApprove,
  onReject,
  actionLoading,
}: {
  task: Task;
  onApprove?: (task: Task, editedContent?: string) => void;
  onReject?: (task: Task) => void;
  actionLoading: boolean;
}) {
  const [expanded, setExpanded] = useState(false);
  const [draftEdit, setDraftEdit] = useState(task.draft_content ?? '');

  const isPending = task.status === 'pending';
  const isEmailDraft = task.type === 'email_draft';

  return (
    <div className="rounded-lg bg-slate-900 p-4">
      <div className="flex items-start justify-between gap-2">
        <div className="min-w-0 flex-1">
          <p className="text-sm font-medium text-slate-200">{task.title}</p>
          {task.description && (
            <p className="mt-1 line-clamp-2 text-xs text-slate-400">
              {task.description}
            </p>
          )}
          <div className="mt-2 flex flex-wrap items-center gap-2">
            <PriorityBadge priority={task.priority} />
            <TypeBadge type={task.type} />
            <span className="text-xs text-slate-500">
              {new Date(task.created_at).toLocaleDateString()}
            </span>
          </div>
        </div>

        {isPending && onApprove && onReject && (
          <div className="flex shrink-0 gap-1">
            <button
              onClick={() => onApprove(task, isEmailDraft ? draftEdit : undefined)}
              disabled={actionLoading}
              className="rounded p-1.5 text-green-400 hover:bg-green-600/20 disabled:opacity-50"
              title="Approve"
            >
              {actionLoading ? (
                <Loader2 className="h-4 w-4 animate-spin" />
              ) : (
                <CheckCircle className="h-4 w-4" />
              )}
            </button>
            <button
              onClick={() => onReject(task)}
              disabled={actionLoading}
              className="rounded p-1.5 text-red-400 hover:bg-red-600/20 disabled:opacity-50"
              title="Reject"
            >
              <XCircle className="h-4 w-4" />
            </button>
          </div>
        )}
      </div>

      {isPending && isEmailDraft && (
        <>
          <button
            onClick={() => setExpanded((prev) => !prev)}
            className="mt-2 flex items-center gap-1 text-xs text-indigo-400 hover:text-indigo-300"
          >
            {expanded ? (
              <>
                <ChevronUp className="h-3 w-3" /> Hide Draft
              </>
            ) : (
              <>
                <ChevronDown className="h-3 w-3" /> View Draft
              </>
            )}
          </button>
          {expanded && (
            <textarea
              className="mt-2 w-full rounded-md border border-slate-700 bg-slate-800 p-2 text-sm text-slate-200 focus:border-indigo-500 focus:outline-none"
              rows={5}
              value={draftEdit}
              onChange={(e) => setDraftEdit(e.target.value)}
            />
          )}
        </>
      )}
    </div>
  );
}

function SkeletonList() {
  return (
    <div className="animate-pulse space-y-3">
      {[1, 2, 3].map((i) => (
        <div key={i} className="rounded-lg bg-slate-900 p-4">
          <div className="mb-2 h-4 w-2/3 rounded bg-slate-700" />
          <div className="h-3 w-1/2 rounded bg-slate-700" />
        </div>
      ))}
    </div>
  );
}

const tabConfig: { id: TabName; label: string; icon: React.ComponentType<{ className?: string }> }[] = [
  { id: 'pending', label: 'Pending', icon: Clock },
  { id: 'in_progress', label: 'In Progress', icon: PlayCircle },
  { id: 'completed', label: 'Completed', icon: CheckSquare },
];

export default function TaskBoard() {
  const [tasks, setTasks] = useState<Task[]>([]);
  const [loading, setLoading] = useState(true);
  const [activeTab, setActiveTab] = useState<TabName>('pending');
  const [priorityFilter, setPriorityFilter] = useState<string>('all');
  const [actionLoading, setActionLoading] = useState<Record<string, boolean>>({});

  useEffect(() => {
    fetchTasks()
      .then((data) => setTasks(data))
      .catch(() => setTasks([]))
      .finally(() => setLoading(false));
  }, []);

  const handleApprove = async (task: Task, editedContent?: string) => {
    setActionLoading((prev) => ({ ...prev, [task.id]: true }));
    try {
      await approveTask(task.id, editedContent);
      setTasks((prev) =>
        prev.map((t) => (t.id === task.id ? { ...t, status: 'approved' } : t))
      );
    } finally {
      setActionLoading((prev) => ({ ...prev, [task.id]: false }));
    }
  };

  const handleReject = async (task: Task) => {
    setActionLoading((prev) => ({ ...prev, [task.id]: true }));
    try {
      await rejectTask(task.id);
      setTasks((prev) =>
        prev.map((t) => (t.id === task.id ? { ...t, status: 'rejected' } : t))
      );
    } finally {
      setActionLoading((prev) => ({ ...prev, [task.id]: false }));
    }
  };

  const statusMap: Record<TabName, string[]> = {
    pending: ['pending'],
    in_progress: ['approved'],
    completed: ['completed', 'rejected'],
  };

  const filtered = tasks.filter((t) => {
    const statusMatch = statusMap[activeTab].includes(t.status);
    const priorityMatch = priorityFilter === 'all' || t.priority === priorityFilter;
    return statusMatch && priorityMatch;
  });

  return (
    <div className="min-h-screen bg-slate-900 p-6">
      <div className="mb-6 flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
        <h1 className="flex items-center gap-2 text-2xl font-bold text-slate-200">
          <ListChecks className="h-6 w-6 text-indigo-400" />
          Tasks
        </h1>

        {/* Priority filter */}
        <div className="flex items-center gap-2">
          <Filter className="h-4 w-4 text-slate-400" />
          <select
            value={priorityFilter}
            onChange={(e) => setPriorityFilter(e.target.value)}
            className="rounded-lg border border-slate-700 bg-slate-800 px-3 py-1.5 text-sm text-slate-200 focus:border-indigo-500 focus:outline-none"
          >
            <option value="all">All priorities</option>
            <option value="high">High</option>
            <option value="medium">Medium</option>
            <option value="low">Low</option>
          </select>
        </div>
      </div>

      {/* Tabs */}
      <div className="mb-6 flex gap-1 rounded-lg bg-slate-800 p-1">
        {tabConfig.map(({ id, label, icon: Icon }) => (
          <button
            key={id}
            onClick={() => setActiveTab(id)}
            className={`flex flex-1 items-center justify-center gap-2 rounded-md px-3 py-2 text-sm font-medium transition-colors ${
              activeTab === id
                ? 'bg-indigo-600 text-white'
                : 'text-slate-400 hover:text-slate-200'
            }`}
          >
            <Icon className="h-4 w-4" />
            <span className="hidden sm:inline">{label}</span>
          </button>
        ))}
      </div>

      {/* Task list */}
      {loading ? (
        <SkeletonList />
      ) : filtered.length === 0 ? (
        <div className="flex flex-col items-center justify-center py-16 text-slate-400">
          <CheckSquare className="mb-3 h-10 w-10 text-slate-600" />
          <p className="text-sm">No tasks in this category</p>
        </div>
      ) : (
        <div className="grid grid-cols-1 gap-3 lg:grid-cols-2 xl:grid-cols-3">
          {filtered.map((task) => (
            <TaskCard
              key={task.id}
              task={task}
              onApprove={activeTab === 'pending' ? handleApprove : undefined}
              onReject={activeTab === 'pending' ? handleReject : undefined}
              actionLoading={!!actionLoading[task.id]}
            />
          ))}
        </div>
      )}
    </div>
  );
}
