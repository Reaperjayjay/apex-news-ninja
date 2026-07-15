import { AnimatedBackground } from "@/components/AnimatedBackground";
import { Logo } from "@/components/Logo";
import { GlassCard } from "@/components/GlassCard";
import { Button } from "@/components/ui/button";
import { Label } from "@/components/ui/label";
import { Switch } from "@/components/ui/switch";
import { motion } from "framer-motion";
import { useNavigate } from "react-router-dom";
import { useState, useEffect } from "react";
import { ArrowLeft, Bell, Moon } from "lucide-react";
import { setItem, getItem } from "@/lib/storage";
import { toast } from "sonner";

interface SettingsData {
  darkMode: boolean;
  notifications: boolean;
}

const Settings = () => {
  const navigate = useNavigate();
  const [settings, setSettings] = useState<SettingsData>({
    darkMode: false,
    notifications: true
  });

  useEffect(() => {
    const darkMode = getItem<boolean>('apex:pref:theme');
    const notifications = getItem<boolean>('apex:pref:notifications');

    setSettings({
      darkMode: darkMode ?? false,
      notifications: notifications ?? true
    });
  }, []);

  const handleToggleDarkMode = (checked: boolean) => {
    setSettings(prev => ({ ...prev, darkMode: checked }));
    setItem('apex:pref:theme', checked);
    toast.success(checked ? 'Dark mode enabled' : 'Dark mode disabled');
  };

  const handleToggleNotifications = (checked: boolean) => {
    setSettings(prev => ({ ...prev, notifications: checked }));
    setItem('apex:pref:notifications', checked);
    toast.success(checked ? 'Notifications enabled' : 'Notifications disabled');
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
                <h1 className="text-3xl md:text-4xl font-black gradient-text mb-2">Settings</h1>
                <p className="text-muted-foreground">Customize your Apex News Ninja experience</p>
              </div>

              <div className="space-y-8">
                <div className="flex items-center justify-between p-6 bg-white/5 rounded-xl border border-primary/10">
                  <div className="flex items-center gap-4">
                    <div className="w-12 h-12 bg-primary/20 rounded-lg flex items-center justify-center">
                      <Moon className="w-6 h-6 text-primary" />
                    </div>
                    <div>
                      <Label htmlFor="dark-mode" className="text-base font-semibold cursor-pointer">
                        Dark Mode
                      </Label>
                      <p className="text-sm text-muted-foreground">
                        Toggle dark theme for better viewing at night
                      </p>
                    </div>
                  </div>
                  <Switch
                    id="dark-mode"
                    checked={settings.darkMode}
                    onCheckedChange={handleToggleDarkMode}
                  />
                </div>

                <div className="flex items-center justify-between p-6 bg-white/5 rounded-xl border border-primary/10">
                  <div className="flex items-center gap-4">
                    <div className="w-12 h-12 bg-primary/20 rounded-lg flex items-center justify-center">
                      <Bell className="w-6 h-6 text-primary" />
                    </div>
                    <div>
                      <Label htmlFor="notifications" className="text-base font-semibold cursor-pointer">
                        Notifications
                      </Label>
                      <p className="text-sm text-muted-foreground">
                        Receive WhatsApp notifications for breaking news
                      </p>
                    </div>
                  </div>
                  <Switch
                    id="notifications"
                    checked={settings.notifications}
                    onCheckedChange={handleToggleNotifications}
                  />
                </div>

                <div className="p-6 bg-primary/5 rounded-xl border border-primary/20">
                  <h3 className="font-bold mb-2 flex items-center gap-2">
                    <Bell className="w-5 h-5 text-primary" />
                    About Settings
                  </h3>
                  <p className="text-sm text-muted-foreground">
                    Your preferences are saved locally and will persist across sessions.
                    Dark mode and notification settings can be adjusted at any time.
                  </p>
                </div>
              </div>
            </GlassCard>
          </motion.div>
        </div>
      </div>
    </div>
  );
};

export default Settings;
