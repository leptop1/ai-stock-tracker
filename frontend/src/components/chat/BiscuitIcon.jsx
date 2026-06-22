export default function BiscuitIcon({ size = 20, className = '' }) {
  const s = size
  return (
    <svg
      width={s}
      height={s}
      viewBox="0 0 32 32"
      fill="none"
      xmlns="http://www.w3.org/2000/svg"
      className={className}
    >
      {/* Left ear */}
      <ellipse cx="10" cy="7" rx="3.2" ry="6" fill="currentColor" opacity="0.9" />
      <ellipse cx="10" cy="7" rx="1.6" ry="4.2" fill="currentColor" opacity="0.4" />
      {/* Right ear */}
      <ellipse cx="22" cy="7" rx="3.2" ry="6" fill="currentColor" opacity="0.9" />
      <ellipse cx="22" cy="7" rx="1.6" ry="4.2" fill="currentColor" opacity="0.4" />
      {/* Head */}
      <ellipse cx="16" cy="19" rx="10" ry="9" fill="currentColor" />
      {/* Eyes */}
      <circle cx="12.5" cy="17.5" r="1.5" fill="white" opacity="0.9" />
      <circle cx="19.5" cy="17.5" r="1.5" fill="white" opacity="0.9" />
      <circle cx="13" cy="17.5" r="0.7" fill="currentColor" opacity="0.7" />
      <circle cx="20" cy="17.5" r="0.7" fill="currentColor" opacity="0.7" />
      {/* Nose */}
      <ellipse cx="16" cy="21" rx="1.2" ry="0.8" fill="white" opacity="0.7" />
    </svg>
  )
}
