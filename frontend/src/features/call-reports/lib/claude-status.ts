import type { ClaudeApiStatus, FathomApiStatus } from '../types'

export function formatCallReportError(message: string | null | undefined): string {
  const text = (message || '').trim()
  if (!text) return 'Error al analizar la llamada.'
  const lower = text.toLowerCase()
  if (lower.includes('falta api key de fathom')) {
    return 'Falta API key de Fathom. Configurala en Conexiones API → Fathom.'
  }
  if (
    lower.includes('billing_error') ||
    lower.includes('credit balance') ||
    lower.includes('too low to access the anthropic api') ||
    lower.includes('plans & billing') ||
    lower.includes('no tenés saldo disponible')
  ) {
    return (
      'No tenés saldo disponible en tu cuenta de Anthropic. ' +
      'Recargá créditos en console.anthropic.com → Plans & Billing.'
    )
  }
  if (
    lower.includes('authentication_error') ||
    lower.includes('invalid x-api-key') ||
    lower.includes('invalid api key')
  ) {
    return 'La API key de Anthropic no es válida. Revisala en Conexiones API.'
  }
  return text
}

export function claudeStatusLabel(status: ClaudeApiStatus['status']): string {
  switch (status) {
    case 'ok':
      return 'Activa'
    case 'no_balance':
      return 'Sin saldo'
    case 'invalid_key':
      return 'Key inválida'
    case 'not_configured':
      return 'Sin configurar'
    case 'permission_denied':
      return 'Sin permisos'
    case 'rate_limited':
      return 'Límite alcanzado'
    default:
      return 'No verificada'
  }
}

export function fathomStatusLabel(status: FathomApiStatus['status']): string {
  switch (status) {
    case 'ok':
      return 'Activa'
    case 'invalid_key':
      return 'Key inválida'
    case 'not_configured':
      return 'Sin configurar'
    default:
      return 'No verificada'
  }
}
