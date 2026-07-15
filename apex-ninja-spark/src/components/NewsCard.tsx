import React, { useState } from 'react';
import { GlassCard } from './GlassCard';
import { cn } from '@/lib/utils';
import { ExternalLink, TrendingUp, TrendingDown, Minus } from 'lucide-react';

export interface Article {
    _id: string;
    title: string;
    url: string;
    published_at: string;
    source: string;
    description?: string;
    content?: string;
    image_url?: string | null;

    ai_processed?: boolean;
    sentiment?: 'Bullish' | 'Bearish' | 'Neutral';
    summary?: string;
    key_points?: string[];
}

interface NewsCardProps {
    article: Article;
    className?: string;
}

export const NewsCard = ({ article, className }: NewsCardProps) => {
    const [imageError, setImageError] = useState(false);

    // 1. ROBUST CHECK: Do we actually have an AI summary?
    // We only say "Yes" if the flag is true AND the string is not empty.
    const hasValidAiSummary = article.ai_processed && article.summary && article.summary.trim().length > 0;

    // 2. DECIDE CONTENT: Use AI summary if valid, otherwise fallback to description
    const displayContent = hasValidAiSummary
        ? article.summary
        : (article.description || article.content || "Click to read full story.");

    const getSentimentConfig = (sentiment?: string) => {
        switch (sentiment?.toLowerCase()) {
            case 'bullish':
                return { color: 'bg-green-500/10 text-green-500 border-green-500/20', icon: <TrendingUp className="w-3 h-3 mr-1" />, label: 'Bullish' };
            case 'bearish':
                return { color: 'bg-red-500/10 text-red-500 border-red-500/20', icon: <TrendingDown className="w-3 h-3 mr-1" />, label: 'Bearish' };
            case 'neutral':
                return { color: 'bg-blue-500/10 text-blue-500 border-blue-500/20', icon: <Minus className="w-3 h-3 mr-1" />, label: 'Neutral' };
            default:
                return null;
        }
    };

    const sentimentConfig = getSentimentConfig(article.sentiment);

    return (
        <GlassCard className={cn("flex flex-col h-full relative overflow-hidden group", className)} hover={true}>

            {/* Image Section */}
            {article.image_url && !imageError && (
                <div className="relative w-full h-48 mb-4 rounded-lg overflow-hidden bg-white/5 border border-white/10 shrink-0">
                    <img
                        src={article.image_url}
                        alt={article.title}
                        className="w-full h-full object-cover transition-transform duration-500 group-hover:scale-105"
                        onError={() => setImageError(true)}
                    />
                </div>
            )}

            {/* Header */}
            <div className="flex justify-between items-center text-xs text-muted-foreground mb-3 z-10 relative shrink-0">
                <span className="font-medium uppercase tracking-wider text-primary/80">{article.source}</span>
                <span>{new Date(article.published_at).toLocaleDateString()}</span>
            </div>

            {/* Title */}
            <h3 className="text-lg font-bold leading-tight mb-3 text-foreground z-10 relative group-hover:text-primary transition-colors shrink-0">
                {article.title}
            </h3>

            {/* Sentiment Badge - Only show if valid AI summary exists */}
            {hasValidAiSummary && sentimentConfig && (
                <div className="mb-4 z-10 relative shrink-0">
                    <span className={cn(
                        "inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-bold border backdrop-blur-md",
                        sentimentConfig.color
                    )}>
                        {sentimentConfig.icon}
                        {sentimentConfig.label}
                    </span>
                </div>
            )}

            {/* Content Section */}
            <div className="text-sm text-muted-foreground mb-4 flex-grow z-10 relative">
                {/* Only show "AI SUMMARY" label if we actually have one */}
                {hasValidAiSummary && (
                    <span className="text-xs font-bold text-primary mr-2 uppercase tracking-wide">
                        AI Summary:
                    </span>
                )}
                <span className="leading-relaxed line-clamp-4">
                    {displayContent}
                </span>
            </div>

            {/* Key Points - Only show if valid */}
            {hasValidAiSummary && article.key_points && article.key_points.length > 0 && (
                <div className="mb-4 bg-background/40 border border-white/5 rounded-lg p-3 text-xs z-10 relative backdrop-blur-sm shrink-0">
                    <p className="font-semibold mb-2 opacity-90 text-primary/90">Key Takeaways:</p>
                    <ul className="space-y-1.5">
                        {article.key_points.slice(0, 3).map((point, idx) => (
                            <li key={idx} className="flex items-start opacity-80">
                                <span className="mr-2 mt-1 w-1 h-1 rounded-full bg-primary flex-shrink-0" />
                                <span className="line-clamp-2">{point}</span>
                            </li>
                        ))}
                    </ul>
                </div>
            )}

            {/* Footer */}
            <div className="mt-auto pt-4 border-t border-white/5 z-10 relative shrink-0">
                <a
                    href={article.url}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="inline-flex items-center text-sm font-medium text-primary hover:text-primary/80 transition-colors"
                >
                    Read full story <ExternalLink className="w-3 h-3 ml-1" />
                </a>
            </div>

        </GlassCard>
    );
};