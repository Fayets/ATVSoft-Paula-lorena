import { BrandLogo } from '@/shared/components/brand-logo'

export function AuthBranding() {
  return (
    <div className="mb-8 text-center">
      <BrandLogo
        alt="ATV"
        className="mx-auto h-24 w-auto max-w-[96px] object-contain"
      />
    </div>
  )
}
