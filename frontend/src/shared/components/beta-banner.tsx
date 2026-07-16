/**
 * Banner de versión beta.
 * Para sacarlo: borrá este archivo y quitá `<BetaBanner />` de `app/layout.tsx`
 * (y el badge BETA del sidebar si lo dejamos).
 */
export function BetaBanner() {
  return (
    <div
      role="status"
      className="sticky top-0 z-[100] border-b border-[var(--border)] bg-[var(--amber)]/15 px-4 py-1.5 text-center text-[12px] font-medium tracking-wide text-[var(--text)]"
    >
      Versión <span className="font-semibold">beta</span> — entorno de pruebas. Algunas funciones
      pueden cambiar.
    </div>
  )
}
