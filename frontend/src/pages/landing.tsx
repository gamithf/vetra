import { useNavigate } from 'react-router-dom'
import { PawPrint, Shield, CalendarCheck, Mic, ArrowRight, Stethoscope, Package, Brain } from 'lucide-react'
import { Button } from '@/components/ui/button'
import { useAuth } from '@/context/auth-context'

const features = [
  {
    icon: <Mic className="h-6 w-6" />,
    title: 'AI Co-Pilot',
    desc: 'Voice-to-notes for vets. Dictate findings and let AI handle the paperwork.',
  },
  {
    icon: <CalendarCheck className="h-6 w-6" />,
    title: 'Smart Calendar',
    desc: 'Drag-and-drop scheduling with room assignments and automated reminders.',
  },
  {
    icon: <Package className="h-6 w-6" />,
    title: 'Inventory Tracking',
    desc: 'Real-time stock alerts so you never run out of critical supplies.',
  },
  {
    icon: <Brain className="h-6 w-6" />,
    title: 'Agentic AI',
    desc: 'Autonomous clinical note processing from raw dictation to structured EMR.',
  },
  {
    icon: <Shield className="h-6 w-6" />,
    title: 'Secure EMR',
    desc: 'Full medical records with timeline view, lab results, and vaccination history.',
  },
  {
    icon: <Stethoscope className="h-6 w-6" />,
    title: 'Check-In/Out',
    desc: 'Streamlined client workflow from arrival to payment and billing.',
  },
]

const stats = [
  { value: '60%', label: 'Less admin time' },
  { value: '3x', label: 'Faster check-ins' },
  { value: '99%', label: 'Uptime' },
  { value: '10k+', label: 'Patients served' },
]

export function LandingPage() {
  const navigate = useNavigate()
  const { user } = useAuth()

  return (
    <div className="min-h-screen bg-gradient-to-b from-white via-accent/20 to-white">
      <header className="sticky top-0 z-50 border-b bg-white/80 backdrop-blur-md">
        <div className="mx-auto flex h-16 max-w-7xl items-center justify-between px-6">
          <div className="flex items-center gap-2">
            <div className="flex h-9 w-9 items-center justify-center rounded-xl bg-primary shadow-sm">
              <PawPrint className="h-5 w-5 text-primary-foreground" />
            </div>
            <span className="text-xl font-bold tracking-tight">Vetra</span>
          </div>
          <div className="flex items-center gap-4">
            {user ? (
              <Button onClick={() => navigate(user.role === 'vet' ? '/vet-dashboard' : '/staff-dashboard')}>
                Go to Dashboard
                <ArrowRight size={16} />
              </Button>
            ) : (
              <>
                <Button variant="ghost" onClick={() => navigate('/login')}>
                  Sign In
                </Button>
                <Button onClick={() => navigate('/register')}>
                  Get Started
                  <ArrowRight size={16} />
                </Button>
              </>
            )}
          </div>
        </div>
      </header>

      <section className="relative overflow-hidden px-6 pt-24 pb-32">
        <div className="mx-auto max-w-7xl">
          <div className="mx-auto max-w-3xl text-center">
            <div className="mb-6 inline-flex items-center gap-2 rounded-full bg-primary/10 px-4 py-1.5 text-sm font-medium text-primary">
              <PawPrint size={14} />
              AI-Powered Veterinary Practice Management
            </div>
            <h1 className="text-5xl font-bold tracking-tight text-foreground sm:text-6xl lg:text-7xl">
              The{' '}
              <span className="bg-gradient-to-r from-primary to-emerald-400 bg-clip-text text-transparent">
                AI-First
              </span>{' '}
              Clinic OS
            </h1>
            <p className="mt-6 text-lg text-muted-foreground sm:text-xl leading-relaxed max-w-2xl mx-auto">
              One platform for the entire clinic. Vets dictate, AI writes notes. 
              Staff manage schedules and inventory. Patients get treated faster.
            </p>
            <div className="mt-10 flex items-center justify-center gap-4">
              <Button size="lg" className="h-12 px-8 text-base" onClick={() => navigate('/register')}>
                Start Free Trial
                <ArrowRight size={18} />
              </Button>
              <Button variant="outline" size="lg" className="h-12 px-8 text-base" onClick={() => navigate('/login')}>
                Sign In
              </Button>
            </div>
          </div>
        </div>
        <div className="absolute -top-40 right-0 -z-10 h-[600px] w-[600px] rounded-full bg-primary/5 blur-3xl" />
        <div className="absolute -bottom-40 left-0 -z-10 h-[400px] w-[400px] rounded-full bg-emerald-100/30 blur-3xl" />
      </section>

      <section className="px-6 py-20">
        <div className="mx-auto max-w-7xl">
          <div className="mx-auto mb-16 max-w-2xl text-center">
            <h2 className="text-3xl font-bold tracking-tight sm:text-4xl">
              Everything your clinic needs
            </h2>
            <p className="mt-4 text-lg text-muted-foreground">
              Two interfaces, one powerful platform. Designed for how vets and staff actually work.
            </p>
          </div>

          <div className="grid gap-6 sm:grid-cols-2 lg:grid-cols-3">
            {features.map((feature) => (
              <div
                key={feature.title}
                className="group rounded-xl border bg-card p-6 transition-all duration-300 hover:shadow-lg hover:-translate-y-1"
              >
                <div className="mb-4 flex h-12 w-12 items-center justify-center rounded-xl bg-primary/10 text-primary group-hover:bg-primary group-hover:text-primary-foreground transition-all duration-300">
                  {feature.icon}
                </div>
                <h3 className="mb-2 text-lg font-semibold">{feature.title}</h3>
                <p className="text-sm text-muted-foreground leading-relaxed">{feature.desc}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      <section className="border-y bg-card px-6 py-20">
        <div className="mx-auto max-w-7xl">
          <div className="grid grid-cols-2 gap-8 lg:grid-cols-4">
            {stats.map((stat) => (
              <div key={stat.label} className="text-center">
                <div className="text-4xl font-bold text-primary">{stat.value}</div>
                <div className="mt-2 text-sm text-muted-foreground">{stat.label}</div>
              </div>
            ))}
          </div>
        </div>
      </section>

      <section className="px-6 py-24">
        <div className="mx-auto max-w-3xl text-center">
          <h2 className="text-3xl font-bold tracking-tight sm:text-4xl">
            Ready to transform your clinic?
          </h2>
          <p className="mt-4 text-lg text-muted-foreground">
            Join thousands of veterinary practices using Vetra to save time and improve care.
          </p>
          <div className="mt-10">
            <Button size="lg" className="h-12 px-8 text-base" onClick={() => navigate('/register')}>
              Get Started Free
              <ArrowRight size={18} />
            </Button>
          </div>
        </div>
      </section>

      <footer className="border-t px-6 py-8">
        <div className="mx-auto flex max-w-7xl items-center justify-between text-sm text-muted-foreground">
          <div className="flex items-center gap-2">
            <PawPrint size={16} className="text-primary" />
            <span className="font-medium text-foreground">Vetra</span>
          </div>
          <p>&copy; {new Date().getFullYear()} Vetra. All rights reserved.</p>
        </div>
      </footer>
    </div>
  )
}
