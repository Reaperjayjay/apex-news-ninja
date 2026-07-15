import { AnimatedBackground } from "@/components/AnimatedBackground";
import { Logo } from "@/components/Logo";
import { Button } from "@/components/ui/button";
import { motion } from "framer-motion";
import { useNavigate } from "react-router-dom";
import { useRef, useState, useEffect } from "react";
import {
  Code,
  Briefcase,
  Trophy,
  Brain,
  Globe,
  Landmark,
  Heart,
  Music,
  Bitcoin,
  TrendingUp,
  Check,
  ChevronLeft,
  ChevronRight
} from "lucide-react";
import { useNiche } from "@/context/NicheContext";
import { toast } from "sonner";

const niches = [
  { id: 'Tech', name: 'Tech', icon: Code, color: 'from-cyan-500 to-blue-600' },
  { id: 'Business', name: 'Business', icon: Briefcase, color: 'from-blue-500 to-indigo-600' },
  { id: 'Sports', name: 'Sports', icon: Trophy, color: 'from-green-500 to-emerald-600' },
  { id: 'AI', name: 'AI', icon: Brain, color: 'from-purple-500 to-pink-600' },
  { id: 'World News', name: 'World News', icon: Globe, color: 'from-teal-500 to-cyan-600' },
  { id: 'Politics', name: 'Politics', icon: Landmark, color: 'from-orange-500 to-red-600' },
  { id: 'Health', name: 'Health', icon: Heart, color: 'from-red-500 to-rose-600' },
  { id: 'Entertainment', name: 'Entertainment', icon: Music, color: 'from-indigo-500 to-purple-600' },
  { id: 'Crypto', name: 'Crypto', icon: Bitcoin, color: 'from-yellow-500 to-orange-600' },
  { id: 'Forex', name: 'Forex', icon: TrendingUp, color: 'from-emerald-500 to-teal-600' }
];

