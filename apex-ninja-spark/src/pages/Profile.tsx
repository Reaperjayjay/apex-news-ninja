import { AnimatedBackground } from "@/components/AnimatedBackground";
import { Logo } from "@/components/Logo";
import { GlassCard } from "@/components/GlassCard";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar";
import { motion } from "framer-motion";
import { useNavigate } from "react-router-dom";
import { useState, useEffect, FormEvent } from "react";
import { User, Mail, Phone, Save, ArrowLeft } from "lucide-react";
import { setItem, getItem } from "@/lib/storage";
import { toast } from "sonner";

interface ProfileData {
  name: string;
  email: string;
  phone: string;
  avatarUrl: string;
}

const Profile = () => {
  const navigate = useNavigate();
  const [profile, setProfile] = useState<ProfileData>({
    name: '',
    email: '',
    phone: '',
    avatarUrl: ''
  });

  useEffect(() => {
    const savedProfile = getItem<ProfileData>('apex:profile');
    if (savedProfile) {
      setProfile(savedProfile);
    }
  }, []);

  const handleSubmit = (e: FormEvent) => {
    e.preventDefault();
    setItem('apex:profile', profile);
    toast.success('Profile saved successfully!');
  };

  const getInitials = () => {
    return profile.name
      .split(' ')
      .map(n => n[0])
      .join('')
      .toUpperCase()
      .slice(0, 2);
  };

  return (
    <div className="min-h-screen">
      <AnimatedBackground />

      <div className="relative z-10 min-h-screen px-6 py-12">
        <div className="max-w-4xl mx-auto">
          <div className="mb-8 flex items-center justify-between">
            <Logo variant="full" />
            <Button
              variant="outline"
              onClick={() => navigate('/dashboard')}
              className="border-primary/20 hover:bg-primary/10"
            >
              <ArrowLeft className="w-4 h-4 mr-2" />
              Back to Dashboard
            </Button>
          </div>

          <motion.div
            initial={{ opacity: 0, y: 30 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6 }}
          >
            <GlassCard>
              <div className="text-center mb-8">
                <h1 className="text-3xl md:text-4xl font-black gradient-text mb-2">Your Profile</h1>
                <p className="text-muted-foreground">Manage your personal information</p>
              </div>

              <div className="flex justify-center mb-8">
                <Avatar className="w-24 h-24">
                  <AvatarImage src={profile.avatarUrl} />
                  <AvatarFallback className="bg-primary/20 text-primary text-2xl font-bold">
                    {profile.name ? getInitials() : <User className="w-12 h-12" />}
                  </AvatarFallback>
                </Avatar>
              </div>

              <form onSubmit={handleSubmit} className="space-y-6">
                <div className="space-y-2">
                  <Label htmlFor="name" className="text-sm font-semibold">Full Name</Label>
                  <div className="relative">
                    <User className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-muted-foreground pointer-events-none" />
                    <Input
                      id="name"
                      type="text"
                      placeholder="John Doe"
                      value={profile.name}
                      onChange={(e) => setProfile({ ...profile, name: e.target.value })}
                      className="pl-11 h-12 bg-background/50 border-primary/20 focus:border-primary"
                    />
                  </div>
                </div>

                <div className="space-y-2">
                  <Label htmlFor="email" className="text-sm font-semibold">Email Address</Label>
                  <div className="relative">
                    <Mail className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-muted-foreground pointer-events-none" />
                    <Input
                      id="email"
                      type="email"
                      placeholder="you@example.com"
                      value={profile.email}
                      onChange={(e) => setProfile({ ...profile, email: e.target.value })}
                      className="pl-11 h-12 bg-background/50 border-primary/20 focus:border-primary"
                    />
                  </div>
                </div>

                <div className="space-y-2">
                  <Label htmlFor="phone" className="text-sm font-semibold">Phone Number</Label>
                  <div className="relative">
                    <Phone className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-muted-foreground pointer-events-none" />
                    <Input
                      id="phone"
                      type="tel"
                      placeholder="+234 801 234 5678"
                      value={profile.phone}
                      onChange={(e) => setProfile({ ...profile, phone: e.target.value })}
                      className="pl-11 h-12 bg-background/50 border-primary/20 focus:border-primary"
                    />
                  </div>
                </div>

                <div className="space-y-2">
                  <Label htmlFor="avatar" className="text-sm font-semibold">Avatar URL</Label>
                  <Input
                    id="avatar"
                    type="url"
                    placeholder="https://example.com/avatar.jpg"
                    value={profile.avatarUrl}
                    onChange={(e) => setProfile({ ...profile, avatarUrl: e.target.value })}
                    className="h-12 bg-background/50 border-primary/20 focus:border-primary"
                  />
                </div>

                <Button
                  type="submit"
                  className="w-full h-12 bg-gradient-to-br from-primary to-primary/80 text-background font-bold hover:shadow-lg hover:shadow-primary/50 transition-all"
                >
                  <Save className="w-5 h-5 mr-2" />
                  Save Changes
                </Button>
              </form>
            </GlassCard>
          </motion.div>
        </div>
      </div>
    </div>
  );
};

export default Profile;
