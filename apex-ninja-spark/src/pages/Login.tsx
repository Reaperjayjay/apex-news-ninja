import { AnimatedBackground } from "@/components/AnimatedBackground";
import { Logo } from "@/components/Logo";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { motion } from "framer-motion";
import { useNavigate } from "react-router-dom";
import { useState, FormEvent } from "react";
import { Mail, Lock, Phone } from "lucide-react";
import { useAuth } from "@/context/AuthContext";
import { toast } from "sonner";
import { GoogleLogin } from '@react-oauth/google'; // <--- 1. NEW IMPORT

const Login = () => {
  const navigate = useNavigate();
  const { login } = useAuth();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [phone, setPhone] = useState("");
  const [countryCode, setCountryCode] = useState("+234");
  const [errors, setErrors] = useState<{ [key: string]: string }>({});

  // --- 2. NEW: Handle Google Login ---
  const handleGoogleSuccess = async (credentialResponse: any) => {
    try {
      const { credential } = credentialResponse;
      if (!credential) return;

      // Send to your Secure Backend
      const response = await fetch("https://apex-news-ninja-backend.vercel.app/api/v1/auth/google", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ token: credential }),
      });

      const data = await response.json();

      if (response.ok && data.status === "success") {
        const token = data.data.access_token;
        localStorage.setItem("token", token);
        if (login) login(token);

        toast.success("Welcome back!");
        navigate('/dashboard');
      } else {
        if (response.status === 429) {
          toast.error("Too many login attempts. Please wait.");
        } else {
          toast.error(data.detail || "Google Login failed");
        }
      }
    } catch (err) {
      console.error(err);
      toast.error("Network error during Google Login");
    }
  };

  const validatePassword = (pwd: string): boolean => {
    // Keep your existing validation logic
    const minLength = pwd.length >= 8;
    const hasUpperCase = /[A-Z]/.test(pwd);
    const hasNumber = /[0-9]/.test(pwd);
    const hasSpecialChar = /[!@#$%^&*(),.?":{}|<>]/.test(pwd);

    if (!minLength) {
      setErrors(prev => ({ ...prev, password: "Password must be at least 8 characters" }));
      return false;
    }
    if (!hasUpperCase) {
      setErrors(prev => ({ ...prev, password: "Password must contain at least one uppercase letter" }));
      return false;
    }
    if (!hasNumber) {
      setErrors(prev => ({ ...prev, password: "Password must contain at least one number" }));
      return false;
    }
    if (!hasSpecialChar) {
      setErrors(prev => ({ ...prev, password: "Password must contain at least one special character" }));
      return false;
    }

    setErrors(prev => ({ ...prev, password: "" }));
    return true;
  };

  const validatePhone = (phoneNum: string): boolean => {
    const digitsOnly = phoneNum.replace(/\D/g, '');
    if (digitsOnly.length < 10 || digitsOnly.length > 11) {
      setErrors(prev => ({ ...prev, phone: "Phone number must be 10-11 digits" }));
      return false;
    }
    setErrors(prev => ({ ...prev, phone: "" }));
    return true;
  };

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault();

    const isPasswordValid = validatePassword(password);
    if (!email) {
      setErrors(prev => ({ ...prev, email: "Email is required" }));
      return;
    }

    if (isPasswordValid && email) {
      try {
        // --- 3. Updated to use LIVE Backend URL ---
        const response = await fetch("https://apex-news-ninja-backend.vercel.app/api/v1/auth/login", {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify({
            email: email,
            password: password,
          }),
        });

        const data = await response.json();

        if (response.ok) {
          const token = data.data.access_token;
          localStorage.setItem("token", token);

          if (login) {
            login(token);
          }

          toast.success("Login successful!");
          navigate('/dashboard');
        } else {
          toast.error(data.message || "Login failed");
          setErrors(prev => ({ ...prev, form: data.message }));
        }
      } catch (error) {
        console.error("Login Error:", error);
        toast.error("Connection failed. Check internet.");
      }
    }
  };

  return (
    <div className="min-h-screen">
      <AnimatedBackground />

      <div className="relative z-10 min-h-screen flex flex-col items-center justify-center px-6 py-12">
        <motion.div
          initial={{ opacity: 0, y: 30 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6 }}
          className="w-full max-w-md"
        >
          <div className="mb-8 flex justify-center">
            <Logo variant="full" />
          </div>

          <Card className="glass border-primary/20">
            <CardHeader className="text-center">
              <CardTitle className="text-3xl font-black gradient-text">Welcome Back</CardTitle>
              <CardDescription>Sign in to access your personalized news feed</CardDescription>
            </CardHeader>
            <CardContent>
              <form onSubmit={handleSubmit} className="space-y-6" role="form">
                <div className="space-y-2">
                  <Label htmlFor="email" className="text-sm font-semibold">Email Address</Label>
                  <div className="relative">
                    <Mail className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-muted-foreground pointer-events-none" />
                    <Input
                      id="email"
                      type="email"
                      placeholder="you@example.com"
                      value={email}
                      onChange={(e) => setEmail(e.target.value)}
                      className="pl-11 h-12 bg-background/50 border-primary/20 focus:border-primary"
                      required
                    />
                  </div>
                  {errors.email && <p className="text-sm text-destructive">{errors.email}</p>}
                </div>

                <div className="space-y-2">
                  <Label htmlFor="phone" className="text-sm font-semibold">Phone Number</Label>
                  <div className="flex gap-2">
                    <Select value={countryCode} onValueChange={setCountryCode}>
                      <SelectTrigger className="w-32 h-12 bg-background/50 border-primary/20">
                        <SelectValue />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="+234">🇳🇬 +234</SelectItem>
                        <SelectItem value="+1">🇺🇸 +1</SelectItem>
                        <SelectItem value="+44">🇬🇧 +44</SelectItem>
                        <SelectItem value="+91">🇮🇳 +91</SelectItem>
                      </SelectContent>
                    </Select>
                    <div className="relative flex-1">
                      <Phone className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-muted-foreground pointer-events-none" />
                      <Input
                        id="phone"
                        type="tel"
                        placeholder="8012345678"
                        value={phone}
                        onChange={(e) => {
                          const value = e.target.value.replace(/\D/g, '');
                          setPhone(value);
                          if (value.length > 0) validatePhone(value);
                        }}
                        className="pl-11 h-12 bg-background/50 border-primary/20 focus:border-primary"
                        required
                      />
                    </div>
                  </div>
                  {errors.phone && <p className="text-sm text-destructive">{errors.phone}</p>}
                </div>

                <div className="space-y-2">
                  <Label htmlFor="password" className="text-sm font-semibold">Password</Label>
                  <div className="relative">
                    <Lock className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-muted-foreground pointer-events-none" />
                    <Input
                      id="password"
                      type="password"
                      placeholder="••••••••"
                      value={password}
                      onChange={(e) => {
                        setPassword(e.target.value);
                        if (e.target.value.length > 0) validatePassword(e.target.value);
                      }}
                      className="pl-11 h-12 bg-background/50 border-primary/20 focus:border-primary"
                      required
                    />
                  </div>
                  {errors.password && <p className="text-sm text-destructive">{errors.password}</p>}
                </div>

                <Button
                  type="submit"
                  className="w-full h-12 bg-gradient-to-br from-primary to-primary/80 text-background font-bold hover:shadow-lg hover:shadow-primary/50 transition-all"
                  style={{ boxShadow: '0 4px 20px hsl(var(--primary) / 0.3)' }}
                >
                  Sign In
                </Button>
              </form>

              <div className="mt-6">
                <div className="relative">
                  <div className="absolute inset-0 flex items-center">
                    <span className="w-full border-t border-primary/20" />
                  </div>
                  <div className="relative flex justify-center text-xs uppercase">
                    <span className="bg-card px-2 text-muted-foreground">Or continue with</span>
                  </div>
                </div>

                {/* --- 4. REAL GOOGLE BUTTON --- */}
                <div className="mt-4 flex justify-center">
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

              <p className="text-center text-sm text-muted-foreground mt-6">
                Don't have an account?{" "}
                <button
                  type="button"
                  onClick={() => navigate('/auth')}
                  className="text-primary font-semibold hover:underline transition-all"
                >
                  Sign up
                </button>
              </p>
            </CardContent>
          </Card>
        </motion.div>
      </div>
    </div>
  );
};

export default Login;