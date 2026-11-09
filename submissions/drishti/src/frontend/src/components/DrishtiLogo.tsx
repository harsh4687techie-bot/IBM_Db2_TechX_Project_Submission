import React from 'react';

export interface DrishtiLogoProps {
  variant?: 'horizontal' | 'symbol' | 'compact' | 'light-bg';
  size?: number;
  className?: string;
  showSubtitle?: boolean;
}

/**
 * DRISHTI Master Brand Identity
 * Geometric D with embedded optical focus aperture.
 * Communicates: Vision, Perspective, Intelligence, and Absolute Clarity.
 */
export const DrishtiSymbol: React.FC<{ size?: number; fill?: string; stroke?: string }> = ({
  size = 32,
  fill = '#FFFFFF',
  stroke = '#292929'
}) => {
  return (
    <svg
      width={size}
      height={size}
      viewBox="0 0 64 64"
      fill="none"
      xmlns="http://www.w3.org/2000/svg"
      style={{ display: 'block', flexShrink: 0 }}
    >
      {/* Background boundary frame */}
      <rect width="64" height="64" rx="8" fill={fill === '#000000' ? '#FFFFFF' : '#121212'} />
      <rect x="0.5" y="0.5" width="63" height="63" rx="7.5" stroke={stroke} />
      
      {/* Left Vertical Spine (Data Integrity / Foundation) */}
      <path d="M16 15 H24 V49 H16 Z" fill={fill} />
      
      {/* Precision D-Arc (Institutional Curvature) */}
      <path
        d="M24 15 H35 C44.39 15 52 22.61 52 32 C52 41.39 44.39 49 35 49 H24 V42 H35 C40.52 42 45 37.52 45 32 C45 26.48 40.52 22 35 22 H24 V15 Z"
        fill={fill}
      />
      
      {/* Inner Optical Focal Core ("Drishti" / Vision Center) */}
      <circle cx="34.5" cy="32" r="4" fill={fill} />
      <circle cx="34.5" cy="32" r="7.5" stroke={fill} strokeWidth="1.2" strokeDasharray="2 2" opacity="0.6" />
    </svg>
  );
};

export const DrishtiLogo: React.FC<DrishtiLogoProps> = ({
  variant = 'horizontal',
  size = 32,
  className = '',
  showSubtitle = true
}) => {
  const isLightBg = variant === 'light-bg';
  const textColor = isLightBg ? '#000000' : '#FFFFFF';
  const subtextColor = isLightBg ? '#555555' : '#707070';
  const fillColor = isLightBg ? '#000000' : '#FFFFFF';
  const strokeColor = isLightBg ? '#D0D0D0' : '#292929';

  if (variant === 'symbol') {
    return <DrishtiSymbol size={size} fill={fillColor} stroke={strokeColor} />;
  }

  if (variant === 'compact') {
    return (
      <div className={`drishti-logo-compact ${className}`} style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
        <DrishtiSymbol size={size} fill={fillColor} stroke={strokeColor} />
        <div style={{ display: 'flex', flexDirection: 'column', lineHeight: 1 }}>
          <span style={{
            fontSize: size * 0.52,
            fontWeight: 700,
            letterSpacing: '0.14em',
            color: textColor,
            fontFamily: 'Inter, -apple-system, sans-serif'
          }}>
            DRISHTI
          </span>
          {showSubtitle && (
            <span style={{
              fontSize: 9,
              letterSpacing: '0.12em',
              color: subtextColor,
              marginTop: 3,
              fontWeight: 500,
              textTransform: 'uppercase'
            }}>
              Db2 + AI
            </span>
          )}
        </div>
      </div>
    );
  }

  // Default Primary Horizontal Logo
  return (
    <div className={`drishti-logo-primary ${className}`} style={{ display: 'flex', alignItems: 'center', gap: 14 }}>
      <DrishtiSymbol size={size} fill={fillColor} stroke={strokeColor} />
      <div style={{ display: 'flex', flexDirection: 'column' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
          <span style={{
            fontSize: size * 0.58,
            fontWeight: 700,
            letterSpacing: '0.16em',
            color: textColor,
            fontFamily: 'Inter, -apple-system, sans-serif'
          }}>
            DRISHTI
          </span>
          <span style={{
            fontSize: 9,
            fontWeight: 600,
            letterSpacing: '0.08em',
            padding: '2px 6px',
            border: `1px solid ${strokeColor}`,
            color: subtextColor,
            borderRadius: 2,
            textTransform: 'uppercase'
          }}>
            IBM Db2 &bull; Agentic AI
          </span>
        </div>
        {showSubtitle && (
          <p style={{
            fontSize: 11,
            color: subtextColor,
            letterSpacing: '0.04em',
            marginTop: 2,
            fontWeight: 400
          }}>
            See Beyond Data.
          </p>
        )}
      </div>
    </div>
  );
};

