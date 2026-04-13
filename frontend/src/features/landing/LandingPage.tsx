import { useNavigate } from 'react-router-dom'
import { Star, ArrowRight, Github, Zap, MessageSquare, Cpu } from 'lucide-react'

const PLATFORMS = [
  { label: 'Replit', color: 'bg-orange-500/10 text-orange-300 border-orange-500/20' },
  { label: 'Bolt', color: 'bg-purple-500/10 text-purple-300 border-purple-500/20' },
  { label: 'Lovable', color: 'bg-pink-500/10 text-pink-300 border-pink-500/20' },
  { label: 'v0', color: 'bg-gray-500/10 text-gray-300 border-gray-500/20' },
  { label: 'Cursor', color: 'bg-blue-500/10 text-blue-300 border-blue-500/20' },
  { label: 'Emergent', color: 'bg-teal-500/10 text-teal-300 border-teal-500/20' },
]

const HOW_IT_WORKS = [
  {
    step: '01',
    title: 'Describe your idea',
    description: 'Tell us what you want to build in plain English.',
    icon: <MessageSquare size={20} />,
  },
  {
    step: '02',
    title: 'Answer 14 questions',
    description: 'Our AI digs deeper to understand your features, users, and tech stack.',
    icon: <Zap size={20} />,
  },
  {
    step: '03',
    title: 'Get your prompt',
    description: 'Receive a production-ready 25k-token prompt for any vibe-coding platform.',
    icon: <Cpu size={20} />,
  },
]

