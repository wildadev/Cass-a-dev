import { useState, useEffect } from 'react';
import {
  Calendar,
  Clock,
  ExternalLink,
  Loader2,
  MapPin,
} from 'lucide-react';
import { checkGoogleAuth, type GoogleAuthStatus } from '../api/client';

interface PlaceholderEvent {
  id: string;
  title: string;
  time: string;
  location?: string;
  day: string;
}

const todayEvents: PlaceholderEvent[] = [
  { id: '1', title: 'Team Standup', time: '9:00 AM - 9:30 AM', location: 'Google Meet', day: 'today' },
  { id: '2', title: 'Product Review', time: '11:00 AM - 12:00 PM', location: 'Room 3B', day: 'today' },
  { id: '3', title: '1:1 with Manager', time: '2:00 PM - 2:30 PM', location: 'Google Meet', day: 'today' },
];

const weekEvents: PlaceholderEvent[] = [
  { id: '4', title: 'Sprint Planning', time: '10:00 AM - 11:00 AM', location: 'Room 5A', day: 'Monday' },
  { id: '5', title: 'Design Sync', time: '3:00 PM - 3:30 PM', location: 'Google Meet', day: 'Tuesday' },
  { id: '6', title: 'All Hands', time: '4:00 PM - 5:00 PM', location: 'Main Hall', day: 'Wednesday' },
  { id: '7', title: 'Client Call', time: '1:00 PM - 2:00 PM', location: 'Zoom', day: 'Thursday' },
  { id: '8', title: 'Team Retro', time: '3:00 PM - 4:00 PM', location: 'Room 3B', day: 'Friday' },
];

function EventCard({ event }: { event: PlaceholderEvent }) {
  return (
    <div className="flex items-start gap-3 rounded-lg bg-slate-900 p-3">
      <div className="mt-0.5 rounded-md bg-indigo-600/20 p-1.5">
        <Clock className="h-4 w-4 text-indigo-400" />
      </div>
      <div className="min-w-0 flex-1">
        <p className="text-sm font-medium text-slate-200">{event.title}</p>
        <p className="text-xs text-slate-400">{event.time}</p>
        {event.location && (
          <p className="mt-1 flex items-center gap-1 text-xs text-slate-500">
            <MapPin className="h-3 w-3" />
            {event.location}
          </p>
        )}
      </div>
    </div>
  );
}

export default function CalendarView() {
  const [authStatus, setAuthStatus] = useState<GoogleAuthStatus | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    checkGoogleAuth()
      .then((status) => setAuthStatus(status))
      .catch(() => setAuthStatus({ authenticated: false }))
      .finally(() => setLoading(false));
  }, []);

  if (loading) {
    return (
      <div className="flex min-h-screen items-center justify-center bg-slate-900">
        <Loader2 className="h-8 w-8 animate-spin text-indigo-400" />
      </div>
    );
  }

  if (!authStatus?.authenticated) {
    return (
      <div className="flex min-h-screen items-center justify-center bg-slate-900 p-6">
        <div className="text-center">
          <div className="mx-auto mb-4 flex h-16 w-16 items-center justify-center rounded-full bg-slate-800">
            <Calendar className="h-8 w-8 text-slate-500" />
          </div>
          <h2 className="mb-2 text-xl font-semibold text-slate-200">
            Connect Google Calendar
          </h2>
          <p className="mb-6 max-w-sm text-sm text-slate-400">
            Connect your Google Calendar to see your events and let Cass help manage your schedule.
          </p>
          <a
            href="/auth/google"
            className="inline-flex items-center gap-2 rounded-lg bg-indigo-600 px-5 py-2.5 text-sm font-medium text-white transition-colors hover:bg-indigo-500"
          >
            <ExternalLink className="h-4 w-4" />
            Connect Google
          </a>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-slate-900 p-6">
      <div className="mb-6 flex items-center justify-between">
        <h1 className="flex items-center gap-2 text-2xl font-bold text-slate-200">
          <Calendar className="h-6 w-6 text-indigo-400" />
          Calendar
        </h1>
        {authStatus.email && (
          <span className="text-xs text-slate-500">{authStatus.email}</span>
        )}
      </div>

      {/* Today */}
      <div className="mb-8">
        <h2 className="mb-4 text-lg font-semibold text-slate-200">Today</h2>
        <div className="space-y-2">
          {todayEvents.map((event) => (
            <EventCard key={event.id} event={event} />
          ))}
        </div>
      </div>

      {/* This Week */}
      <div>
        <h2 className="mb-4 text-lg font-semibold text-slate-200">This Week</h2>
        <div className="space-y-2">
          {weekEvents.map((event) => (
            <div key={event.id}>
              <p className="mb-1 text-xs font-medium uppercase tracking-wider text-slate-500">
                {event.day}
              </p>
              <EventCard event={event} />
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
