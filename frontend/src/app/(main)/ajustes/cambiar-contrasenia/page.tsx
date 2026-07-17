'use client'

import { FormEvent, useEffect, useState } from 'react'
import { changePassword } from '@/features/auth/services/auth-service'
import { useAuthUser } from '@/shared/hooks/use-auth-user'
import { useToast } from '@/shared/components/toast'

const ADMIN_PASSWORD = 'sistemas897'
const UNLOCK_KEY = 'atv-change-password-unlocked'

const LABEL =
  'mb-2 block text-[10px] font-semibold uppercase tracking-wider text-[var(--text3)]'
const INPUT =
  'w-full rounded-lg border border-[var(--border2)] bg-[var(--bg3)] px-4 py-3 text-sm text-[var(--text)] outline-none placeholder:text-[var(--text3)]'

function AdminGate({ onUnlock }: { onUnlock: () => void }) {
  const [adminPassword, setAdminPassword] = useState('')
  const [error, setError] = useState('')

  const onSubmit = (e: FormEvent) => {
    e.preventDefault()
    if (adminPassword.trim() !== ADMIN_PASSWORD) {
      setError('Clave de admin incorrecta.')
      return
    }
    try {
      sessionStorage.setItem(UNLOCK_KEY, '1')
    } catch {
      /* ignore */
    }
    onUnlock()
  }

  return (
    <div className="mx-auto max-w-sm py-10">
      <h2 className="text-lg font-bold tracking-tight">Usuario y contraseña</h2>
      <p className="mt-1 text-[12px] text-[var(--text3)]">
        Ingresá la clave de admin para continuar.
      </p>
      <form onSubmit={onSubmit} className="mt-6 space-y-4">
        <div>
          <label htmlFor="admin-password" className={LABEL}>
            Clave de admin
          </label>
          <input
            id="admin-password"
            type="password"
            autoComplete="off"
            value={adminPassword}
            onChange={(e) => {
              setAdminPassword(e.target.value)
              if (error) setError('')
            }}
            className={INPUT}
            autoFocus
          />
        </div>
        {error ? <p className="text-[12px] text-[var(--red)]">{error}</p> : null}
        <button
          type="submit"
          className="w-full rounded-lg border border-[var(--border)] bg-[var(--bg2)] px-4 py-2.5 text-[13px] font-medium text-[var(--text)] hover:bg-[var(--bg3)]"
        >
          Continuar
        </button>
      </form>
    </div>
  )
}

export default function CambiarContraseniaPage() {
  const { ready, userId, username } = useAuthUser()
  const { toast } = useToast()
  const [unlocked, setUnlocked] = useState(false)
  const [checked, setChecked] = useState(false)
  const [adminPassword, setAdminPassword] = useState('')
  const [newUsername, setNewUsername] = useState('')
  const [newPassword, setNewPassword] = useState('')
  const [confirmPassword, setConfirmPassword] = useState('')
  const [pending, setPending] = useState(false)
  const [error, setError] = useState('')

  useEffect(() => {
    try {
      setUnlocked(sessionStorage.getItem(UNLOCK_KEY) === '1')
    } catch {
      setUnlocked(false)
    }
    setChecked(true)
  }, [])

  useEffect(() => {
    if (username) setNewUsername(username)
  }, [username])

  const onUnlock = () => {
    setAdminPassword(ADMIN_PASSWORD)
    setUnlocked(true)
  }

  const onSubmit = async (e: FormEvent) => {
    e.preventDefault()
    setError('')
    const nextUser = newUsername.trim()
    const nextPass = newPassword.trim()
    if (!nextUser && !nextPass) {
      setError('Indicá un nuevo usuario y/o una nueva contraseña.')
      return
    }
    if (nextPass && nextPass !== confirmPassword) {
      setError('Las contraseñas no coinciden.')
      return
    }
    if (nextPass && nextPass.length < 6) {
      setError('La nueva contraseña debe tener al menos 6 caracteres.')
      return
    }
    setPending(true)
    const result = await changePassword(adminPassword || ADMIN_PASSWORD, {
      newUsername: nextUser || undefined,
      newPassword: nextPass || undefined,
    })
    setPending(false)
    if (result.error) {
      setError(result.error)
      return
    }
    setNewPassword('')
    setConfirmPassword('')
    toast('Datos de cuenta actualizados.')
  }

  if (!checked) {
    return <div className="py-12 text-[13px] text-[var(--text3)]">Cargando…</div>
  }

  if (!unlocked) {
    return <AdminGate onUnlock={onUnlock} />
  }

  if (!ready) {
    return <div className="py-12 text-[13px] text-[var(--text3)]">Cargando sesión…</div>
  }

  if (!userId) {
    return (
      <div className="py-12 text-[13px] text-[var(--text3)]">
        Iniciá sesión para cambiar usuario o contraseña.
      </div>
    )
  }

  return (
    <div className="mx-auto max-w-md">
      <h2 className="text-lg font-bold tracking-tight">Usuario y contraseña</h2>
      <p className="mt-1 text-[12px] text-[var(--text3)]">
        Podés cambiar el usuario, la contraseña, o ambos.
      </p>

      <form onSubmit={(e) => void onSubmit(e)} className="mt-6 space-y-4">
        <div>
          <label htmlFor="new-username" className={LABEL}>
            Usuario
          </label>
          <input
            id="new-username"
            type="text"
            autoComplete="username"
            value={newUsername}
            onChange={(e) => setNewUsername(e.target.value)}
            className={INPUT}
            required
          />
        </div>
        <div>
          <label htmlFor="new-password" className={LABEL}>
            Nueva contraseña (opcional)
          </label>
          <input
            id="new-password"
            type="password"
            autoComplete="new-password"
            value={newPassword}
            onChange={(e) => setNewPassword(e.target.value)}
            className={INPUT}
            minLength={6}
          />
        </div>
        <div>
          <label htmlFor="confirm-password" className={LABEL}>
            Confirmar contraseña
          </label>
          <input
            id="confirm-password"
            type="password"
            autoComplete="new-password"
            value={confirmPassword}
            onChange={(e) => setConfirmPassword(e.target.value)}
            className={INPUT}
            minLength={6}
          />
        </div>
        {error ? <p className="text-[12px] text-[var(--red)]">{error}</p> : null}
        <button
          type="submit"
          disabled={pending}
          className="w-full rounded-lg border border-[var(--border)] bg-[var(--bg2)] px-4 py-2.5 text-[13px] font-medium text-[var(--text)] hover:bg-[var(--bg3)] disabled:opacity-50"
        >
          {pending ? 'Guardando…' : 'Guardar cambios'}
        </button>
      </form>
    </div>
  )
}
