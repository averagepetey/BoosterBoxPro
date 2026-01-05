/**
 * Logo Component
 * Displays the BoosterBoxPro rocket boot logo
 */

import Image from 'next/image';
import Link from 'next/link';

interface LogoProps {
  size?: 'sm' | 'md' | 'lg' | 'xl';
  showText?: boolean;
  className?: string;
  href?: string;
}

const sizeMap = {
  sm: 96,
  md: 120,
  lg: 192,
  xl: 360,
};

export function Logo({ 
  size = 'md', 
  showText = false, 
  className = '',
  href = '/'
}: LogoProps) {
  const logoSize = sizeMap[size];
  
  const logoElement = (
    <div className={`flex items-center gap-3 ${className}`}>
      <Image
        src="/images/BoosterProTextLogo.png"
        alt="BoosterBoxPro Logo"
        width={logoSize}
        height={logoSize}
        className="object-contain"
        priority
      />
      {showText && (
        <span className="text-xl font-bold text-foreground">
          BoosterBoxPro
        </span>
      )}
    </div>
  );

  if (href) {
    return (
      <Link href={href} className="hover:opacity-80 transition-opacity">
        {logoElement}
      </Link>
    );
  }

  return logoElement;
}