const NicheSelect = () => {
  const navigate = useNavigate();
  const { selectedNiches, toggleNiche } = useNiche();
  const scrollContainerRef = useRef<HTMLDivElement>(null);
  const [canScrollLeft, setCanScrollLeft] = useState(false);
  const [canScrollRight, setCanScrollRight] = useState(true);

  const checkScroll = () => {
    const container = scrollContainerRef.current;
    if (container) {
      setCanScrollLeft(container.scrollLeft > 0);
      setCanScrollRight(
        container.scrollLeft < container.scrollWidth - container.clientWidth - 10
      );
    }
  };

  useEffect(() => {
    const container = scrollContainerRef.current;
    if (container) {
      checkScroll();
      container.addEventListener('scroll', checkScroll);
      window.addEventListener('resize', checkScroll);
      return () => {
        container.removeEventListener('scroll', checkScroll);
        window.removeEventListener('resize', checkScroll);
      };
    }
  }, []);

  const scroll = (direction: 'left' | 'right') => {
    const container = scrollContainerRef.current;
    if (container) {
      const scrollAmount = 300;
      container.scrollBy({
        left: direction === 'left' ? -scrollAmount : scrollAmount,
        behavior: 'smooth'
      });
    }
  };

  const handleContinue = () => {
    if (selectedNiches.length === 0) {
      toast.error("Please select at least one category");
      return;
    }
    toast.success(`${selectedNiches.length} categories selected!`);
    navigate('/dashboard');
  };

  return (
    <div className="min-h-screen">
      <AnimatedBackground />

      <div className="relative z-10 min-h-screen flex flex-col px-6 py-12">
        <div className="mb-12 flex justify-center">
          <Logo variant="full" />
        </div>

        <motion.div
          initial={{ opacity: 0, y: 30 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6 }}
          className="flex-1 flex flex-col items-center justify-center max-w-7xl mx-auto w-full"
        >
          <div className="text-center mb-12">
            <h1 className="text-4xl md:text-5xl font-black mb-4 gradient-text">
              Choose Your News Categories
            </h1>
            <p className="text-xl text-muted-foreground max-w-2xl mx-auto">
              Select the topics that matter to you. We'll curate personalized news from these domains.
            </p>
          </div>

          <div className="w-full mb-12 relative group">
            <motion.button
              onClick={() => scroll('left')}
              disabled={!canScrollLeft}
              whileHover={{ scale: 1.1 }}
              whileTap={{ scale: 0.95 }}
              className={`absolute left-0 top-1/2 -translate-y-1/2 z-20 p-3 rounded-full backdrop-blur-xl transition-all duration-300 ${
                canScrollLeft
                  ? 'bg-white/20 hover:bg-white/40 cursor-pointer'
                  : 'bg-white/5 opacity-40 cursor-not-allowed'
              }`}
              style={{
                boxShadow: canScrollLeft ? '0 4px 15px hsl(var(--primary) / 0.2)' : 'none'
              }}
            >
              <ChevronLeft className="w-6 h-6 text-primary" />
            </motion.button>

            <motion.button
              onClick={() => scroll('right')}
              disabled={!canScrollRight}
              whileHover={{ scale: 1.1 }}
              whileTap={{ scale: 0.95 }}
              className={`absolute right-0 top-1/2 -translate-y-1/2 z-20 p-3 rounded-full backdrop-blur-xl transition-all duration-300 ${
                canScrollRight
                  ? 'bg-white/20 hover:bg-white/40 cursor-pointer'
                  : 'bg-white/5 opacity-40 cursor-not-allowed'
              }`}
              style={{
                boxShadow: canScrollRight ? '0 4px 15px hsl(var(--primary) / 0.2)' : 'none'
              }}
            >
              <ChevronRight className="w-6 h-6 text-primary" />
            </motion.button>

            <div className="overflow-hidden px-16">
              <div
                ref={scrollContainerRef}
                className="overflow-x-auto flex gap-4 snap-x snap-mandatory pb-4 scrollbar-hidden"
                onScroll={checkScroll}
              >
                {niches.map((niche, index) => {
                const isSelected = selectedNiches.includes(niche.id);

                return (
                  <motion.button
                    key={niche.id}
                    initial={{ opacity: 0, x: -30 }}
                    animate={{ opacity: 1, x: 0 }}
                    transition={{ delay: index * 0.05, duration: 0.4 }}
                    onClick={() => toggleNiche(niche.id)}
                    className={`
                      flex-shrink-0 w-64 h-28 rounded-xl p-4 snap-start
                      transition-all duration-300 cursor-pointer
                      ${isSelected
                        ? 'bg-white/12 ring-2 ring-primary/60 border border-primary/40'
                        : 'bg-white/6 border border-gray-300/20 hover:bg-white/10 hover:scale-105'
                      }
                    `}
                    style={{
                      boxShadow: isSelected ? '0 4px 20px hsl(var(--primary) / 0.3)' : 'none'
                    }}
                    tabIndex={0}
                    aria-pressed={isSelected}
                    onKeyDown={(e) => {
                      if (e.key === 'Enter' || e.key === ' ') {
                        e.preventDefault();
                        toggleNiche(niche.id);
                      }
                    }}
                  >
                    <div className="flex items-center justify-between h-full">
                      <div className="flex items-center gap-4">
                        <div
                          className={`w-14 h-14 rounded-lg bg-gradient-to-br ${niche.color} flex items-center justify-center flex-shrink-0`}
                        >
                          <niche.icon className="w-7 h-7 text-white" />
                        </div>
                        <h3 className="text-lg font-bold text-left">{niche.name}</h3>
                      </div>

                      {isSelected && (
                        <motion.div
                          initial={{ scale: 0 }}
                          animate={{ scale: 1 }}
                          className="w-8 h-8 rounded-full bg-primary flex items-center justify-center flex-shrink-0"
                        >
                          <Check className="w-5 h-5 text-black" />
                        </motion.div>
                      )}
                    </div>
                  </motion.button>
                );
              })}
              </div>
            </div>
          </div>

          <div className="text-center space-y-6">
            <p className="text-sm text-muted-foreground">
              {selectedNiches.length} {selectedNiches.length === 1 ? 'category' : 'categories'} selected
            </p>

            <Button
              onClick={handleContinue}
              size="lg"
              className="bg-gradient-to-br from-primary to-secondary text-black font-bold text-lg px-12 hover:shadow-xl hover:shadow-primary/50 transition-all"
              disabled={selectedNiches.length === 0}
            >
              Continue to Dashboard
            </Button>
          </div>
        </motion.div>
      </div>

      <style>{`
        .scrollbar-hidden::-webkit-scrollbar {
          display: none;
        }
        .scrollbar-hidden {
          -ms-overflow-style: none;
          scrollbar-width: none;
        }
      `}</style>
    </div>
  );
};

export default NicheSelect;
