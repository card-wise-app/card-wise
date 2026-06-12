// Custom SVG credit-card art — no stock images, no real card numbers.
export default function CardArt({ issuer, name, art = "dark", className = "" }: {
  issuer: string; name: string; art?: "lime" | "dark" | "white"; className?: string;
}) {
  const bg = art === "lime" ? "#C1FF72" : art === "dark" ? "#17171C" : "#FFFFFF";
  const fg = art === "dark" ? "#FFFFFF" : "#17171C";
  const sub = art === "dark" ? "rgba(255,255,255,0.65)" : "rgba(23,23,28,0.6)";
  return (
    <svg viewBox="0 0 340 210" className={className} role="img" aria-label={`${issuer} ${name} illustration`}>
      <rect x="2" y="2" width="336" height="206" rx="22" fill={bg} stroke="#17171C" strokeOpacity="0.15" />
      <circle cx="272" cy="52" r="30" fill="#C1FF72" opacity={art === "lime" ? 0.55 : 0.9} />
      <circle cx="298" cy="52" r="30" fill={art === "dark" ? "#FFFFFF" : "#17171C"} opacity="0.85" />
      <text x="24" y="42" fill={fg} fontSize="13" fontWeight="700" fontFamily="Space Grotesk, sans-serif">{issuer.toUpperCase()}</text>
      <rect x="24" y="72" width="46" height="34" rx="7" fill="none" stroke={fg} strokeOpacity="0.5" />
      <path d="M24 89 h46 M35 72 v34 M58 72 v34" stroke={fg} strokeOpacity="0.5" fill="none" />
      <text x="24" y="140" fill={fg} fontSize="17" letterSpacing="2" fontFamily="monospace">•••• •••• •••• ••••</text>
      <text x="24" y="172" fill={fg} fontSize="14" fontWeight="700" fontFamily="Space Grotesk, sans-serif">{name}</text>
      <text x="24" y="190" fill={sub} fontSize="11">Sample art — not a real card. No number, CVV or OTP.</text>
    </svg>
  );
}
