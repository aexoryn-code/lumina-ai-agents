export default function Home() {
  return (
    <main className="flex min-h-screen flex-col items-center justify-center p-24">
      <div className="z-10 max-w-5xl w-full items-center justify-center font-mono text-sm">
        <h1 className="text-6xl font-bold text-center mb-8 bg-gradient-to-r from-blue-500 to-purple-600 bg-clip-text text-transparent">
          Lumina AI Agents
        </h1>
        <p className="text-center text-xl text-muted-foreground mb-12">
          Enterprise AI Operating System
        </p>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          <div className="p-6 border border-border rounded-lg bg-card">
            <h3 className="text-lg font-semibold mb-2">Multi-Agent</h3>
            <p className="text-sm text-muted-foreground">
              Specialized agents for coding, research, UI/UX, and more
            </p>
          </div>
          <div className="p-6 border border-border rounded-lg bg-card">
            <h3 className="text-lg font-semibold mb-2">Adaptive Reasoning</h3>
            <p className="text-sm text-muted-foreground">
              Dynamic reasoning modes from fast to strategic
            </p>
          </div>
          <div className="p-6 border border-border rounded-lg bg-card">
            <h3 className="text-lg font-semibold mb-2">Multi-Model</h3>
            <p className="text-sm text-muted-foreground">
              Intelligent routing across OpenAI, Claude, Gemini, and more
            </p>
          </div>
        </div>
      </div>
    </main>
  )
}
