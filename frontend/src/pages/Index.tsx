import { Header } from '@/components/Header';
import { Footer } from '@/components/Footer';
import { LandingHero } from '@/components/LandingHero';
import { FeatureCard } from '@/components/FeatureCard';
import { MessageSquare, Image, Mic } from 'lucide-react';

const Index = () => {
  return (
    <div className="min-h-screen flex flex-col">
      <Header />
      
      <main className="flex-1">
        <LandingHero />
        
        {/* Features section */}
        <section className="py-20 border-t border-border">
          <div className="container">
            <div className="text-center mb-12">
              <h2 className="text-2xl font-semibold text-foreground mb-3">
                Built for simplicity
              </h2>
              <p className="text-muted-foreground max-w-md mx-auto">
                Everything you need, nothing you don't.
              </p>
            </div>
            
            <div className="grid md:grid-cols-3 gap-6 max-w-4xl mx-auto">
              <FeatureCard
                icon={<MessageSquare className="w-5 h-5" />}
                title="Natural Chat"
                description="Conversational AI that understands context and provides thoughtful responses."
              />
              <FeatureCard
                icon={<Image className="w-5 h-5" />}
                title="Image Upload"
                description="Share images for visual context. Drag & drop or click to upload."
              />
              <FeatureCard
                icon={<Mic className="w-5 h-5" />}
                title="Voice Input"
                description="Speak naturally. Text-to-speech brings responses to life."
              />
            </div>
          </div>
        </section>
      </main>
      
      <Footer />
    </div>
  );
};

export default Index;
