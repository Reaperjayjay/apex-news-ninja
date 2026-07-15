import { useEffect, useRef } from 'react';

export const AnimatedBackground = () => {
  const particlesRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const container = particlesRef.current;
    if (!container) return;

    // Create 30 particles
    for (let i = 0; i < 30; i++) {
      const particle = document.createElement('div');
      particle.className = 'absolute w-[3px] h-[3px] bg-primary rounded-full animate-float';
      particle.style.left = `${Math.random() * 100}%`;
      particle.style.animationDelay = `${Math.random() * 20}s`;
      particle.style.boxShadow = '0 0 10px hsl(var(--primary))';
      container.appendChild(particle);
    }

    return () => {
      if (container) {
        container.innerHTML = '';
      }
    };
  }, []);

  return (
    <>
      {/* Radial gradients background */}
      <div 
        className="fixed inset-0 z-0"
        style={{
          background: `
            radial-gradient(circle at 20% 50%, rgba(0, 212, 255, 0.15), transparent 50%),
            radial-gradient(circle at 80% 80%, rgba(0, 102, 204, 0.1), transparent 50%),
            linear-gradient(180deg, #000 0%, #0a0f1c 100%)
          `
        }}
      />
      {/* Particles */}
      <div ref={particlesRef} className="fixed inset-0 z-[1] pointer-events-none" />
    </>
  );
};
