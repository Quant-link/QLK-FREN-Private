// Cryptocurrency logo utilities using CoinGecko API

const COINGECKO_CRYPTO_MAPPING: Record<string, string> = {
  'bitcoin': 'bitcoin',
  'ethereum': 'ethereum', 
  'solana': 'solana',
  'cardano': 'cardano',
  'polkadot': 'polkadot',
  'chainlink': 'chainlink'
};

export function getCryptoIcon(cryptoName: string) {
  const normalizedName = cryptoName.toLowerCase();
  const coinId = COINGECKO_CRYPTO_MAPPING[normalizedName] || normalizedName;
  
  return (
    <CryptoLogo 
      cryptoName={normalizedName}
      coinId={coinId}
      size={40}
    />
  );
}

interface CryptoLogoProps {
  cryptoName: string;
  coinId: string;
  size?: number;
}

function CryptoLogo({ cryptoName, coinId, size = 40 }: CryptoLogoProps) {
  // Use CoinGecko's direct image URLs for better performance
  const getLogoUrl = (coinId: string) => {
    switch (coinId) {
      case 'bitcoin':
        return 'https://coin-images.coingecko.com/coins/images/1/large/bitcoin.png';
      case 'ethereum':
        return 'https://coin-images.coingecko.com/coins/images/279/large/ethereum.png';
      case 'solana':
        return 'https://coin-images.coingecko.com/coins/images/4128/large/solana.png';
      case 'cardano':
        return 'https://coin-images.coingecko.com/coins/images/975/large/cardano.png';
      case 'polkadot':
        return 'https://coin-images.coingecko.com/coins/images/12171/large/polkadot.png';
      case 'chainlink':
        return 'https://coin-images.coingecko.com/coins/images/877/large/chainlink-new-logo.png';
      default:
        return 'https://coin-images.coingecko.com/coins/images/1/large/bitcoin.png';
    }
  };

  const logoUrl = getLogoUrl(coinId);

  return (
    <img
      src={logoUrl}
      alt={`${cryptoName} logo`}
      width={size}
      height={size}
      className="rounded-full object-cover"
      onError={(e) => {
        // Fallback to a default crypto icon if image fails to load
        e.currentTarget.src = 'https://coin-images.coingecko.com/coins/images/1/large/bitcoin.png';
      }}
    />
  );
}

export function getCryptoDisplayName(cryptoName: string): string {
  const normalizedName = cryptoName.toLowerCase();
  
  switch (normalizedName) {
    case 'bitcoin':
      return 'BITCOIN';
    case 'ethereum':
      return 'ETHEREUM';
    case 'solana':
      return 'SOLANA';
    case 'cardano':
      return 'CARDANO';
    case 'polkadot':
      return 'POLKADOT';
    case 'chainlink':
      return 'CHAINLINK';
    default:
      return cryptoName.toUpperCase();
  }
} 