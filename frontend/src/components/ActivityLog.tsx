import { useState, useEffect, useCallback, useRef } from 'react';
import {
  Search,
  Activity,
  Mail,
  Calendar,
  CheckCircle,
  Loader2,
  ChevronDown,
} from 'lucide-react';
import { fetchActivity, type ActivityItem } from '../api/client';

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

function ToolBadge({ name }: { name: string }) {
  return (
    <span className="inline-block rounded-full bg-slate-700 px-2 py-0.5 text-xs text-slate-300">
      {name.replace(/_/g, ' ')}
    </span>
  );
}

export default function ActivityLog() {
  const [items, setItems] = useState<ActivityItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [loadingMore, setLoadingMore] = useState(false);
  const [hasMore, setHasMore] = useState(true);
  const [search, setSearch] = useState('');
  const debounceRef = useRef<ReturnType<typeof setTimeout> | null>(null);
  const PAGE_SIZE = 20;

  const loadItems = useCallback(
    async (query: string, append = false) => {
      if (append) {
        setLoadingMore(true);
      } else {
        setLoading(true);
      }

      try {
        const limit = append ? items.length + PAGE_SIZE : PAGE_SIZE;
        const data = await fetchActivity(query || undefined, limit);

        if (append) {
          setItems(data);
        } else {
          setItems(data);
        }

        setHasMore(data.length >= limit);
      } catch {
        if (!append) setItems([]);
      } finally {
        setLoading(false);
        setLoadingMore(false);
      }
    },
    [items.length]
  );

  // Initial load
  useEffect(() => {
    loadItems('');
  }, []); // eslint-disable-line react-hooks/exhaustive-deps

  // Debounced search
  useEffect(() => {
    if (debounceRef.current) {
      clearTimeout(debounceRef.current);
    }

    debounceRef.current = setTimeout(() => {
      loadItems(search);
    }, 300);

    return () => {
      if (debounceRef.current) {
        clearTimeout(debounceRef.current);
      }
    };
  }, [search]); // eslint-disable-line react-hooks/exhaustive-deps

  const handleLoadMore = () => {
    loadItems(search, true);
  };

  return (
    <div className="min-h-screen bg-slate-900 p-6">
      <h1 className="mb-6 flex items-center gap-2 text-2xl font-bold text-slate-200">
        <Activity className="h-6 w-6 text-green-400" />
        Activity Log
      </h1>

      {/* Search bar */}
      <div className="relative mb-6">
        <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-slate-400" />
        <input
          type="text"
          value={search}
          onChange={(e) => setSearch(e.target.value)}
          placeholder="Search activity..."
          className="w-full rounded-lg border border-slate-700 bg-slate-800 py-2.5 pl-10 pr-4 text-sm text-slate-200 placeholder-slate-400 focus:border-indigo-500 focus:outline-none"
        />
      </div>

      {/* Activity list */}
      {loading ? (
        <div className="flex items-center justify-center py-16">
          <Loader2 className="h-8 w-8 animate-spin text-indigo-400" />
        </div>
      ) : items.length === 0 ? (
        <div className="flex flex-col items-center justify-center py-16 text-slate-400">
          <Activity className="mb-3 h-10 w-10 text-slate-600" />
          <p className="text-sm">
            {search ? 'No matching activity found' : 'No activity yet'}
          </p>
        </div>
      ) : (
        <>
          <div className="space-y-2">
            {items.map((item) => (
              <div
                key={item.id}
                className="flex items-start gap-3 rounded-lg bg-slate-800 p-4"
              >
                <div className="mt-0.5">{activityIcon(item.type)}</div>
                <div className="min-w-0 flex-1">
                  <div className="flex flex-wrap items-center gap-2">
                    <p className="text-sm text-slate-200">{item.description}</p>
                    {item.type && <ToolBadge name={item.type} />}
                  </div>
                  <p className="mt-1 text-xs text-slate-500">
                    {new Date(item.timestamp).toLocaleString()}
                  </p>
                </div>
              </div>
            ))}
          </div>

          {hasMore && (
            <div className="mt-6 flex justify-center">
              <button
                onClick={handleLoadMore}
                disabled={loadingMore}
                className="inline-flex items-center gap-2 rounded-lg border border-slate-700 bg-slate-800 px-4 py-2 text-sm text-slate-300 transition-colors hover:bg-slate-700 disabled:opacity-50"
              >
                {loadingMore ? (
                  <Loader2 className="h-4 w-4 animate-spin" />
                ) : (
                  <ChevronDown className="h-4 w-4" />
                )}
                Load More
              </button>
            </div>
          )}
        </>
      )}
    </div>
  );
}
