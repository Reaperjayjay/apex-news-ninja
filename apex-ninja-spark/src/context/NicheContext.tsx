import { createContext, useContext, useState, useEffect, ReactNode } from 'react';
import { setItem, getItem } from '@/lib/storage';

interface NicheContextType {
  selectedNiches: string[];
  addNiche: (niche: string) => void;
  removeNiche: (niche: string) => void;
  toggleNiche: (niche: string) => void;
  clearNiches: () => void;
}

const NicheContext = createContext<NicheContextType | undefined>(undefined);

export const NicheProvider = ({ children }: { children: ReactNode }) => {
  const [selectedNiches, setSelectedNiches] = useState<string[]>([]);

  useEffect(() => {
    const saved = getItem<string[]>('apex:selectedNiches');
    if (saved && Array.isArray(saved)) {
      setSelectedNiches(saved);
    }
  }, []);

  useEffect(() => {
    setItem('apex:selectedNiches', selectedNiches);
  }, [selectedNiches]);

  const addNiche = (niche: string) => {
    if (!selectedNiches.includes(niche)) {
      setSelectedNiches([...selectedNiches, niche]);
    }
  };

  const removeNiche = (niche: string) => {
    setSelectedNiches(selectedNiches.filter(n => n !== niche));
  };

  const toggleNiche = (niche: string) => {
    if (selectedNiches.includes(niche)) {
      removeNiche(niche);
    } else {
      addNiche(niche);
    }
  };

  const clearNiches = () => {
    setSelectedNiches([]);
  };

  return (
    <NicheContext.Provider value={{ selectedNiches, addNiche, removeNiche, toggleNiche, clearNiches }}>
      {children}
    </NicheContext.Provider>
  );
};

export const useNiche = () => {
  const context = useContext(NicheContext);
  if (context === undefined) {
    throw new Error('useNiche must be used within a NicheProvider');
  }
  return context;
};
