import { useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { Header } from '@/components/Header';
import { AuthForm } from '@/components/AuthForm';
import { useSessionStore } from '@/stores/sessionStore';
import AgenticBg from '@/assets/agentic.png';

const Auth = () => {
  const navigate = useNavigate();
  const { isAuthenticated } = useSessionStore();

  useEffect(() => {
    if (isAuthenticated) {
      navigate('/chat');
    }
  }, [isAuthenticated, navigate]);

  return (
    <div className="min-h-screen flex flex-col bg-ink-black relative overflow-hidden">
      <div className="absolute inset-0 z-0">
        <img
          src={AgenticBg}
          alt="Background"
          className="w-full h-full object-cover opacity-60 scale-100"
        />
        <div className="absolute inset-0 bg-ink-black/80 backdrop-blur-[1px]"></div>
      </div>

      <div className="relative z-10 flex-1 flex flex-col">
        <Header />

        <main className="flex-1 flex items-center justify-center p-6 pt-32 md:pt-40">
          <AuthForm />
        </main>
      </div>
    </div>
  );
};

export default Auth;
