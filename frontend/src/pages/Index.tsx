import { Link } from "react-router-dom";
import DemoVideo from "@/assets/AI_Product_Explainer_Video_Generation.mp4";
import { Header } from "@/components/Header";

const Index = () => {
  return (
    <div className="bg-ink-black text-text-main font-sans antialiased selection:bg-primary/30 selection:text-white transition-colors duration-300 overflow-x-hidden min-h-screen">
      <Header />

      <main className="flex flex-col min-h-screen pt-32 pb-20 w-full relative">
        <section className="flex flex-col md:flex-row items-center justify-between min-h-[70vh] gap-12 md:gap-16 mb-24 px-6 md:px-12 max-w-[1440px] mx-auto w-full z-10">
          <div className="flex flex-col gap-8 relative md:w-1/2">
            <div className="absolute -left-6 top-2 bottom-2 w-[2px] bg-primary scale-y-0 animate-[scale-y_1s_ease-out_forwards]"></div>
            <h1 className="font-display text-5xl md:text-7xl lg:text-8xl font-black leading-[0.9] tracking-tighter text-balance uppercase text-white">
              <span className="block opacity-0 animate-[fadeIn_0.8s_ease-out_0.2s_forwards] translate-y-4">
                Search.
              </span>
              <span className="block opacity-0 animate-[fadeIn_0.8s_ease-out_0.3s_forwards] translate-y-4">
                Scrape.
              </span>
              <span className="block text-primary opacity-0 animate-[fadeIn_0.8s_ease-out_0.4s_forwards] translate-y-4">
                Curate.
              </span>
            </h1>
            <div className="mt-4 max-w-xl opacity-0 animate-[fadeIn_1s_ease-out_0.8s_forwards]">
              <p className="text-lg md:text-xl text-text-muted font-light leading-relaxed font-sans">
                ContextIQ is the autonomous intelligence layer for commerce. We
                transform intent into action by navigating the chaotic web to
                deliver verified, high-signal market insights.
              </p>
            </div>
            <div className="flex items-center opacity-0 animate-[fadeIn_1s_ease-out_1.2s_forwards] mt-4">
              <Link
                to="/chat"
                className="flex items-center gap-3 text-sm font-bold uppercase tracking-wider group text-white hover:text-primary transition-colors font-display"
              >
                <span className="w-2 h-2 bg-current rounded-full"></span>
                Start Agent
                <span className="material-symbols-outlined text-[18px] group-hover:translate-x-1 transition-transform">
                  east
                </span>
              </Link>
            </div>
          </div>
          <div className="md:w-1/2 relative w-full h-full flex justify-center md:justify-end opacity-0 animate-[fadeIn_1.5s_ease-out_0.5s_forwards]">
            <div className="relative w-full aspect-square max-w-[600px]">
              <div className="absolute inset-0 bg-gradient-radial from-white/5 to-transparent opacity-30 blur-2xl"></div>
              <div className="absolute inset-0 rounded-2xl overflow-hidden border border-border-subtle group">
                <img
                  alt="AI Neural Network Visualization"
                  className="w-full h-full object-cover opacity-80 mix-blend-screen scale-100 group-hover:scale-105 transition-transform duration-700"
                  src="https://lh3.googleusercontent.com/aida-public/AB6AXuD9gCIoyXQt7RfMUBd1VVDlqNCDn7CfrTOxz4KJoGtQ_f22w0NnYAFHzVOSvar3SEJldiPXL3B1ja6LbpftQSSS0htSiAZXeLa-5TGMnWiaMWZXxw_taEEauk_hyHEn2gRR2Z6rxSfwn5ftMhYp6Z6YHPRFMXS48vtLvJlhYWc1q6LnhmpKts61jK20M6AFdTxXjzt7-w7APpM3_LP0dyCrO7T25pJzIUk4YpyqAYuHNYXT_7NKrlD8p7eOdwuiBdAltGJI-li7gQk"
                />
                <div className="absolute inset-0 bg-gradient-to-t from-ink-black via-transparent to-ink-black/20"></div>
              </div>
              <div className="absolute bottom-8 left-8 right-8 md:-left-12 md:right-auto md:w-[380px] glass-panel rounded-xl p-6 animate-float z-20">
                <div className="flex items-center justify-between mb-4 border-b border-white/5 pb-3">
                  <div className="flex items-center gap-2">
                    <span className="w-2 h-2 bg-green-500 rounded-full shadow-[0_0_8px_rgba(34,197,94,0.6)]"></span>
                    <span className="text-xs font-mono text-white/60 tracking-wider">
                      NEURAL LATTICE
                    </span>
                  </div>
                  <span className="text-[10px] font-mono text-primary">
                    ACTIVE THREADS: 124
                  </span>
                </div>
                <div className="space-y-4">
                  <div className="flex gap-3">
                    <div className="w-6 h-6 rounded bg-white/10 flex items-center justify-center shrink-0">
                      <span className="material-symbols-outlined text-[14px] text-white">
                        hub
                      </span>
                    </div>
                    <div>
                      <p className="text-sm text-white font-medium">
                        Constructing decision model...
                      </p>
                      <p className="text-xs text-text-muted mt-1">
                        Ingesting unstructured data streams
                      </p>
                    </div>
                  </div>
                  <div className="h-[1px] bg-white/5 w-full my-2"></div>
                  <div className="flex gap-2 items-center">
                    <span className="material-symbols-outlined text-[14px] text-primary">
                      check_circle
                    </span>
                    <span className="text-xs text-white/80">
                      Indexing global signal patterns
                    </span>
                  </div>
                  <div className="flex gap-2 items-center">
                    <span className="material-symbols-outlined text-[14px] text-primary">
                      check_circle
                    </span>
                    <span className="text-xs text-white/80">
                      Verifying source integrity (99.9%)
                    </span>
                  </div>
                  <div className="mt-2 p-3 bg-white/5 rounded border border-white/5 flex flex-col gap-2">
                    <div className="flex justify-between items-center text-[10px] font-mono uppercase text-text-muted">
                      <span>Confidence Score</span>
                      <span>High</span>
                    </div>
                    <div className="w-full h-1 bg-white/10 rounded-full overflow-hidden">
                      <div className="h-full w-[94%] bg-primary rounded-full"></div>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </section>

        <div className="relative w-full border-t border-border-subtle bg-charcoal/30">
          <div className="absolute inset-0 bg-grid-pattern pointer-events-none z-0 opacity-40"></div>
          <div className="relative z-10 px-6 md:px-12 max-w-[1440px] mx-auto w-full pt-20">
            <section className="grid grid-cols-1 md:grid-cols-12 gap-12 mb-32">
              <div className="md:col-span-4">
                <h3 className="text-2xl font-bold tracking-tight mb-4 font-display text-white">
                  Live Signals
                </h3>
                <p className="text-sm text-text-muted max-w-xs leading-relaxed">
                  Our agent parses thousands of data points to deliver a
                  verified, curated list of products tailored to your exact
                  needs.
                </p>
              </div>
              <div className="md:col-span-8 flex flex-col">
                <div className="group flex items-baseline justify-between border-t border-border-subtle py-6 md:py-8 transition-colors hover:bg-white/[0.02] px-4 -mx-4 rounded-lg">
                  <div className="flex items-baseline gap-8 md:gap-16">
                    <span className="text-xs font-mono text-primary/70">
                      01
                    </span>
                    <span className="text-xl md:text-3xl font-medium tracking-tight font-display group-hover:translate-x-2 transition-transform duration-300">
                      Semantic Understanding
                    </span>
                  </div>
                  <span className="material-symbols-outlined opacity-0 group-hover:opacity-100 transition-opacity text-primary">
                    psychology
                  </span>
                </div>
                <div className="group flex items-baseline justify-between border-t border-border-subtle py-6 md:py-8 transition-colors hover:bg-white/[0.02] px-4 -mx-4 rounded-lg">
                  <div className="flex items-baseline gap-8 md:gap-16">
                    <span className="text-xs font-mono text-primary/70">
                      02
                    </span>
                    <span className="text-xl md:text-3xl font-medium tracking-tight font-display group-hover:translate-x-2 transition-transform duration-300">
                      Cross-Site Scraping
                    </span>
                  </div>
                  <span className="material-symbols-outlined opacity-0 group-hover:opacity-100 transition-opacity text-primary">
                    public
                  </span>
                </div>
                <div className="group flex items-baseline justify-between border-t border-border-subtle py-6 md:py-8 transition-colors hover:bg-white/[0.02] px-4 -mx-4 rounded-lg">
                  <div className="flex items-baseline gap-8 md:gap-16">
                    <span className="text-xs font-mono text-primary/70">
                      03
                    </span>
                    <span className="text-xl md:text-3xl font-medium tracking-tight font-display group-hover:translate-x-2 transition-transform duration-300">
                      Sentiment Analysis
                    </span>
                  </div>
                  <span className="material-symbols-outlined opacity-0 group-hover:opacity-100 transition-opacity text-primary">
                    thumbs_up_down
                  </span>
                </div>
                <div className="group flex items-baseline justify-between border-t border-b border-border-subtle py-6 md:py-8 transition-colors hover:bg-white/[0.02] px-4 -mx-4 rounded-lg">
                  <div className="flex items-baseline gap-8 md:gap-16">
                    <span className="text-xs font-mono text-primary/70">
                      04
                    </span>
                    <span className="text-xl md:text-3xl font-medium tracking-tight font-display group-hover:translate-x-2 transition-transform duration-300">
                      Link Verification
                    </span>
                  </div>
                  <span className="material-symbols-outlined opacity-0 group-hover:opacity-100 transition-opacity text-primary">
                    link
                  </span>
                </div>
              </div>
            </section>
            <section className="py-10 md:py-16 flex flex-col items-center text-center">
              <div className="max-w-4xl relative mb-8">
                <span className="material-symbols-outlined absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 text-[200px] md:text-[300px] opacity-[0.02] select-none pointer-events-none text-white">
                  smart_toy
                </span>
                <h2 className="font-display text-4xl md:text-5xl font-semibold leading-tight tracking-tight text-balance text-white">
                  Designed to find answers — <br className="hidden md:block" />
                  <span className="text-text-muted">not just list links.</span>
                </h2>
              </div>

              <div className="w-full max-w-[1000px] aspect-video md:aspect-[21/9] bg-charcoal rounded-lg overflow-hidden relative mb-8 group border border-border-subtle shadow-2xl">
                <video
                  className="w-full h-full object-cover transition-transform duration-700 group-hover:scale-105"
                  src={DemoVideo}
                  autoPlay
                  loop
                  muted
                  playsInline
                />
              </div>

              <div className="flex justify-center">
                <Link
                  to="/auth"
                  className="inline-flex items-center justify-center px-8 py-4 border border-primary/30 rounded-full text-white hover:bg-primary/10 hover:border-primary transition-all duration-300 bg-charcoal/50 backdrop-blur-sm text-sm font-bold tracking-widest uppercase font-display group relative overflow-hidden"
                >
                  <span className="relative z-10 flex items-center gap-2">
                    Try Now <span className="material-symbols-outlined text-[18px] group-hover:translate-x-1 transition-transform">arrow_forward</span>
                  </span>
                  <div className="absolute inset-0 bg-primary/10 translate-y-[100%] group-hover:translate-y-0 transition-transform duration-300"></div>
                </Link>
              </div>
            </section>

            <section className="w-full relative mb-20 rounded-2xl overflow-hidden bg-white/5 border border-white/10 group backdrop-blur-sm">
              <div className="absolute inset-0 bg-grid-pattern opacity-30 pointer-events-none"></div>
              <div className="absolute inset-0 bg-gradient-radial from-primary/10 to-transparent opacity-0 group-hover:opacity-20 transition-opacity duration-700"></div>

              <div className="relative z-10 p-8 md:p-12 flex flex-col md:flex-row items-center justify-between gap-12">
                <div className="flex-1 space-y-6">
                  <div className="flex items-center gap-3 text-primary/80">
                    <span className="material-symbols-outlined text-[20px]">security</span>
                    <span className="text-xs font-mono uppercase tracking-widest font-semibold text-white/70">Data Protocol</span>
                  </div>

                  <h3 className="text-3xl md:text-5xl font-bold font-display text-white leading-tight">
                    Your Secrets Are Safe.
                  </h3>

                  <p className="text-text-muted text-base md:text-lg leading-relaxed max-w-xl">
                    We prioritize your privacy. All processing happens locally or via encrypted channels.
                    We do not sell, share, or monetize your search intent data.
                  </p>

                  <div className="flex flex-wrap gap-6 pt-4">
                    <div className="flex items-center gap-2 text-sm text-white/80">
                      <span className="material-symbols-outlined text-primary text-[18px]">lock</span>
                      <span>256-bit Encryption</span>
                    </div>
                    <div className="flex items-center gap-2 text-sm text-white/80">
                      <span className="material-symbols-outlined text-primary text-[18px]">database</span>
                      <span>No Data Selling</span>
                    </div>
                  </div>
                </div>

                <div className="relative shrink-0">
                  <div className="w-48 h-48 md:w-64 md:h-64 rounded-full border border-white/5 flex items-center justify-center relative">
                    <div className="absolute inset-0 rounded-full border border-primary/20 animate-[spin_10s_linear_infinite]"></div>
                    <div className="absolute inset-4 rounded-full border border-white/5 animate-[spin_15s_linear_infinite_reverse]"></div>
                    <span className="material-symbols-outlined text-6xl md:text-8xl text-primary animate-pulse">shield</span>
                  </div>
                </div>
              </div>
            </section>
          </div>
        </div>
      </main>

      <footer className="w-full border-t border-border-subtle py-8 md:py-12 bg-charcoal relative z-20">
        <div className="max-w-[1440px] mx-auto px-6 md:px-12 flex flex-col md:flex-row justify-between items-start md:items-center gap-6 text-xs md:text-sm text-text-muted font-sans">
          <div className="flex items-center gap-2">
            <span className="material-symbols-outlined text-[16px]">
              copyright
            </span>
            <span className="font-medium text-white">
              ContextIQ Systems Inc.
            </span>
          </div>

          <div className="flex items-center gap-2 opacity-50">
            <span className="w-2 h-2 rounded-full bg-green-500 animate-pulse"></span>
            <span>System Operational</span>
          </div>
        </div>
      </footer>
    </div>
  );
};

export default Index;
