const BASE_URL = '';

async function request<T>(url: string, options?: RequestInit): Promise<T> {
  const res = await fetch(`${BASE_URL}${url}`, {
    headers: {
      'Content-Type': 'application/json',
    },
    ...options,
  });

  if (!res.ok) {
    const errorBody = await res.text().catch(() => '');
    throw new Error(`API error ${res.status}: ${errorBody || res.statusText}`);
  }

  return res.json() as Promise<T>;
}

export interface DashboardData {
  pending_tasks: number;
  completed_today: number;
  upcoming_events: number;
  unread_emails: number;
  recent_activity: ActivityItem[];
}

export interface Task {
  id: string;
  type: string;
  title: string;
  description: string;
  status: 'pending' | 'approved' | 'rejected' | 'completed';
  priority: 'low' | 'medium' | 'high';
  created_at: string;
  draft_content?: string;
}

export interface ActivityItem {
  id: string;
  type: string;
  title: string;
  description: string;
  timestamp: string;
}

export interface OnboardingStatus {
  completed: boolean;
  user_name?: string;
  assistant_name?: string;
}

export interface OnboardingData {
  user_name: string;
  assistant_name: string;
  assistant_persona: string;
}

export interface GoogleAuthStatus {
  authenticated: boolean;
  email?: string;
}

export interface FeedbackPayload {
  messageId: string;
  type: string;
  content?: string;
}

export function fetchDashboard(): Promise<DashboardData> {
  return request<DashboardData>('/api/dashboard');
}

export function fetchTasks(status?: string): Promise<Task[]> {
  const params = status ? `?status=${encodeURIComponent(status)}` : '';
  return request<Task[]>(`/api/tasks${params}`);
}

export function approveTask(id: string, editedContent?: string): Promise<Task> {
  return request<Task>(`/api/tasks/${id}/approve`, {
    method: 'PATCH',
    body: JSON.stringify({ edited_content: editedContent }),
  });
}

export function rejectTask(id: string, reason?: string): Promise<Task> {
  return request<Task>(`/api/tasks/${id}/reject`, {
    method: 'PATCH',
    body: JSON.stringify({ reason }),
  });
}

export function submitFeedback(
  messageId: string,
  type: string,
  content?: string
): Promise<{ success: boolean }> {
  return request<{ success: boolean }>('/api/feedback', {
    method: 'POST',
    body: JSON.stringify({ message_id: messageId, type, content }),
  });
}

export function fetchActivity(
  search?: string,
  limit?: number,
  offset?: number
): Promise<ActivityItem[]> {
  const params = new URLSearchParams();
  if (search) params.set('search', search);
  if (limit !== undefined) params.set('limit', String(limit));
  if (offset !== undefined) params.set('offset', String(offset));
  const qs = params.toString();
  return request<ActivityItem[]>(`/api/activity${qs ? `?${qs}` : ''}`);
}

export function checkOnboarding(): Promise<OnboardingStatus> {
  return request<OnboardingStatus>('/api/onboarding/status');
}

export function completeOnboarding(data: OnboardingData): Promise<{ success: boolean }> {
  return request<{ success: boolean }>('/api/onboarding', {
    method: 'POST',
    body: JSON.stringify(data),
  });
}

export function checkGoogleAuth(): Promise<GoogleAuthStatus> {
  return request<GoogleAuthStatus>('/auth/google/status');
}
