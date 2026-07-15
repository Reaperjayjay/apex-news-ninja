import { AnimatedBackground } from "@/components/AnimatedBackground";
import { Logo } from "@/components/Logo";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { motion, AnimatePresence } from "framer-motion";
import { useNavigate } from "react-router-dom";
import {
  Newspaper,
  TrendingUp,
  Clock,
  Settings as SettingsIcon,
  User,
  Bell,
  Search,
  Menu,
  LogOut,
  Briefcase,
  Brain,
  Bitcoin,
  TrendingDown,
  Code,
  GraduationCap,
  Music,
  RefreshCw,
  AlertCircle
} from "lucide-react";
import { useState, useEffect } from "react";
import { useAuth } from "@/context/AuthContext";
import { NewsCard } from "@/components/NewsCard";
import { API_BASE_URL } from "@/lib/api";

interface Article {
  _id: string;
  title: string;
  description: string | null;
  content: string | null;
  url: string;
  image_url: string | null;
  source: string;
  author: string | null;
  category: string;
  published_at: string;
  fetched_at: string;
  view_count: number;
  click_count: number;
  ai_processed?: boolean;
  sentiment?: 'Bullish' | 'Bearish' | 'Neutral';
  summary?: string;
  key_points?: string[];
}

const Dashboard = () => {
  const navigate = useNavigate();
  const { logout } = useAuth();
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const [articles, setArticles] = useState<Article[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [page, setPage] = useState(1);
  const [totalArticles, setTotalArticles] = useState(0);
  const [searchQuery, setSearchQuery] = useState("");

  useEffect(() => {
    fetchNews();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [page]);

  const fetchNews = async () => {
    try {
      setLoading(true);
      setError(null);

      const token = localStorage.getItem('token');

      if (!token) {
        setError('Session expired. Please refresh.');
        // navigate('/auth'); // Optional: Auto-redirect
      }

      // Construct URL with search query if present
      let url = `${API_BASE_URL}/api/v1/news/feed?page=${page}&page_size=20`;
      if (searchQuery) {
        url += `&keywords=${encodeURIComponent(searchQuery)}`;
      }

      const response = await fetch(url, {
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        }
      });

      const data = await response.json();

      if (response.ok && data.status === 'success') {
        // If it's page 1 (new search or refresh), replace articles. Else append for pagination.
        if (page === 1) {
          setArticles(data.data.items || data.data.articles || []);
        } else {
          setArticles(prev => [...prev, ...(data.data.items || data.data.articles || [])]);
        }
        setTotalArticles(data.data.total || 0);
      } else {
        // If 401 Unauthorized, log out
        if (response.status === 401) {
          logout();
          navigate('/auth');
          return;
        }
        setError(data.message || 'Failed to load news');
      }
    } catch (err) {
      console.error('Error fetching news:', err);
      setError('Failed to connect to backend. Please check your internet connection.');
    } finally {
      setLoading(false);
    }
  };

  // Search Handlers
  const handleSearch = () => {
    setArticles([]); // Clear old results
    if (page === 1) {
      fetchNews(); // Force fetch if already on page 1
    } else {
      setPage(1); // Changing page triggers useEffect which calls fetchNews
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter') {
      e.preventDefault(); // <--- Added to stop page refresh
      handleSearch();
    }
  };

  const menuItems = [
    { id: 'dashboard', label: 'Dashboard', icon: Newspaper, path: '/dashboard' },
    { id: 'business', label: 'Business', icon: Briefcase, path: '/news/business' },
    { id: 'ai', label: 'AI', icon: Brain, path: '/news/ai' },
    { id: 'crypto', label: 'Crypto', icon: Bitcoin, path: '/news/crypto' },
    { id: 'forex', label: 'Forex', icon: TrendingDown, path: '/news/forex' },
    { id: 'tech', label: 'Tech', icon: Code, path: '/news/tech' },
    { id: 'education', label: 'Education', icon: GraduationCap, path: '/news/education' },
    { id: 'entertainment', label: 'Entertainment', icon: Music, path: '/news/entertainment' },
    { id: 'profile', label: 'Profile', icon: User, path: '/profile' },
    { id: 'settings', label: 'Settings', icon: SettingsIcon, path: '/settings' }
  ];

  const handleMenuClick = (path: string) => {
    navigate(path);
    setSidebarOpen(false);
  };

  const handleLogout = () => {
    logout();
    localStorage.removeItem('token');
    navigate('/auth');
  };

  useEffect(() => {
    const handleEscape = (e: KeyboardEvent) => {
      if (e.key === 'Escape' && sidebarOpen) {
        setSidebarOpen(false);
      }
    };
    window.addEventListener('keydown', handleEscape);
    return () => window.removeEventListener('keydown', handleEscape);
  }, [sidebarOpen]);

  // Loading State
  if (loading && articles.length === 0) {
    return (
      <div className="min-h-screen relative">
        <AnimatedBackground />
        <div className="relative z-[2] min-h-screen flex items-center justify-center">
          <div className="text-center">
            <RefreshCw className="w-16 h-16 text-primary animate-spin mx-auto mb-4" />
            <h2 className="text-2xl font-bold mb-2">Loading Your News Feed...</h2>
            <p className="text-muted-foreground">Fetching latest AI insights</p>
          </div>
        </div>
      </div>
    );
  }

  // Error State
  if (error && articles.length === 0) {
    return (
      <div className="min-h-screen relative">
        <AnimatedBackground />
        <div className="relative z-[2] min-h-screen flex items-center justify-center p-6">
          <Card className="max-w-md w-full glass border-destructive/50">
            <CardHeader>
              <div className="flex items-center gap-3 mb-2">
                <AlertCircle className="w-8 h-8 text-destructive" />
                <CardTitle className="text-destructive">Connection Error</CardTitle>
              </div>
              <CardDescription className="text-base">{error}</CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="flex gap-2">
                <Button onClick={fetchNews} className="flex-1">
                  <RefreshCw className="w-4 h-4 mr-2" />
                  Retry
                </Button>
                <Button onClick={() => navigate('/auth')} variant="outline" className="flex-1">
                  Login Again
                </Button>
              </div>
            </CardContent>
          </Card>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen relative">
      <AnimatedBackground />

      <AnimatePresence>
        {sidebarOpen && (
          <>
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
              transition={{ duration: 0.3 }}
              onClick={() => setSidebarOpen(false)}
              className="fixed inset-0 bg-black/40 z-30"
            />

            <motion.aside
              initial={{ x: '-100%' }}
              animate={{ x: '0%' }}
              exit={{ x: '-100%' }}
              transition={{ type: 'spring', stiffness: 300, damping: 30 }}
              className="fixed inset-y-0 left-0 w-72 bg-white/6 backdrop-blur-xl border-r border-white/10 z-40 p-4 space-y-4 overflow-y-auto"
            >
              <div className="mb-6">
                <Logo variant="full" />
              </div>

              <nav className="space-y-2">
                {menuItems.map((item) => (
                  <button
                    key={item.id}
                    onClick={() => handleMenuClick(item.path)}
                    className="w-full flex items-center gap-3 px-4 py-3 rounded-md hover:bg-white/10 transition-all text-left group"
                  >
                    <item.icon className="w-5 h-5 text-primary group-hover:scale-110 transition-transform" />
                    <span className="font-medium">{item.label}</span>
                  </button>
                ))}

                <button
                  onClick={handleLogout}
                  className="w-full flex items-center gap-3 px-4 py-3 rounded-md hover:bg-destructive/10 hover:text-destructive transition-all text-left group"
                >
                  <LogOut className="w-5 h-5 group-hover:scale-110 transition-transform" />
                  <span className="font-medium">Logout</span>
                </button>
              </nav>
            </motion.aside>
          </>
        )}
      </AnimatePresence>

      <div className="relative z-[2] min-h-screen">
        <header className="sticky top-0 z-20 bg-card/95 backdrop-blur-xl border-b border-primary/20 px-6 py-4">
          <div className="flex items-center justify-between max-w-7xl mx-auto">
            <div className="flex items-center gap-4">
              <motion.button
                onClick={() => setSidebarOpen(true)}
                className="p-2 rounded-md ring-2 ring-cyan-400/40 hover:ring-cyan-400/60 hover:scale-105 transition-all"
                whileHover={{ scale: 1.05 }}
                whileTap={{ scale: 0.95 }}
                style={{
                  boxShadow: '0 0 20px rgba(0, 191, 255, 0.3), 0 0 40px rgba(0, 191, 255, 0.1)',
                  animation: 'pulse 3s cubic-bezier(0.4, 0, 0.6, 1) infinite'
                }}
              >
                <Menu className="w-6 h-6 text-primary" />
              </motion.button>
              <Logo variant="compact" />
            </div>

            <div className="flex items-center gap-2">
              <Button
                onClick={fetchNews}
                variant="ghost"
                size="sm"
                className="mr-2"
                disabled={loading}
              >
                <RefreshCw className={`w-4 h-4 ${loading ? 'animate-spin' : ''}`} />
              </Button>
              <Button
                className="bg-gradient-to-br from-primary to-primary/80 text-background font-bold hover:shadow-lg hover:shadow-primary/50 transition-all"
                style={{ boxShadow: '0 4px 20px hsl(var(--primary) / 0.3)' }}
              >
                <Bell className="w-5 h-5 sm:mr-2" />
                <span className="hidden sm:inline">Notifications</span>
              </Button>
            </div>
          </div>
        </header>

        <main className="p-6 max-w-7xl mx-auto">
          <motion.div
            initial={{ opacity: 0, y: -20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.4 }}
            className="mb-8"
          >
            <h1 className="text-3xl lg:text-4xl font-black gradient-text mb-2">
              Your News Feed
            </h1>
            <p className="text-muted-foreground">
              {totalArticles} articles analyzed by AI
            </p>
          </motion.div>

          {/* Search Bar Area */}
          <div className="relative mb-8 group">
            <button
              onClick={handleSearch}
              className="absolute left-2 top-1/2 -translate-y-1/2 p-2 rounded-xl hover:bg-primary/10 text-muted-foreground hover:text-primary transition-all z-10"
              title="Search"
            >
              <Search className="w-5 h-5" />
            </button>
            <input
              type="text"
              placeholder="Search news (e.g. 'Bitcoin', 'AI')..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              onKeyDown={handleKeyDown}
              className="w-full h-14 pl-14 pr-6 bg-card/80 backdrop-blur-xl rounded-xl border border-primary/20 focus:border-primary focus:outline-none focus:ring-2 focus:ring-primary/20 transition-all text-foreground placeholder:text-muted-foreground"
              style={{ boxShadow: '0 2px 15px hsl(var(--primary) / 0.08)' }}
            />
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6 mb-8">
            {[
              { label: "Articles Today", value: totalArticles.toString(), icon: Newspaper, change: `${articles.length} loaded` },
              { label: "AI Analysis", value: "Active", icon: Brain, change: "sentiment enabled" },
              { label: "Updated", value: loading ? "..." : "Now", icon: Clock, change: "live" }
            ].map((stat, index) => (
              <motion.div
                key={stat.label}
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: index * 0.1, duration: 0.4 }}
                whileHover={{ y: -4, transition: { duration: 0.2 } }}
              >
                <div
                  className="bg-card/80 backdrop-blur-xl rounded-2xl p-6 border border-primary/15 transition-all hover:border-primary/40 hover:shadow-lg"
                  style={{ boxShadow: '0 2px 15px hsl(var(--primary) / 0.08)' }}
                >
                  <div className="flex items-start justify-between">
                    <div className="flex-1">
                      <p className="text-xs text-muted-foreground mb-1 font-medium">
                        {stat.label}
                      </p>
                      <p className="text-3xl font-black text-foreground">
                        {stat.value}
                      </p>
                      <p className="text-xs text-primary mt-1 font-semibold">
                        {stat.change}
                      </p>
                    </div>
                    <div
                      className="w-12 h-12 bg-primary/10 rounded-xl flex items-center justify-center"
                      style={{ boxShadow: '0 2px 12px hsl(var(--primary) / 0.15)' }}
                    >
                      <stat.icon className="w-6 h-6 text-primary" />
                    </div>
                  </div>
                </div>
              </motion.div>
            ))}
          </div>

          <div className="mb-6">
            <h2 className="text-2xl font-bold flex items-center gap-2">
              <TrendingUp className="w-6 h-6 text-primary" />
              <span className="gradient-text">Latest Updates</span>
            </h2>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {articles.map((article, index) => (
              <motion.div
                key={article._id}
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: index * 0.05, duration: 0.4 }}
                whileHover={{ y: -2, transition: { duration: 0.2 } }}
                className="h-full"
              >
                <NewsCard article={article} />
              </motion.div>
            ))}
          </div>

          <div className="text-center mt-12">
            <Button
              onClick={() => setPage(p => p + 1)}
              variant="outline"
              className="border-primary/20 hover:bg-primary/10 hover:border-primary/40 px-8"
              disabled={loading}
            >
              {loading ? 'Loading...' : 'Load More Articles'}
            </Button>
          </div>
        </main>
      </div>

      <style>{`
        @keyframes pulse {
          0%, 100% { opacity: 1; }
          50% { opacity: 0.7; }
        }
      `}</style>
    </div>
  );
};

export default Dashboard;