import { useState } from 'react';
import {
  ArrowRight,
  ArrowLeft,
  User,
  Bot,
  ExternalLink,
  SkipForward,
  Loader2,
} from 'lucide-react';
import { completeOnboarding } from '../api/client';

interface OnboardingProps {
  onComplete: () => void;
}

export default function Onboarding({ onComplete }: OnboardingProps) {
  const [step, setStep] = useState(0);
  const [userName, setUserName] = useState('');
  const [assistantName, setAssistantName] = useState('Cass');
  const [persona, setPersona] = useState('');
  const [submitting, setSubmitting] = useState(false);

  const handleComplete = async () => {
    setSubmitting(true);
    try {
      await completeOnboarding({
        user_name: userName.trim() || 'User',
        assistant_name: assistantName.trim() || 'Cass',
        assistant_persona: persona.trim(),
      });
      onComplete();
    } catch {
      // Allow proceeding even if API fails
      onComplete();
    } finally {
      setSubmitting(false);
    }
  };

  const handleNext = () => {
    if (step < 2) {
      setStep(step + 1);
    } else {
      handleComplete();
    }
  };

  const handleBack = () => {
    if (step > 0) setStep(step - 1);
  };

  const canProceed = () => {
    if (step === 0) return userName.trim().length > 0;
    return true;
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/60 backdrop-blur-sm">
      <div className="w-full max-w-md mx-4 rounded-2xl bg-slate-800 p-8 shadow-2xl">
        {/* Progress dots */}
        <div className="mb-8 flex items-center justify-center gap-2">
          {[0, 1, 2].map((i) => (
            <div
              key={i}
              className={`h-2 rounded-full transition-all ${
                i === step
                  ? 'w-8 bg-indigo-500'
                  : i < step
                  ? 'w-2 bg-indigo-400'
                  : 'w-2 bg-slate-600'
              }`}
            />
          ))}
        </div>

        {/* Step 1: User name */}
        {step === 0 && (
          <div className="text-center">
            <div className="mx-auto mb-4 flex h-14 w-14 items-center justify-center rounded-full bg-indigo-600/20">
              <User className="h-7 w-7 text-indigo-400" />
            </div>
            <h2 className="mb-2 text-xl font-bold text-slate-100">
              What's your name?
            </h2>
            <p className="mb-6 text-sm text-slate-400">
              This helps personalize your experience.
            </p>
            <input
              type="text"
              value={userName}
              onChange={(e) => setUserName(e.target.value)}
              onKeyDown={(e) => e.key === 'Enter' && canProceed() && handleNext()}
              placeholder="Enter your name"
              autoFocus
              className="w-full rounded-lg border border-slate-600 bg-slate-900 px-4 py-3 text-center text-slate-200 placeholder-slate-500 focus:border-indigo-500 focus:outline-none"
            />
          </div>
        )}

        {/* Step 2: Assistant name + persona */}
        {step === 1 && (
          <div className="text-center">
            <div className="mx-auto mb-4 flex h-14 w-14 items-center justify-center rounded-full bg-indigo-600/20">
              <Bot className="h-7 w-7 text-indigo-400" />
            </div>
            <h2 className="mb-2 text-xl font-bold text-slate-100">
              What should I call myself?
            </h2>
            <p className="mb-6 text-sm text-slate-400">
              Pick a name for your assistant.
            </p>
            <input
              type="text"
              value={assistantName}
              onChange={(e) => setAssistantName(e.target.value)}
              placeholder="Cass"
              autoFocus
              className="mb-4 w-full rounded-lg border border-slate-600 bg-slate-900 px-4 py-3 text-center text-slate-200 placeholder-slate-500 focus:border-indigo-500 focus:outline-none"
            />
            <textarea
              value={persona}
              onChange={(e) => setPersona(e.target.value)}
              placeholder="Describe my personality... (optional)"
              rows={3}
              className="w-full rounded-lg border border-slate-600 bg-slate-900 px-4 py-3 text-sm text-slate-200 placeholder-slate-500 focus:border-indigo-500 focus:outline-none"
            />
          </div>
        )}

        {/* Step 3: Google connect */}
        {step === 2 && (
          <div className="text-center">
            <div className="mx-auto mb-4 flex h-14 w-14 items-center justify-center rounded-full bg-indigo-600/20">
              <ExternalLink className="h-7 w-7 text-indigo-400" />
            </div>
            <h2 className="mb-2 text-xl font-bold text-slate-100">
              Connect your Google account
            </h2>
            <p className="mb-6 text-sm text-slate-400">
              Link Google to access your calendar and email. You can skip this for now.
            </p>
            <a
              href="/auth/google"
              className="mb-3 inline-flex w-full items-center justify-center gap-2 rounded-lg bg-indigo-600 px-5 py-3 text-sm font-medium text-white transition-colors hover:bg-indigo-500"
            >
              <ExternalLink className="h-4 w-4" />
              Connect Google
            </a>
            <button
              onClick={handleComplete}
              disabled={submitting}
              className="inline-flex w-full items-center justify-center gap-2 rounded-lg border border-slate-600 px-5 py-3 text-sm font-medium text-slate-300 transition-colors hover:bg-slate-700 disabled:opacity-50"
            >
              {submitting ? (
                <Loader2 className="h-4 w-4 animate-spin" />
              ) : (
                <SkipForward className="h-4 w-4" />
              )}
              Skip for now
            </button>
          </div>
        )}

        {/* Navigation buttons */}
        <div className="mt-8 flex items-center justify-between">
          {step > 0 ? (
            <button
              onClick={handleBack}
              className="inline-flex items-center gap-1 text-sm text-slate-400 transition-colors hover:text-slate-200"
            >
              <ArrowLeft className="h-4 w-4" />
              Back
            </button>
          ) : (
            <div />
          )}

          {step < 2 && (
            <button
              onClick={handleNext}
              disabled={!canProceed()}
              className="inline-flex items-center gap-1 rounded-lg bg-indigo-600 px-4 py-2 text-sm font-medium text-white transition-colors hover:bg-indigo-500 disabled:opacity-50"
            >
              Next
              <ArrowRight className="h-4 w-4" />
            </button>
          )}
        </div>
      </div>
    </div>
  );
}