export default function LandingPage() {
  const navigate = useNavigate()

  return (
    <div className="min-h-screen flex flex-col" style={{ backgroundColor: '#0a0a0f' }}>
      {/* Nav */}
      <nav className="fixed top-0 left-0 right-0 z-50 flex items-center justify-between px-6 py-4 border-b border-white/5 backdrop-blur-sm" style={{ backgroundColor: 'rgba(10,10,15,0.85)' }}>
        <div className="flex items-center gap-2.5">
          <div className="w-7 h-7 rounded-lg flex items-center justify-center" style={{ background: 'linear-gradient(135deg, #818cf8, #a78bfa)' }}>
            <span className="text-white font-bold text-xs">VA</span>
          </div>
          <span className="font-semibold text-white text-sm tracking-tight">Vibe Architect</span>
        </div>

        <div className="flex items-center gap-3">
          <a
            href="https://github.com/your-org/vibe-architect"
            target="_blank"
            rel="noopener noreferrer"
            className="hidden sm:flex items-center gap-1.5 text-gray-400 hover:text-white text-sm transition-colors px-3 py-1.5 rounded-lg hover:bg-white/5"
          >
            <Github size={15} />
            <span>GitHub</span>
          </a>
          <button
            onClick={() => navigate('/intake')}
            className="flex items-center gap-1.5 text-sm font-medium px-4 py-2 rounded-lg text-white transition-all hover:opacity-90 active:scale-95"
            style={{ background: 'linear-gradient(135deg, #818cf8, #a78bfa)' }}
          >
            Start Vibing
            <ArrowRight size={14} />
          </button>
        </div>
      </nav>

      {/* Hero */}
      <section className="flex-1 flex flex-col items-center justify-center px-6 pt-32 pb-24 text-center">
        {/* Glow orb */}
        <div
          className="absolute top-1/3 left-1/2 -translate-x-1/2 -translate-y-1/2 w-96 h-96 rounded-full pointer-events-none"
          style={{
            background: 'radial-gradient(ellipse at center, rgba(129,140,248,0.12) 0%, transparent 70%)',
            filter: 'blur(40px)',
          }}
        />

        {/* Badge */}
        <div className="inline-flex items-center gap-2 px-3 py-1.5 rounded-full border border-white/10 bg-white/5 text-xs text-gray-400 mb-8 backdrop-blur-sm">
          <span className="w-1.5 h-1.5 rounded-full bg-green-400 animate-pulse" />
          Open source · MIT License
        </div>

        {/* Headline */}
        <h1
          className="text-5xl sm:text-6xl lg:text-7xl font-black tracking-tight leading-none mb-6 max-w-4xl"
          style={{
            backgroundClip: 'text',
            WebkitBackgroundClip: 'text',
            WebkitTextFillColor: 'transparent',
            backgroundImage: 'linear-gradient(135deg, #818cf8, #a78bfa, #ec4899)',
          }}
        >
          What will you vibe today?
        </h1>

        {/* Sub-headline */}
        <p className="text-base sm:text-lg text-gray-400 max-w-xl leading-relaxed mb-10">
          Turn your app idea into a production-ready AI prompt in 5 minutes.
          Answer 14 questions. Get a 25k-token prompt for any vibe-coding platform.
        </p>

        {/* CTAs */}
        <div className="flex flex-col sm:flex-row items-center gap-3">
          <button
            onClick={() => navigate('/intake')}
            className="flex items-center gap-2 px-7 py-3.5 rounded-xl text-white font-semibold text-base transition-all hover:opacity-90 active:scale-95 shadow-lg shadow-indigo-500/20"
            style={{ background: 'linear-gradient(135deg, #818cf8, #a78bfa, #ec4899)' }}
          >
            Start Vibing →
          </button>
          <a
            href="https://github.com/your-org/vibe-architect"
            target="_blank"
            rel="noopener noreferrer"
            className="flex items-center gap-2 px-6 py-3.5 rounded-xl text-gray-300 font-medium text-base transition-all hover:text-white hover:bg-white/5 border border-white/10"
          >
            <Star size={16} className="text-yellow-400" />
            Star on GitHub
          </a>
        </div>
      </section>

      {/* How it works */}
      <section className="px-6 pb-20 max-w-4xl mx-auto w-full">
        <p className="text-xs font-semibold uppercase tracking-widest text-gray-600 text-center mb-10">
          How it works
        </p>
        <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
          {HOW_IT_WORKS.map((item) => (
            <div
              key={item.step}
              className="relative rounded-2xl border border-white/8 p-6 transition-all hover:border-white/15"
              style={{ backgroundColor: 'rgba(255,255,255,0.03)' }}
            >
              {/* Subtle gradient top border */}
              <div
                className="absolute top-0 left-6 right-6 h-px rounded-full"
                style={{ background: 'linear-gradient(90deg, transparent, rgba(129,140,248,0.4), transparent)' }}
              />
              <div className="flex items-center gap-3 mb-4">
                <div
                  className="w-9 h-9 rounded-xl flex items-center justify-center text-indigo-300"
                  style={{ backgroundColor: 'rgba(129,140,248,0.1)' }}
                >
                  {item.icon}
                </div>
                <span className="text-xs font-bold text-gray-600 tracking-widest">{item.step}</span>
              </div>
              <h3 className="text-white font-semibold text-sm mb-2">{item.title}</h3>
              <p className="text-gray-500 text-sm leading-relaxed">{item.description}</p>
            </div>
          ))}
        </div>
      </section>

      {/* Platform logos row */}
      <section className="px-6 pb-20 max-w-4xl mx-auto w-full">
        <p className="text-xs font-semibold uppercase tracking-widest text-gray-600 text-center mb-6">
          Works with every vibe-coding platform
        </p>
        <div className="flex flex-wrap items-center justify-center gap-2">
          {PLATFORMS.map((p) => (
            <span
              key={p.label}
              className={`px-4 py-2 rounded-full border text-xs font-semibold tracking-wide ${p.color}`}
            >
              {p.label}
            </span>
          ))}
        </div>
      </section>

      {/* Footer */}
      <footer className="border-t border-white/5 px-6 py-6 text-center">
        <p className="text-gray-600 text-sm">
          Open source. MIT License. Built for builders.
        </p>
      </footer>
    </div>
  )
}
