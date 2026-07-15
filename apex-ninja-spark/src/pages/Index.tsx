import { AnimatedBackground } from "@/components/AnimatedBackground";
import { Logo } from "@/components/Logo";
import { GlassCard } from "@/components/GlassCard";
import { Button } from "@/components/ui/button";
import { motion } from "framer-motion";
import { useNavigate } from "react-router-dom";
import { 
  Zap, 
  Brain, 
  MessageSquare, 
  Target, 
  TrendingUp, 
  Shield,
  Sparkles,
  ArrowRight
} from "lucide-react";
import { useEffect, useState } from "react";

const Index = () => {
  const navigate = useNavigate();
  const [scrolled, setScrolled] = useState(false);

  useEffect(() => {
    const handleScroll = () => {
      setScrolled(window.scrollY > 50);
    };
    window.addEventListener('scroll', handleScroll);
    return () => window.removeEventListener('scroll', handleScroll);
  }, []);

  const features = [
    {
      icon: Brain,
      title: "AI-Powered Summaries",
      description: "Get concise, intelligent news summaries tailored to your interests"
    },
    {
      icon: MessageSquare,
      title: "WhatsApp Delivery",
      description: "Receive your daily digest directly on WhatsApp"
    },
    {
      icon: Target,
      title: "Multi-Domain Coverage",
      description: "Stay informed across technology, business, sports, and more"
    },
    {
      icon: Sparkles,
      title: "Personalized Content",
      description: "AI learns your preferences to deliver relevant news"
    },
    {
      icon: TrendingUp,
      title: "Real-Time Updates",
      description: "Breaking news delivered as it happens"
    },
    {
      icon: Shield,
      title: "Trusted Sources",
      description: "Curated from verified, reputable news outlets"
    }
  ];

  return (
    <div className="min-h-screen">
      <AnimatedBackground />
      
      {/* Header */}
      <motion.header
        initial={{ y: -100 }}
        animate={{ y: 0 }}
        className={`fixed top-0 w-full z-[1000] transition-all duration-300 ${
          scrolled 
            ? 'py-2 sm:py-3 bg-card/95 backdrop-blur-xl shadow-lg' 
            : 'py-3 sm:py-5 bg-card/80 backdrop-blur-xl'
        } border-b border-primary/20`}
      >
        <nav className="max-w-7xl mx-auto px-4 sm:px-6 flex justify-between items-center">
          <Logo variant="full" />
          <div className="flex items-center gap-3 sm:gap-6 lg:gap-8">
            <a href="#features" className="hidden sm:inline text-sm text-muted-foreground hover:text-primary transition-colors font-medium">
              Features
            </a>
            <a href="#how-it-works" className="hidden sm:inline text-sm text-muted-foreground hover:text-primary transition-colors font-medium">
              How It Works
            </a>
            <Button
              onClick={() => navigate('/login')}
              className="bg-gradient-to-br from-primary to-primary/80 text-background font-bold hover:shadow-lg hover:shadow-primary/50 transition-all h-8 sm:h-9 text-xs sm:text-sm px-3 sm:px-4"
              style={{ boxShadow: '0 4px 20px hsl(var(--primary) / 0.3)' }}
            >
              Get Started
            </Button>
          </div>
        </nav>
      </motion.header>

      {/* Hero Section */}
      <section className="relative min-h-screen flex items-center justify-center px-6 pt-32 pb-20 z-10">
        <div className="max-w-6xl mx-auto text-center">
          <motion.div
            initial={{ opacity: 0, y: 40 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.45 }}
          >
            <GlassCard className="max-w-4xl mx-auto">
              <div className="inline-flex items-center gap-2 px-4 py-2 rounded-full glass mb-6">
                <Zap className="w-4 h-4 text-primary" />
                <span className="text-sm font-semibold text-primary">AI-Powered News Platform</span>
              </div>

              <h1 className="text-5xl md:text-6xl font-black mb-6 gradient-text leading-tight">
                Get Your Personalized WhatsApp News Aggregator Now
              </h1>

              <p className="text-xl text-muted-foreground mb-10 max-w-2xl mx-auto">
                AI-curated news summaries from multiple domains delivered directly to your WhatsApp.
                Stay informed without the information overload.
              </p>

              <Button
                size="lg"
                onClick={() => navigate('/login')}
                className="bg-gradient-to-br from-primary to-secondary text-black font-bold text-lg px-8 hover:shadow-xl hover:shadow-primary/50 transition-all group"
              >
                Try Apex News Ninja
                <ArrowRight className="ml-2 w-5 h-5 group-hover:translate-x-1 transition-transform" />
              </Button>
            </GlassCard>
          </motion.div>
        </div>
      </section>

      {/* Features Section */}
      <section id="features" className="relative py-32 px-6 z-10">
        <div className="max-w-7xl mx-auto">
          <motion.div
            initial={{ opacity: 0 }}
            whileInView={{ opacity: 1 }}
            viewport={{ once: true }}
            className="text-center mb-16"
          >
            <h2 className="text-5xl font-black mb-4 gradient-text">
              Powerful Features
            </h2>
            <p className="text-xl text-muted-foreground">
              Everything you need to stay informed, delivered intelligently
            </p>
          </motion.div>

          <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-8">
            {features.map((feature, index) => (
              <motion.div
                key={feature.title}
                initial={{ opacity: 0, y: 30 }}
                whileInView={{ opacity: 1, y: 0 }}
                viewport={{ once: true }}
                transition={{ delay: index * 0.1 }}
              >
                <GlassCard className="h-full">
                  <div 
                    className="w-14 h-14 rounded-xl flex items-center justify-center mb-4"
                    style={{
                      background: 'linear-gradient(135deg, hsl(var(--primary) / 0.2), hsl(var(--secondary) / 0.2))',
                      border: '2px solid hsl(var(--primary) / 0.3)'
                    }}
                  >
                    <feature.icon className="w-7 h-7 text-primary" />
                  </div>
                  <h3 className="text-xl font-bold mb-3">{feature.title}</h3>
                  <p className="text-muted-foreground">{feature.description}</p>
                </GlassCard>
              </motion.div>
            ))}
          </div>
        </div>
      </section>

      {/* How It Works Section */}
      <section id="how-it-works" className="relative py-32 px-6 z-10">
        <div className="max-w-5xl mx-auto">
          <motion.div
            initial={{ opacity: 0 }}
            whileInView={{ opacity: 1 }}
            viewport={{ once: true }}
            className="text-center mb-16"
          >
            <h2 className="text-5xl font-black mb-4 gradient-text">
              How It Works
            </h2>
            <p className="text-xl text-muted-foreground">
              Get started in 3 simple steps
            </p>
          </motion.div>

          <div className="space-y-8">
            {[
              {
                step: "01",
                title: "Sign Up & Choose Domains",
                description: "Create your account and select news categories that matter to you"
              },
              {
                step: "02",
                title: "Connect WhatsApp",
                description: "Link your WhatsApp number for seamless news delivery"
              },
              {
                step: "03",
                title: "Receive Daily Digests",
                description: "Get personalized AI-curated news summaries every day"
              }
            ].map((step, index) => (
              <motion.div
                key={step.step}
                initial={{ opacity: 0, x: -30 }}
                whileInView={{ opacity: 1, x: 0 }}
                viewport={{ once: true }}
                transition={{ delay: index * 0.2 }}
              >
                <GlassCard className="flex gap-6 items-start">
                  <div 
                    className="text-6xl font-black"
                    style={{
                      background: 'linear-gradient(135deg, hsl(var(--primary)), hsl(var(--accent)))',
                      WebkitBackgroundClip: 'text',
                      WebkitTextFillColor: 'transparent',
                      backgroundClip: 'text'
                    }}
                  >
                    {step.step}
                  </div>
                  <div className="flex-1">
                    <h3 className="text-2xl font-bold mb-2">{step.title}</h3>
                    <p className="text-muted-foreground text-lg">{step.description}</p>
                  </div>
                </GlassCard>
              </motion.div>
            ))}
          </div>

          <motion.div
            initial={{ opacity: 0, y: 30 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            className="text-center mt-16"
          >
            <Button
              size="lg"
              onClick={() => navigate('/login')}
              className="bg-gradient-to-br from-primary to-secondary text-black font-bold text-lg px-12 hover:shadow-xl hover:shadow-primary/50 transition-all"
            >
              Get Started Now
            </Button>
          </motion.div>
        </div>
      </section>

      {/* Footer */}
      <footer className="relative border-t border-primary/20 py-8 px-6 z-10">
        <div className="max-w-7xl mx-auto text-center text-muted-foreground">
          <p>&copy; 2025 Apex News Ninja. All rights reserved.</p>
        </div>
      </footer>
    </div>
  );
};

export default Index;
