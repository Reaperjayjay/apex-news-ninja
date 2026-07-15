import { AnimatedBackground } from "@/components/AnimatedBackground";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { motion } from "framer-motion";
import { useNavigate, useParams } from "react-router-dom";
import {
  ArrowLeft,
  Clock,
  ChevronRight,
  RefreshCw,
  AlertCircle,
  Newspaper
} from "lucide-react";
import { useState, useEffect } from "react";

// Define the Article Interface
interface Article {
  id: string;
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
}

const NewsCategory = () => {
  const { category } = useParams();
  const navigate = useNavigate();

  const [articles, setArticles] = useState<Article[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [page, setPage] = useState(1);
  const [totalArticles, setTotalArticles] = useState(0);

  // Capitalize category for display
  const displayCategory = category ? category.charAt(0).toUpperCase() + category.slice(1) : "News";

  useEffect(() => {
    setArticles([]);
    setPage(1);
    fetchCategoryNews(1);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [category]);

  const fetchCategoryNews = async (pageNumber: number) => {
    try {
      setLoading(true);
      setError(null);

      const token = localStorage.getItem('token');
      if (!token) return;

      // --- FIX: USE VERCEL URL & LOWERCASE CATEGORY ---
      const response = await fetch(
        `https://apex-news-ninja-backend.vercel.app/api/v1/news/feed?page=${pageNumber}&page_size=20&categories=${category?.toLowerCase()}`,
        {
          headers: {
            'Authorization': `Bearer ${token}`,
            'Content-Type': 'application/json'
          }
        }
      );

      const data = await response.json();

      if (data.status === 'success') {
        if (pageNumber === 1) {
          setArticles(data.data.articles);
        } else {
          setArticles(prev => [...prev, ...data.data.articles]);
        }
        setTotalArticles(data.data.total);
      } else {
        setError(data.message || 'Failed to load news');
      }
    } catch (err) {
      console.error('Error fetching news:', err);
      setError('Failed to connect to backend.');
    } finally {
      setLoading(false);
    }
  };

  const handleLoadMore = () => {
    const nextPage = page + 1;
    setPage(nextPage);
    fetchCategoryNews(nextPage);
  };

  const handleArticleClick = async (article: Article) => {
    try {
      const token = localStorage.getItem('token');
      if (token) {
        // --- FIX: USE VERCEL URL HERE TOO ---
        await fetch(`https://apex-news-ninja-backend.vercel.app/api/v1/news/article/${article.id}/view`, {
          method: 'POST',
          headers: {
            'Authorization': `Bearer ${token}`,
            'Content-Type': 'application/json'
          }
        });
      }
    } catch (e) {
      console.error("Tracking error", e);
    }
    window.open(article.url, '_blank', 'noopener,noreferrer');
  };

  const getTimeAgo = (dateString: string) => {
    const date = new Date(dateString);
    const now = new Date();
    const diffMs = now.getTime() - date.getTime();
    const diffMins = Math.floor(diffMs / 60000);
    const diffHours = Math.floor(diffMins / 60);
    const diffDays = Math.floor(diffHours / 24);

    if (diffMins < 60) return `${diffMins}m ago`;
    if (diffHours < 24) return `${diffHours}h ago`;
    return `${diffDays}d ago`;
  };

  return (
    <div className="min-h-screen relative">
      <AnimatedBackground />

      <div className="relative z-[2] min-h-screen">
        <header className="sticky top-0 z-20 bg-card/95 backdrop-blur-xl border-b border-primary/20 px-6 py-4">
          <div className="flex items-center gap-4 max-w-7xl mx-auto">
            <Button
              variant="ghost"
              size="icon"
              onClick={() => navigate('/dashboard')}
              className="rounded-full hover:bg-primary/10"
            >
              <ArrowLeft className="w-6 h-6" />
            </Button>
            <div>
              <h1 className="text-xl font-bold gradient-text">{displayCategory} News</h1>
              <p className="text-xs text-muted-foreground">
                {totalArticles} articles available
              </p>
            </div>
          </div>
        </header>

        <main className="p-6 max-w-7xl mx-auto">
          {/* Loading State */}
          {loading && articles.length === 0 && (
            <div className="flex flex-col items-center justify-center py-20">
              <RefreshCw className="w-12 h-12 text-primary animate-spin mb-4" />
              <p>Fetching {displayCategory} news...</p>
            </div>
          )}

          {/* Empty State */}
          {!loading && articles.length === 0 && (
            <div className="flex flex-col items-center justify-center py-20 text-muted-foreground">
              <Newspaper className="w-16 h-16 mb-4 opacity-50" />
              <p>No articles found for {displayCategory} yet.</p>
              <p className="text-sm">Try refreshing the page!</p>
            </div>
          )}

          {/* Error State */}
          {error && (
            <div className="flex items-center gap-2 text-destructive justify-center py-10">
              <AlertCircle className="w-5 h-5" />
              <p>{error}</p>
            </div>
          )}

          {/* News Grid */}
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {articles.map((article, index) => (
              <motion.div
                key={article.id}
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: index * 0.05, duration: 0.4 }}
                whileHover={{ y: -4, transition: { duration: 0.2 } }}
              >
                <Card
                  className="glass border-primary/15 cursor-pointer hover:border-primary/40 transition-all hover:shadow-lg group h-full flex flex-col"
                  onClick={() => handleArticleClick(article)}
                >
                  {article.image_url && (
                    <div className="w-full h-48 overflow-hidden rounded-t-xl shrink-0">
                      <img
                        src={article.image_url}
                        alt={article.title}
                        className="w-full h-full object-cover group-hover:scale-105 transition-transform duration-300"
                      />
                    </div>
                  )}
                  <CardHeader>
                    <div className="flex items-center justify-between mb-2">
                      <span className="px-2.5 py-1 bg-primary/20 text-primary text-xs font-bold rounded-full">
                        {article.source}
                      </span>
                      <span className="text-xs text-muted-foreground flex items-center gap-1">
                        <Clock className="w-3 h-3" />
                        {getTimeAgo(article.published_at)}
                      </span>
                    </div>
                    <CardTitle className="text-lg group-hover:text-primary transition-colors line-clamp-2">
                      {article.title}
                    </CardTitle>
                  </CardHeader>
                  <CardContent className="flex-1">
                    <CardDescription className="line-clamp-3 mb-4">
                      {article.description || "Click to read full story..."}
                    </CardDescription>

                    <div className="flex items-center justify-between mt-auto pt-4 border-t border-primary/10">
                      <span className="text-xs text-muted-foreground">
                        {article.view_count} views
                      </span>
                      <Button variant="ghost" size="sm" className="text-primary h-8 px-2">
                        Read More <ChevronRight className="w-4 h-4 ml-1" />
                      </Button>
                    </div>
                  </CardContent>
                </Card>
              </motion.div>
            ))}
          </div>

          {/* Load More Button */}
          {articles.length > 0 && articles.length < totalArticles && (
            <div className="text-center mt-12 mb-8">
              <Button
                onClick={handleLoadMore}
                disabled={loading}
                variant="outline"
                className="w-full max-w-xs"
              >
                {loading ? <RefreshCw className="w-4 h-4 animate-spin mr-2" /> : null}
                Load More Articles
              </Button>
            </div>
          )}
        </main>
      </div>
    </div>
  );
};

export default NewsCategory;