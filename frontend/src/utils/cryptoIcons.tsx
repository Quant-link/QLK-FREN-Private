import BitcoinIcon from '../components/BitcoinIcon';
import EthereumIcon from '../components/EthereumIcon';
import SolanaIcon from '../components/SolanaIcon';
import CardanoIcon from '../components/CardanoIcon';
import PolkadotIcon from '../components/PolkadotIcon';
import ChainlinkIcon from '../components/ChainlinkIcon';

export function getCryptoIcon(cryptoName: string) {
  const normalizedName = cryptoName.toLowerCase();
  
  switch (normalizedName) {
    case 'bitcoin':
      return <BitcoinIcon />;
    case 'ethereum':
      return <EthereumIcon />;
    case 'solana':
      return <SolanaIcon />;
    case 'cardano':
      return <CardanoIcon />;
    case 'polkadot':
      return <PolkadotIcon />;
    case 'chainlink':
      return <ChainlinkIcon />;
    default:
      return <BitcoinIcon />; // Fallback to Bitcoin icon
  }
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