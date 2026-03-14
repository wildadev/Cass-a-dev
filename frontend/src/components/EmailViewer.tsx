import { useState, useEffect } from 'react';
import {
  Mail,
  ExternalLink,
  Loader2,
  Star,
  Paperclip,
} from 'lucide-react';
import { checkGoogleAuth, type GoogleAuthStatus } from '../api/client';

interface PlaceholderEmail {
  id: string;
  from: string;
  subject: string;
  preview: string;
  time: string;
  unread: boolean;
  starred: boolean;
  hasAttachment: boolean;
}

const placeholderEmails: PlaceholderEmail[] = [
  {
    id: '1',
    from: 'Sarah Chen',
    subject: 'Q1 Report Review',
    preview: 'Hi, could you review the attached Q1 report before our meeting tomorrow?',
    time: '10:23 AM',
    unread: true,
    starred: false,
    hasAttachment: true,
  },
  {
    id: '2',
    from: 'Marketing Team',
    subject: 'Campaign Launch Updates',
    preview: 'The new campaign is set to go live next Monday. Here are the final assets...',
    time: '9:45 AM',
    unread: true,
    starred: true,
    hasAttachment: false,
  },
  {
    id: '3',
    from: 'David Park',
    subject: 'Re: Project Timeline',
    preview: 'Thanks for the update. I think we can push the deadline by a week if needed.',
    time: 'Yesterday',
    unread: false,
    starred: false,
    hasAttachment: false,
  },
  {
    id: '4',
    from: 'HR Department',
    subject: 'Benefits Enrollment Reminder',
    preview: 'This is a reminder that open enrollment closes at the end of this month.',
    time: 'Yesterday',
    unread: false,
    starred: false,
    hasAttachment: true,
  },
  {
    id: '5',
    from: 'Alex Rivera',
    subject: 'Lunch tomorrow?',
    preview: 'Hey! Want to grab lunch tomorrow? There is a new place downtown I have been wanting to try.',
    time: 'Mar 12',
    unread: false,
    starred: true,
    hasAttachment: false,
  },
];

export default function EmailViewer() {
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
            <Mail className="h-8 w-8 text-slate-500" />
          </div>
          <h2 className="mb-2 text-xl font-semibold text-slate-200">
            Connect Gmail
          </h2>
          <p className="mb-6 max-w-sm text-sm text-slate-400">
            Connect your Gmail account to see your emails and let Cass help manage your inbox.
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
          <Mail className="h-6 w-6 text-indigo-400" />
          Inbox
        </h1>
        {authStatus.email && (
          <span className="text-xs text-slate-500">{authStatus.email}</span>
        )}
      </div>

      <div className="divide-y divide-slate-700/50 rounded-xl bg-slate-800">
        {placeholderEmails.map((email) => (
          <button
            key={email.id}
            className="flex w-full items-start gap-3 px-4 py-3 text-left transition-colors hover:bg-slate-700/50"
          >
            <div className="mt-1 shrink-0">
              {email.starred ? (
                <Star className="h-4 w-4 fill-yellow-400 text-yellow-400" />
              ) : (
                <Star className="h-4 w-4 text-slate-600" />
              )}
            </div>
            <div className="min-w-0 flex-1">
              <div className="flex items-baseline justify-between gap-2">
                <p
                  className={`truncate text-sm ${
                    email.unread
                      ? 'font-semibold text-slate-100'
                      : 'font-medium text-slate-300'
                  }`}
                >
                  {email.from}
                </p>
                <span className="shrink-0 text-xs text-slate-500">{email.time}</span>
              </div>
              <p
                className={`truncate text-sm ${
                  email.unread ? 'text-slate-200' : 'text-slate-400'
                }`}
              >
                {email.subject}
              </p>
              <p className="truncate text-xs text-slate-500">{email.preview}</p>
            </div>
            {email.hasAttachment && (
              <Paperclip className="mt-2 h-3.5 w-3.5 shrink-0 text-slate-500" />
            )}
            {email.unread && (
              <div className="mt-2 h-2 w-2 shrink-0 rounded-full bg-indigo-500" />
            )}
          </button>
        ))}
      </div>
    </div>
  );
}
