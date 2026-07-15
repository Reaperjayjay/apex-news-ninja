import { AnimatedBackground } from "@/components/AnimatedBackground";
import { Button } from "@/components/ui/button";
import { motion } from "framer-motion";
import { useNavigate } from "react-router-dom";
import { useState } from "react";
import { Check, Newspaper, Briefcase, Zap, TrendingUp, Heart, Globe, Music, Code, Phone } from "lucide-react";

const Onboarding = () => {
  const navigate = useNavigate();
  const [currentStep, setCurrentStep] = useState(1);
  const [selectedDomains, setSelectedDomains] = useState<string[]>([]);
  const [whatsappNumber, setWhatsappNumber] = useState("");

  const domains = [
    { id: "technology", name: "Technology", icon: Code, color: "from-cyan-500 to-blue-600" },
    { id: "business", name: "Business", icon: Briefcase, color: "from-blue-500 to-indigo-600" },
    { id: "sports", name: "Sports", icon: Zap, color: "from-green-500 to-emerald-600" },
    { id: "entertainment", name: "Entertainment", icon: Music, color: "from-purple-500 to-pink-600" },
    { id: "health", name: "Health", icon: Heart, color: "from-red-500 to-rose-600" },
    { id: "science", name: "Science", icon: Globe, color: "from-teal-500 to-cyan-600" },
    { id: "politics", name: "Politics", icon: TrendingUp, color: "from-orange-500 to-red-600" },
    { id: "world", name: "World News", icon: Newspaper, color: "from-indigo-500 to-purple-600" },
  ];

  const steps = [
    { number: 1, label: "Select Domains" },
    { number: 2, label: "Connect WhatsApp" },
    { number: 3, label: "Complete Setup" }
  ];

  const toggleDomain = (domainId: string) => {
    setSelectedDomains(prev =>
      prev.includes(domainId)
        ? prev.filter(d => d !== domainId)
        : [...prev, domainId]
    );
  };

  const handleNext = () => {
    if (currentStep === 1 && selectedDomains.length === 0) {
      alert("Please select at least one domain");
      return;
    }
    if (currentStep === 2 && !whatsappNumber) {
      alert("Please enter your WhatsApp number");
      return;
    }
    if (currentStep < 3) {
      setCurrentStep(currentStep + 1);
    } else {
      navigate('/dashboard');
    }
  };

  const progress = (currentStep / 3) * 100;

  return (
    <div className="min-h-screen">
      <AnimatedBackground />

      {/* Progress Bar */}
      <div className="fixed top-0 left-0 right-0 z-[1000] glass border-b border-primary/20 py-8 px-6">
        <div className="max-w-4xl mx-auto">
          <div className="flex justify-between mb-4">
            {steps.map((step) => (
              <div key={step.number} className="flex-1 text-center relative">
                {step.number < steps.length && (
                  <div className="absolute top-[15px] left-1/2 w-full h-0.5 bg-white/10" />
                )}
                <div className="relative inline-flex flex-col items-center">
                  <div
                    className={`w-8 h-8 rounded-full flex items-center justify-center text-sm font-bold mb-2 transition-all ${
                      step.number === currentStep
                        ? 'bg-gradient-to-br from-primary to-secondary text-black scale-125 shadow-lg shadow-primary/50'
                        : step.number < currentStep
                        ? 'bg-accent text-black'
                        : 'bg-white/10 border-2 border-white/20'
                    }`}
                  >
                    {step.number < currentStep ? <Check className="w-4 h-4" /> : step.number}
                  </div>
                  <span className={`text-xs font-semibold ${
                    step.number === currentStep ? 'text-primary' : step.number < currentStep ? 'text-accent' : 'text-muted-foreground'
                  }`}>
                    {step.label}
                  </span>
                </div>
              </div>
            ))}
          </div>
          <div className="h-1 bg-white/10 rounded-full overflow-hidden">
            <motion.div
              className="h-full bg-gradient-to-r from-primary to-accent"
              style={{ width: `${progress}%` }}
              initial={{ width: 0 }}
              animate={{ width: `${progress}%` }}
              transition={{ duration: 0.5 }}
            />
          </div>
        </div>
      </div>

      {/* Content */}
      <div className="relative z-10 min-h-screen flex items-center justify-center px-6 pt-40 pb-20">
        <motion.div
          key={currentStep}
          initial={{ opacity: 0, x: 20 }}
          animate={{ opacity: 1, x: 0 }}
          exit={{ opacity: 0, x: -20 }}
          transition={{ duration: 0.5 }}
          className="w-full max-w-5xl"
        >
          {/* Step 1: Select Domains */}
          {currentStep === 1 && (
            <div className="text-center">
              <h2 className="text-5xl font-black mb-4 gradient-text">
                Choose Your News Domains
              </h2>
              <p className="text-xl text-muted-foreground mb-12 max-w-2xl mx-auto">
                Select the topics that matter most to you. We'll curate personalized news from these domains.
              </p>

              <div className="grid grid-cols-2 md:grid-cols-4 gap-6">
                {domains.map((domain, index) => (
                  <motion.button
                    key={domain.id}
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ delay: index * 0.05 }}
                    onClick={() => toggleDomain(domain.id)}
                    className={`glass rounded-2xl p-8 transition-all hover:scale-105 ${
                      selectedDomains.includes(domain.id)
                        ? 'ring-2 ring-primary bg-primary/10'
                        : 'hover:bg-white/5'
                    }`}
                  >
                    <div className={`w-16 h-16 rounded-xl bg-gradient-to-br ${domain.color} flex items-center justify-center mx-auto mb-4`}>
                      <domain.icon className="w-8 h-8 text-white" />
                    </div>
                    <h3 className="font-bold text-lg mb-2">{domain.name}</h3>
                    {selectedDomains.includes(domain.id) && (
                      <motion.div
                        initial={{ scale: 0 }}
                        animate={{ scale: 1 }}
                        className="mt-2"
                      >
                        <div className="inline-flex items-center gap-1 bg-primary text-black px-3 py-1 rounded-full text-xs font-bold">
                          <Check className="w-3 h-3" />
                          Selected
                        </div>
                      </motion.div>
                    )}
                  </motion.button>
                ))}
              </div>

              <p className="text-sm text-muted-foreground mt-8">
                {selectedDomains.length} domain{selectedDomains.length !== 1 ? 's' : ''} selected
              </p>
            </div>
          )}

          {/* Step 2: Connect WhatsApp */}
          {currentStep === 2 && (
            <div className="text-center max-w-2xl mx-auto">
              <div className="w-20 h-20 bg-gradient-to-br from-primary to-secondary rounded-full flex items-center justify-center mx-auto mb-6">
                <Phone className="w-10 h-10 text-black" />
              </div>
              <h2 className="text-5xl font-black mb-4 gradient-text">
                Connect Your WhatsApp
              </h2>
              <p className="text-xl text-muted-foreground mb-12">
                Enter your WhatsApp number to receive daily AI-curated news summaries
              </p>

              <div className="glass rounded-3xl p-10">
                <div className="space-y-6">
                  <div className="text-left">
                    <label className="block text-sm font-semibold mb-2">WhatsApp Number</label>
                    <input
                      type="tel"
                      value={whatsappNumber}
                      onChange={(e) => setWhatsappNumber(e.target.value)}
                      placeholder="+1 (234) 567-8900"
                      className="w-full h-14 px-6 bg-background/50 border border-primary/20 rounded-xl focus:border-primary focus:outline-none focus:ring-2 focus:ring-primary/20 transition-all text-lg"
                    />
                  </div>

                  <div className="bg-primary/5 border border-primary/20 rounded-xl p-6 text-left">
                    <h4 className="font-bold mb-3 flex items-center gap-2">
                      <Zap className="w-5 h-5 text-primary" />
                      What to Expect
                    </h4>
                    <ul className="space-y-2 text-sm text-muted-foreground">
                      <li className="flex items-start gap-2">
                        <Check className="w-4 h-4 text-accent mt-0.5" />
                        <span>Daily digest at your preferred time</span>
                      </li>
                      <li className="flex items-start gap-2">
                        <Check className="w-4 h-4 text-accent mt-0.5" />
                        <span>Breaking news alerts for selected domains</span>
                      </li>
                      <li className="flex items-start gap-2">
                        <Check className="w-4 h-4 text-accent mt-0.5" />
                        <span>Interactive summaries you can respond to</span>
                      </li>
                    </ul>
                  </div>
                </div>
              </div>
            </div>
          )}

          {/* Step 3: Complete */}
          {currentStep === 3 && (
            <div className="text-center max-w-2xl mx-auto">
              <motion.div
                initial={{ scale: 0 }}
                animate={{ scale: 1 }}
                transition={{ type: "spring", duration: 0.6 }}
                className="w-24 h-24 bg-gradient-to-br from-accent to-primary rounded-full flex items-center justify-center mx-auto mb-6"
              >
                <Check className="w-12 h-12 text-black" />
              </motion.div>
              <h2 className="text-5xl font-black mb-4 gradient-text">
                You're All Set!
              </h2>
              <p className="text-xl text-muted-foreground mb-12">
                Your personalized news dashboard is ready. Start exploring curated content now!
              </p>

              <div className="glass rounded-3xl p-10 text-left space-y-4">
                <div className="flex items-start gap-4 p-4 bg-primary/5 rounded-xl">
                  <div className="w-12 h-12 bg-gradient-to-br from-primary to-secondary rounded-lg flex items-center justify-center flex-shrink-0">
                    <Check className="w-6 h-6 text-black" />
                  </div>
                  <div>
                    <h4 className="font-bold mb-1">{selectedDomains.length} Domains Selected</h4>
                    <p className="text-sm text-muted-foreground">
                      {domains.filter(d => selectedDomains.includes(d.id)).map(d => d.name).join(", ")}
                    </p>
                  </div>
                </div>

                <div className="flex items-start gap-4 p-4 bg-primary/5 rounded-xl">
                  <div className="w-12 h-12 bg-gradient-to-br from-primary to-secondary rounded-lg flex items-center justify-center flex-shrink-0">
                    <Phone className="w-6 h-6 text-black" />
                  </div>
                  <div>
                    <h4 className="font-bold mb-1">WhatsApp Connected</h4>
                    <p className="text-sm text-muted-foreground">{whatsappNumber}</p>
                  </div>
                </div>
              </div>
            </div>
          )}

          {/* Navigation Buttons */}
          <div className="flex justify-between items-center mt-12">
            <Button
              variant="outline"
              onClick={() => currentStep > 1 && setCurrentStep(currentStep - 1)}
              disabled={currentStep === 1}
              className="border-primary/20 hover:bg-primary/10"
            >
              Back
            </Button>
            <Button
              onClick={handleNext}
              className="bg-gradient-to-br from-primary to-secondary text-black font-bold px-8 hover:shadow-lg hover:shadow-primary/50"
            >
              {currentStep === 3 ? "Go to Dashboard" : "Continue"}
            </Button>
          </div>
        </motion.div>
      </div>
    </div>
  );
};

export default Onboarding;
