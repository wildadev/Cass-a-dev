import { useState, useEffect } from 'react';
import {
  CheckCircle,
  XCircle,
  Clock,
  Activity,
  AlertTriangle,
  Mail,
  Calendar,
  ChevronDown,
  ChevronUp,
  Loader2,
} from 'lucide-react';
import {
  fetchDashboard,
  approveTask,
  rejectTask,
  type DashboardData,
  type Task,
} from '../api/client';

interface PendingApproval extends Task {}

interface DashboardResponse extends DashboardData {
  pending_approvals?: PendingApproval[];
  active_tasks?: Task[];
}

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

function SkeletonCard() {
  return (
    <div className="animate-pulse rounded-xl bg-slate-800 p-6">
      <div className="mb-4 h-5 w-1/3 rounded bg-slate-700" />
      <div className="space-y-3">
        <div className="h-4 w-full rounded bg-slate-700" />
        <div className="h-4 w-2/3 rounded bg-slate-700" />
        <div className="h-4 w-1/2 rounded bg-slate-700" />
      </div>
    </div>
  );
}

function activityIcon(type: string) {
  switch (type) {
    case 'email':
      return <Mail className="h-4 w-4 text-indigo-400" />;
    case 'calendar':
      return <Calendar className="h-4 w-4 text-green-400" />;
    case 'task':
      return <CheckCircle className="h-4 w-4 text-yellow-400" />;
    default:
      return <Activity className="h-4 w-4 text-slate-400" />;
  }
}

