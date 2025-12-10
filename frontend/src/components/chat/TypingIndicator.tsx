import { Link, Loader2 } from 'lucide-react';

interface TypingIndicatorProps {
  isAnalyzingLink?: boolean;
}

export function TypingIndicator({ isAnalyzingLink = false }: TypingIndicatorProps) {
  if (isAnalyzingLink) {
    return (
      <div className="flex justify-start animate-slide-up">
        <div className="bubble-assistant px-4 py-3">
          <div className="flex items-center gap-2 text-muted-foreground">
            <Loader2 className="w-4 h-4 animate-spin text-primary" />
            <span className="text-sm">Agent is reading the website...</span>
            <Link className="w-3.5 h-3.5 text-primary" />
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="flex justify-start animate-slide-up">
      <div className="bubble-assistant px-4 py-3">
        <div className="flex items-center gap-1.5">
          <div className="w-2 h-2 rounded-full bg-muted-foreground typing-dot" />
          <div className="w-2 h-2 rounded-full bg-muted-foreground typing-dot" />
          <div className="w-2 h-2 rounded-full bg-muted-foreground typing-dot" />
        </div>
      </div>
    </div>
  );
}
