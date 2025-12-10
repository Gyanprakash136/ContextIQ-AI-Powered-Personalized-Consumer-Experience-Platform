import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { useSessionStore } from '@/stores/sessionStore';
import { toast } from 'sonner';
import { Loader2 } from 'lucide-react';

type AuthMode = 'signin' | 'signup';

export function AuthForm() {
  const navigate = useNavigate();
  /* eslint-disable @typescript-eslint/no-unused-vars */
  const { login, loginAsGuest } = useSessionStore();

  const [mode, setMode] = useState<AuthMode>('signin');
  const [isLoading, setIsLoading] = useState(false);
  // Email auth placeholders
  const [formData, setFormData] = useState({
    name: '',
    email: '',
    password: '',
    confirmPassword: '',
  });
  const [errors, setErrors] = useState<Record<string, string>>({});

  const handleGoogleLogin = async () => {
    try {
      await login();
      toast.success('Welcome back!');
      navigate('/chat');
    } catch (error) {
      toast.error('Google Sign-In failed.');
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    toast.info("Please use Google Sign-In for this demo.");
  };

  return (
    <div className="w-full max-w-2xl mx-auto">
      <div className="bg-transparent backdrop-blur-md border border-white/10 rounded-2xl p-6 md:p-8 shadow-2xl animate-scale-in transition-all duration-300">
        <div className="flex flex-col items-center mb-6">
          <h2 className="text-2xl font-bold font-display text-white mb-2">
            {mode === 'signin' ? 'Welcome Back' : 'Create Account'}
          </h2>
          <p className="text-text-muted text-sm text-center">
            Enter your details to access the agentic layer.
          </p>
        </div>

        {/* Toggle */}
        <div className="flex bg-black/40 rounded-lg p-1 mb-6 border border-white/5 max-w-sm mx-auto w-full">
          <button
            onClick={() => setMode('signin')}
            className={`flex-1 py-2 text-sm font-medium rounded-md transition-all duration-300 ${mode === 'signin'
              ? 'bg-white/10 text-white shadow-sm'
              : 'text-text-muted hover:text-white hover:bg-white/5'
              }`}
          >
            Sign In
          </button>
          <button
            onClick={() => setMode('signup')}
            className={`flex-1 py-2 text-sm font-medium rounded-md transition-all duration-300 ${mode === 'signup'
              ? 'bg-white/10 text-white shadow-sm'
              : 'text-text-muted hover:text-white hover:bg-white/5'
              }`}
          >
            Sign Up
          </button>
        </div>

        <form onSubmit={handleSubmit} className="space-y-4">
          <div className={mode === 'signup' ? 'grid grid-cols-1 md:grid-cols-2 gap-4 space-y-0' : 'space-y-4'}>
            {mode === 'signup' && (
              <div className="space-y-1">
                <Input
                  placeholder="Name"
                  value={formData.name}
                  onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                  aria-label="Name"
                  className="bg-black/40 border-white/10 text-white placeholder:text-white/30 focus-visible:ring-1 focus-visible:ring-white/30 focus-visible:border-white/30 transition-all h-11"
                />
                {errors.name && (
                  <p className="text-destructive text-xs ml-1">{errors.name}</p>
                )}
              </div>
            )}

            <div className="space-y-1">
              <Input
                type="email"
                placeholder="Email"
                value={formData.email}
                onChange={(e) => setFormData({ ...formData, email: e.target.value })}
                aria-label="Email"
                className="bg-black/40 border-white/10 text-white placeholder:text-white/30 focus-visible:ring-1 focus-visible:ring-white/30 focus-visible:border-white/30 transition-all h-11"
              />
              {errors.email && (
                <p className="text-destructive text-xs ml-1">{errors.email}</p>
              )}
            </div>

            <div className="space-y-1">
              <Input
                type="password"
                placeholder="Password"
                value={formData.password}
                onChange={(e) => setFormData({ ...formData, password: e.target.value })}
                aria-label="Password"
                className="bg-black/40 border-white/10 text-white placeholder:text-white/30 focus-visible:ring-1 focus-visible:ring-white/30 focus-visible:border-white/30 transition-all h-11"
              />
              {errors.password && (
                <p className="text-destructive text-xs ml-1">{errors.password}</p>
              )}
            </div>

            {mode === 'signup' && (
              <div className="space-y-1">
                <Input
                  type="password"
                  placeholder="Confirm Password"
                  value={formData.confirmPassword}
                  onChange={(e) => setFormData({ ...formData, confirmPassword: e.target.value })}
                  aria-label="Confirm Password"
                  className="bg-black/40 border-white/10 text-white placeholder:text-white/30 focus-visible:ring-1 focus-visible:ring-white/30 focus-visible:border-white/30 transition-all h-11"
                />
                {errors.confirmPassword && (
                  <p className="text-destructive text-xs ml-1">{errors.confirmPassword}</p>
                )}
              </div>
            )}
          </div>

          <Button type="submit" className="w-full bg-primary hover:bg-primary/90 text-white font-semibold h-11 shadow-lg shadow-primary/20 transition-all duration-300 group mt-2" disabled={isLoading}>
            <span className="flex items-center gap-2 group-hover:scale-105 transition-transform">
              {isLoading ? (
                <Loader2 className="w-4 h-4 animate-spin" />
              ) : mode === 'signin' ? (
                'Sign In'
              ) : (
                'Create Account'
              )}
            </span>
          </Button>
        </form>

        {/* Divider */}
        <div className="flex items-center gap-4 my-6">
          <div className="flex-1 h-px bg-white/10" />
          <span className="text-xs text-text-muted bg-transparent px-2 uppercase tracking-widest font-mono">or</span>
          <div className="flex-1 h-px bg-white/10" />
        </div>

        {/* Social buttons */}
        <div className="flex flex-col gap-3 mb-6">
          <Button
            type="button"
            variant="outline"
            className="w-full h-12 bg-white text-black hover:bg-gray-100 hover:text-black border-0 font-medium transition-transform active:scale-[0.98] shadow-lg flex items-center justify-center gap-3 text-base"
            onClick={() => handleGoogleLogin()}
          >
            <svg className="w-5 h-5" viewBox="0 0 24 24">
              <path
                fill="#4285F4"
                d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z"
              />
              <path
                fill="#34A853"
                d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z"
              />
              <path
                fill="#FBBC05"
                d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l2.85-2.22.81-.62z"
              />
              <path
                fill="#EA4335"
                d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z"
              />
            </svg>
            Continue with Google
          </Button>
        </div>

        {/* Back to Dashboard */}
        <div className="text-center">
          <button
            onClick={() => navigate('/')}
            className="text-sm text-text-muted/60 hover:text-white transition-all duration-300 hover-underline-animation inline-block"
          >
            Back to Dashboard
          </button>
        </div>
      </div>
    </div>
  );
}