export default function Dashboard() {
  const [data, setData] = useState<DashboardResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [expandedDrafts, setExpandedDrafts] = useState<Record<string, boolean>>({});
  const [draftEdits, setDraftEdits] = useState<Record<string, string>>({});
  const [actionLoading, setActionLoading] = useState<Record<string, boolean>>({});

  useEffect(() => {
    fetchDashboard()
      .then((d) => setData(d as DashboardResponse))
      .catch(() => setData(null))
      .finally(() => setLoading(false));
  }, []);

  const handleApprove = async (task: PendingApproval) => {
    setActionLoading((prev) => ({ ...prev, [task.id]: true }));
    try {
      const editedContent =
        task.type === 'email_draft' ? draftEdits[task.id] ?? task.draft_content : undefined;
      await approveTask(task.id, editedContent);
      setData((prev) => {
        if (!prev) return prev;
        return {
          ...prev,
          pending_approvals: prev.pending_approvals?.filter((t) => t.id !== task.id),
        };
      });
    } finally {
      setActionLoading((prev) => ({ ...prev, [task.id]: false }));
    }
  };

  const handleReject = async (task: PendingApproval) => {
    setActionLoading((prev) => ({ ...prev, [task.id]: true }));
    try {
      await rejectTask(task.id);
      setData((prev) => {
        if (!prev) return prev;
        return {
          ...prev,
          pending_approvals: prev.pending_approvals?.filter((t) => t.id !== task.id),
        };
      });
    } finally {
      setActionLoading((prev) => ({ ...prev, [task.id]: false }));
    }
  };

  const toggleDraft = (id: string, draftContent?: string) => {
    setExpandedDrafts((prev) => ({ ...prev, [id]: !prev[id] }));
    if (!draftEdits[id] && draftContent) {
      setDraftEdits((prev) => ({ ...prev, [id]: draftContent }));
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-slate-900 p-6">
        <h1 className="mb-6 text-2xl font-bold text-slate-200">Dashboard</h1>
        <div className="grid grid-cols-1 gap-6 md:grid-cols-2 lg:grid-cols-3">
          <SkeletonCard />
          <SkeletonCard />
          <SkeletonCard />
        </div>
      </div>
    );
  }

  const pendingApprovals = data?.pending_approvals ?? [];
  const activeTasks = data?.active_tasks ?? [];
  const recentActivity = (data?.recent_activity ?? []).slice(0, 5);

  return (
    <div className="min-h-screen bg-slate-900 p-6">
      <h1 className="mb-6 text-2xl font-bold text-slate-200">Dashboard</h1>

      {/* Stats row */}
      <div className="mb-8 grid grid-cols-2 gap-4 lg:grid-cols-4">
        {[
          { label: 'Pending Tasks', value: data?.pending_tasks ?? 0, icon: Clock },
          { label: 'Completed Today', value: data?.completed_today ?? 0, icon: CheckCircle },
          { label: 'Upcoming Events', value: data?.upcoming_events ?? 0, icon: Calendar },
          { label: 'Unread Emails', value: data?.unread_emails ?? 0, icon: Mail },
        ].map(({ label, value, icon: Icon }) => (
          <div key={label} className="rounded-xl bg-slate-800 p-4">
            <div className="flex items-center gap-2 text-slate-400">
              <Icon className="h-4 w-4" />
              <span className="text-sm">{label}</span>
            </div>
            <p className="mt-1 text-2xl font-bold text-slate-200">{value}</p>
          </div>
        ))}
      </div>

      {/* Card grid */}
      <div className="grid grid-cols-1 gap-6 md:grid-cols-2 lg:grid-cols-3">
        {/* Pending Approvals */}
        <div className="rounded-xl bg-slate-800 p-6">
          <h2 className="mb-4 flex items-center gap-2 text-lg font-semibold text-slate-200">
            <AlertTriangle className="h-5 w-5 text-yellow-400" />
            Pending Approvals
          </h2>
          {pendingApprovals.length === 0 ? (
            <p className="text-sm text-slate-400">No pending approvals</p>
          ) : (
            <ul className="space-y-3">
              {pendingApprovals.map((task) => (
                <li key={task.id} className="rounded-lg bg-slate-900 p-3">
                  <div className="flex items-start justify-between gap-2">
                    <div className="min-w-0 flex-1">
                      <p className="text-sm font-medium text-slate-200">{task.title}</p>
                      <TypeBadge type={task.type} />
                    </div>
                    <div className="flex shrink-0 gap-1">
                      <button
                        onClick={() => handleApprove(task)}
                        disabled={actionLoading[task.id]}
                        className="rounded p-1 text-green-400 hover:bg-green-600/20 disabled:opacity-50"
                        title="Approve"
                      >
                        {actionLoading[task.id] ? (
                          <Loader2 className="h-4 w-4 animate-spin" />
                        ) : (
                          <CheckCircle className="h-4 w-4" />
                        )}
                      </button>
                      <button
                        onClick={() => handleReject(task)}
                        disabled={actionLoading[task.id]}
                        className="rounded p-1 text-red-400 hover:bg-red-600/20 disabled:opacity-50"
                        title="Reject"
                      >
                        <XCircle className="h-4 w-4" />
                      </button>
                    </div>
                  </div>

                  {task.type === 'email_draft' && (
                    <>
                      <button
                        onClick={() => toggleDraft(task.id, task.draft_content)}
                        className="mt-2 flex items-center gap-1 text-xs text-indigo-400 hover:text-indigo-300"
                      >
                        {expandedDrafts[task.id] ? (
                          <>
                            <ChevronUp className="h-3 w-3" /> Hide Draft
                          </>
                        ) : (
                          <>
                            <ChevronDown className="h-3 w-3" /> View Draft
                          </>
                        )}
                      </button>
                      {expandedDrafts[task.id] && (
                        <textarea
                          className="mt-2 w-full rounded-md border border-slate-700 bg-slate-800 p-2 text-sm text-slate-200 focus:border-indigo-500 focus:outline-none"
                          rows={4}
                          value={draftEdits[task.id] ?? task.draft_content ?? ''}
                          onChange={(e) =>
                            setDraftEdits((prev) => ({ ...prev, [task.id]: e.target.value }))
                          }
                        />
                      )}
                    </>
                  )}
                </li>
              ))}
            </ul>
          )}
        </div>

        {/* Active Tasks */}
        <div className="rounded-xl bg-slate-800 p-6">
          <h2 className="mb-4 flex items-center gap-2 text-lg font-semibold text-slate-200">
            <Clock className="h-5 w-5 text-indigo-400" />
            Active Tasks
          </h2>
          {activeTasks.length === 0 ? (
            <p className="text-sm text-slate-400">No active tasks</p>
          ) : (
            <ul className="space-y-3">
              {activeTasks.map((task) => (
                <li key={task.id} className="rounded-lg bg-slate-900 p-3">
                  <p className="text-sm font-medium text-slate-200">{task.title}</p>
                  <div className="mt-1 flex items-center gap-2">
                    <PriorityBadge priority={task.priority} />
                    <span className="text-xs text-slate-400">
                      {new Date(task.created_at).toLocaleDateString()}
                    </span>
                  </div>
                </li>
              ))}
            </ul>
          )}
        </div>

        {/* Recent Activity */}
        <div className="rounded-xl bg-slate-800 p-6">
          <h2 className="mb-4 flex items-center gap-2 text-lg font-semibold text-slate-200">
            <Activity className="h-5 w-5 text-green-400" />
            Recent Activity
          </h2>
          {recentActivity.length === 0 ? (
            <p className="text-sm text-slate-400">No recent activity</p>
          ) : (
            <ul className="space-y-3">
              {recentActivity.map((item) => (
                <li key={item.id} className="flex items-start gap-3">
                  <div className="mt-0.5">{activityIcon(item.type)}</div>
                  <div className="min-w-0 flex-1">
                    <p className="text-sm text-slate-200">{item.description}</p>
                    <p className="text-xs text-slate-400">
                      {new Date(item.timestamp).toLocaleString()}
                    </p>
                  </div>
                </li>
              ))}
            </ul>
          )}
        </div>
      </div>
    </div>
  );
}
