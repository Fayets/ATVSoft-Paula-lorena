import Image from 'next/image'
import atvLogo from '@/assets/atv-logo.png'

type BrandLogoProps = {
  className?: string
  alt?: string
}

/** Logo ATV (PNG importado). */
export function BrandLogo({
  className = 'h-10 w-auto max-w-[56px] flex-shrink-0 object-contain',
  alt = 'ATV',
}: BrandLogoProps) {
  return (
    <Image
      src={atvLogo}
      alt={alt}
      width={atvLogo.width}
      height={atvLogo.height}
      className={className}
      sizes="120px"
      priority
    />
  )
}
