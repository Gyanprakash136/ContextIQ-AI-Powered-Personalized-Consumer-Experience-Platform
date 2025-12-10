import { useNavigate } from 'react-router-dom';
import { Button } from '@/components/ui/button';
import { useSessionStore } from '@/stores/sessionStore';
import { ArrowRight } from 'lucide-react';

export function LandingHero() {
  const navigate = useNavigate();
  const { isAuthenticated } = useSessionStore();

  const handleTryNow = () => {
    if (isAuthenticated) {
      navigate('/chat');
    } else {
      navigate('/auth');
    }
  };

  return (
    <section className="relative min-h-[80vh] flex items-center justify-center overflow-hidden">
      {/* Subtle gradient backdrop */}
      <div className="absolute inset-0 bg-gradient-to-b from-primary/5 via-transparent to-transparent" />
      <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[600px] h-[600px] bg-primary/5 rounded-full blur-3xl" />
      
      <div className="container relative z-10 text-center py-20">
        <div className="animate-fade-in">
          <p className="text-primary text-sm font-medium tracking-wide mb-4 uppercase">
            Your AI. Your Context. Your Way.
          </p>
        </div>
        
        <h1 className="text-4xl sm:text-5xl md:text-6xl font-semibold text-foreground max-w-3xl mx-auto leading-tight mb-6 animate-slide-up">
          Think faster. Create smarter.
        </h1>
        
        <p className="text-lg text-muted-foreground max-w-xl mx-auto mb-10 animate-slide-up" style={{ animationDelay: '0.1s' }}>
          Drop images, paste links, or just talk — AI that sees, reads, and understands.
        </p>
        
        <div className="flex flex-col sm:flex-row items-center justify-center gap-4 animate-slide-up" style={{ animationDelay: '0.2s' }}>
          <Button onClick={handleTryNow} size="lg" className="group">
            Try Now
            <ArrowRight className="w-4 h-4 group-hover:translate-x-1 transition-transform" />
          </Button>
          <Button variant="outline" size="lg" onClick={() => navigate('/auth')}>
            Sign In
          </Button>
        </div>
      </div>
    </section>
  );
}
