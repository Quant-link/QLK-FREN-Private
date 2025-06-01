function SolanaIcon() {
  return (
    <svg
      width="40"
      height="40"
      viewBox="0 0 40 40"
      fill="none"
      xmlns="http://www.w3.org/2000/svg"
    >
      <circle cx="20" cy="20" r="20" fill="#9945FF"/>
      <path
        d="M10.5 25.5h17c.3 0 .6-.1.8-.3l2.7-2.7c.4-.4.1-1.1-.5-1.1h-17c-.3 0-.6.1-.8.3l-2.7 2.7c-.4.4-.1 1.1.5 1.1z"
        fill="url(#solana-grad1)"
      />
      <path
        d="M10.5 30.5h17c.3 0 .6-.1.8-.3l2.7-2.7c.4-.4.1-1.1-.5-1.1h-17c-.3 0-.6.1-.8.3l-2.7 2.7c-.4.4-.1 1.1.5 1.1z"
        fill="url(#solana-grad2)"
      />
      <path
        d="M29.5 14.5h-17c-.3 0-.6.1-.8.3l-2.7 2.7c-.4.4-.1 1.1.5 1.1h17c.3 0 .6-.1.8-.3l2.7-2.7c.4-.4.1-1.1-.5-1.1z"
        fill="url(#solana-grad3)"
      />
      <defs>
        <linearGradient id="solana-grad1" x1="10" y1="24" x2="30" y2="24" gradientUnits="userSpaceOnUse">
          <stop stopColor="#00FFA3"/>
          <stop offset="1" stopColor="#DC1FFF"/>
        </linearGradient>
        <linearGradient id="solana-grad2" x1="10" y1="29" x2="30" y2="29" gradientUnits="userSpaceOnUse">
          <stop stopColor="#00FFA3"/>
          <stop offset="1" stopColor="#DC1FFF"/>
        </linearGradient>
        <linearGradient id="solana-grad3" x1="10" y1="16" x2="30" y2="16" gradientUnits="userSpaceOnUse">
          <stop stopColor="#00FFA3"/>
          <stop offset="1" stopColor="#DC1FFF"/>
        </linearGradient>
      </defs>
    </svg>
  );
}

export default SolanaIcon; 