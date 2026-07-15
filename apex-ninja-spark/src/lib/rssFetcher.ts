interface NewsItem {
  id: string;
  title: string;
  snippet: string;
  source: string;
  category: string;
  time: string;
  url: string;
}

export const fetchAINews = async (): Promise<NewsItem[]> => {
  return new Promise((resolve) => {
    setTimeout(() => {
      resolve([
        {
          id: 'ai-1',
          title: 'Latest AI Research Breakthroughs',
          snippet: 'Discover the newest developments in artificial intelligence and machine learning.',
          source: 'AI Weekly',
          category: 'AI',
          time: '1 hour ago',
          url: 'https://example.com/ai-research'
        },
        {
          id: 'ai-2',
          title: 'Neural Networks Achieve New Milestone',
          snippet: 'Deep learning models demonstrate unprecedented accuracy in complex tasks.',
          source: 'Tech Science',
          category: 'AI',
          time: '3 hours ago',
          url: 'https://example.com/neural-networks'
        }
      ]);
    }, 500);
  });
};
