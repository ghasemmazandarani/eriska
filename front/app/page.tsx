import Header from '@/components/Header';
import Hero from '@/components/Hero';
import HowItWorks from '@/components/HowItWorks';
import Features from '@/components/Features';
import DashboardPreview from '@/components/DashboardPreview';
import AISection from '@/components/AISection';
import UseCases from '@/components/UseCases';
import FAQ from '@/components/FAQ';
import CTA from '@/components/CTA';
import Footer from '@/components/Footer';

import NetworkBackground from '@/components/NetworkBackground';
import TerminalDemo from '@/components/TerminalDemo';
import ThreatMap from '@/components/ThreatMap';

export default function Home() {
  return (
    <div className="relative min-h-screen flex flex-col overflow-hidden bg-slate-950">
      {/* Background Effects */}
      <NetworkBackground />
      <div className="absolute top-0 right-0 w-[500px] h-[500px] bg-emerald-500/10 rounded-full blur-[100px] -translate-y-1/2 translate-x-1/4 pointer-events-none"></div>
      <div className="absolute bottom-0 left-0 w-[500px] h-[500px] bg-blue-500/10 rounded-full blur-[100px] translate-y-1/2 -translate-x-1/4 pointer-events-none"></div>
      <div className="scan-overlay pointer-events-none"></div>

      <Header />

      <main className="flex-grow">
        <Hero />
        <HowItWorks />
        <Features />
        <DashboardPreview />
        <ThreatMap />
        <AISection />
        <UseCases />
        <FAQ />
        <CTA />
      </main>

      <Footer />
    </div>
  );
}
