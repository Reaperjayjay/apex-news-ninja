import { Link } from "react-router-dom";
import { cn } from "@/lib/utils";
import apexLogo from "@/assets/apex-ai-studios-logo.png";

interface LogoProps {
  showSubtitle?: boolean;
  className?: string;
  variant?: "full" | "compact";
}

export const Logo = ({ showSubtitle = true, className, variant = "full" }: LogoProps) => {
  return (
    <Link to="/" className={cn("flex items-center gap-3 group", className)}>
      <div 
        className="flex items-center justify-center transition-all duration-300"
        style={{
          filter: 'drop-shadow(0 0 12px hsl(var(--primary) / 0.6))'
        }}
      >
        <img 
          src={apexLogo} 
          alt="APEX AI Studios" 
          className={cn(
            "transition-all duration-300 group-hover:scale-105",
            variant === "compact" ? "h-10 w-10" : "h-12 w-12"
          )}
        />
      </div>
      {variant === "full" && (
        <div className="flex flex-col">
          <span className="text-base sm:text-lg font-extrabold tracking-wide text-foreground">
            APEX NEWS NINJA
          </span>
          {showSubtitle && (
            <span className="text-[0.65rem] sm:text-[0.7rem] text-muted-foreground font-medium">
              by APEX AI Studios
            </span>
          )}
        </div>
      )}
    </Link>
  );
};
