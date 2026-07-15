import { AnimatedBackground } from "@/components/AnimatedBackground";
import { Logo } from "@/components/Logo";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Separator } from "@/components/ui/separator";
import { motion } from "framer-motion";
import { useNavigate } from "react-router-dom";
import { useState } from "react";
import { Brain, Zap, Target, Mail, Lock, User } from "lucide-react";
import { toast } from "sonner";
import { useAuth } from "@/context/AuthContext";
import { AUTH_ENDPOINTS } from "@/lib/api";
import { GoogleLogin } from '@react-oauth/google';

interface ValidationError {
  msg: string;
}

const Auth = () => {
  const navigate = useNavigate();
  const { login } = useAuth();

  const [isLogin, setIsLogin] = useState(false);
  const [formData, setFormData] = useState({
    name: "",
    email: "",
    password: ""
  });
  const [loading, setLoading] = useState(false);

  const features = [
    {
      icon: Brain,
      title: "AI-Powered Intelligence",
      description: "Advanced algorithms curate the most relevant news for you"
    },
    {
      icon: Zap,
      title: "Instant Delivery",
      description: "Get your personalized digest directly on WhatsApp in seconds"
    },
    {
      icon: Target,
      title: "Precision Targeting",
      description: "Choose from 15+ domains to match your exact interests"
    }
  ];

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setFormData({ ...formData, [e.target.id]: e.target.value });
  };

  const handleGoogleSuccess = async (credentialResponse: any) => {
    try {
      setLoading(true);
      const { credential } = credentialResponse;

      if (!credential) {
        toast.error("Google login failed to retrieve token");
        return;
      }

      const response = await fetch("https://apex-news-ninja-backend.vercel.app/api/v1/auth/google", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ token: credential }),
      });

      const data = await response.json();

      if (response.ok && data.status === "success") {
        localStorage.setItem("token", data.data.access_token);
        if (login) login(data.data.access_token);

        toast.success("Welcome back!");
        navigate("/dashboard");
      } else {
        if (response.status === 429) {
          toast.error("Too many login attempts. Please wait a minute.");
        } else {
          toast.error(data.detail || "Google Login failed");
        }
      }
    } catch (err) {
      console.error(err);
      toast.error("Network error during Google Login");
    } finally {
      setLoading(false);
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);

    const url = isLogin ? AUTH_ENDPOINTS.LOGIN : AUTH_ENDPOINTS.REGISTER;

    try {
      const randomSuffix = Math.floor(Math.random() * 10000);
      const generatedUsername = formData.email.split('@')[0] + randomSuffix;

      const payload = isLogin
        ? {
          email: formData.email,
          password: formData.password
        }
        : {
          email: formData.email,
          password: formData.password,
          full_name: formData.name,
          username: generatedUsername,
          phone_number: "0000000000"
        };

      const response = await fetch(url, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload),
      });

      const data = await response.json();

      if (response.ok) {
        if (data.data && data.data.access_token) {
          const token = data.data.access_token;
          localStorage.setItem("token", token);
          if (login) login(token);

          toast.success(isLogin ? "Login successful!" : "Account created!");
          navigate('/dashboard');
        } else if (!isLogin) {
          toast.success("Account created! Please sign in.");
          setIsLogin(true);
        }
      } else {
        console.error("Auth Error:", data);
        if (response.status === 422 && data.detail) {
          const errorMsg = Array.isArray(data.detail)
            ? data.detail.map((e: ValidationError) => e.msg).join(", ")
            : JSON.stringify(data.detail);
          toast.error("Validation Error: " + errorMsg);
        } else {
          toast.error(data.detail || data.message || "Authentication failed");
        }
      }
    } catch (error) {
      console.error("Network Error:", error);
      toast.error("Failed to connect. Check console for details.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen">
      <AnimatedBackground />

      <div className="relative z-10 min-h-screen grid lg:grid-cols-2">
        {/* Left Panel */}
        <div className="hidden lg:flex flex-col justify-center p-12 lg:p-16 xl:p-20 relative">
          <div className="absolute top-8 lg:top-12 left-8 lg:left-12 xl:left-20">
            <Logo variant="full" />
          </div>

          <motion.div
            initial={{ opacity: 0, y: 30 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.8 }}
            className="max-w-xl mt-32"
          >
            {/* Added mt-32 to push text down on laptops */}

            <h1 className="text-4xl lg:text-5xl xl:text-6xl font-black mb-8 lg:mb-12 gradient-text leading-tight">
              Your Personal News Revolution Starts Here
            </h1>

            <div className="space-y-6 lg:space-y-8">
              {features.map((feature, index) => (
                <motion.div
                  key={feature.title}
                  initial={{ opacity: 0, x: -30 }}
                  animate={{ opacity: 1, x: 0 }}
                  transition={{ delay: 0.2 + index * 0.1 }}
                  className="flex gap-4 lg:gap-6 items-start p-4 lg:p-6 bg-card/80 backdrop-blur-xl border border-primary/15 rounded-xl lg:rounded-2xl hover:bg-primary/10 hover:border-primary/30 transition-all"
                >
                  <div
                    className="w-12 h-12 lg:w-14 lg:h-14 rounded-lg lg:rounded-xl flex items-center justify-center flex-shrink-0"
                    style={{
                      background: 'linear-gradient(135deg, hsl(var(--primary) / 0.2), hsl(var(--secondary) / 0.2))',
                      border: '2px solid hsl(var(--primary) / 0.3)',
                      boxShadow: '0 2px 12px hsl(var(--primary) / 0.15)'
                    }}
                  >
                    <feature.icon className="w-6 h-6 lg:w-7 lg:h-7 text-primary" />
                  </div>
                  <div>
                    <h3 className="text-lg lg:text-xl font-bold mb-1 lg:mb-2">{feature.title}</h3>
                    <p className="text-sm lg:text-base text-muted-foreground">{feature.description}</p>
                  </div>
                </motion.div>
              ))}
            </div>
          </motion.div>
        </div>

        {/* Right Panel - Auth Form */}
        <div className="flex items-center justify-center p-6 sm:p-8">
          <motion.div
            initial={{ opacity: 0, y: 30 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.8, delay: 0.2 }}
            className="w-full max-w-md"
          >
            <div className="bg-card/90 backdrop-blur-xl border border-primary/15 rounded-2xl lg:rounded-3xl p-6 sm:p-8 lg:p-10">
              <div className="lg:hidden mb-6 sm:mb-8 flex justify-center">
                <Logo showSubtitle={true} variant="full" />
              </div>

              <div className="text-center mb-6 sm:mb-8">
                <h2 className="text-2xl sm:text-3xl font-black mb-2">
                  {isLogin ? "Welcome Back" : "Create Account"}
                </h2>
                <p className="text-sm sm:text-base text-muted-foreground">
                  {isLogin
                    ? "Enter your credentials to access your dashboard"
                    : "Join thousands of users staying informed daily"
                  }
                </p>
              </div>

              <form onSubmit={handleSubmit} className="space-y-4 sm:space-y-6">
                {!isLogin && (
                  <div className="space-y-2">
                    <Label htmlFor="name" className="text-sm font-semibold">Full Name</Label>
                    <div className="relative">
                      <User className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 sm:w-5 sm:h-5 text-muted-foreground pointer-events-none" />
                      <Input
                        id="name"
                        type="text"
                        placeholder="John Doe"
                        className="pl-10 sm:pl-11 h-10 sm:h-12 bg-background/50 border-primary/20 focus:border-primary text-sm sm:text-base"
                        required={!isLogin}
                        value={formData.name}
                        onChange={handleChange}
                      />
                    </div>
                  </div>
                )}

                <div className="space-y-2">
                  <Label htmlFor="email" className="text-sm font-semibold">Email Address</Label>
                  <div className="relative">
                    <Mail className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 sm:w-5 sm:h-5 text-muted-foreground pointer-events-none" />
                    <Input
                      id="email"
                      type="email"
                      placeholder="you@example.com"
                      className="pl-10 sm:pl-11 h-10 sm:h-12 bg-background/50 border-primary/20 focus:border-primary text-sm sm:text-base"
                      required
                      value={formData.email}
                      onChange={handleChange}
                    />
                  </div>
                </div>

                <div className="space-y-2">
                  <Label htmlFor="password" className="text-sm font-semibold">Password</Label>
                  <div className="relative">
                    <Lock className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 sm:w-5 sm:h-5 text-muted-foreground pointer-events-none" />
                    <Input
                      id="password"
                      type="password"
                      placeholder="••••••••"
                      className="pl-10 sm:pl-11 h-10 sm:h-12 bg-background/50 border-primary/20 focus:border-primary text-sm sm:text-base"
                      required
                      value={formData.password}
                      onChange={handleChange}
                    />
                  </div>
                </div>

                <Button
                  type="submit"
                  disabled={loading}
                  className="w-full h-10 sm:h-12 bg-gradient-to-br from-primary to-primary/80 text-background font-bold text-sm sm:text-base hover:shadow-lg hover:shadow-primary/50 transition-all"
                  style={{ boxShadow: '0 4px 20px hsl(var(--primary) / 0.3)' }}
                >
                  {loading ? "Processing..." : (isLogin ? "Sign In" : "Create Account")}
                </Button>
              </form>

              <div className="mt-6 sm:mt-8">
                <div className="relative">
                  <Separator className="my-4 sm:my-6" />
                  <div className="absolute inset-0 flex items-center justify-center">
                    <span className="bg-card px-4 text-xs sm:text-sm text-muted-foreground">OR</span>
                  </div>
                </div>

                <div className="flex justify-center w-full">
                  <GoogleLogin
                    onSuccess={handleGoogleSuccess}
                    onError={() => toast.error("Google Login Failed")}
                    theme="filled_blue"
                    shape="pill"
                    width="350"
                    text="continue_with"
                  />
                </div>
              </div>

              <p className="text-center text-xs sm:text-sm text-muted-foreground mt-4 sm:mt-6">
                {isLogin ? "Don't have an account? " : "Already have an account? "}
                <button
                  type="button"
                  onClick={() => setIsLogin(!isLogin)}
                  className="text-primary font-semibold hover:underline transition-all"
                >
                  {isLogin ? "Sign up" : "Sign in"}
                </button>
              </p>
            </div>
          </motion.div>
        </div>
      </div>
    </div>
  );
};

export default Auth;