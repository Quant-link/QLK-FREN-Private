import { useMetaMask } from '../hooks/useMetaMask';
import { WalletIcon } from './Icons';

export function MetaMaskWallet() {
  const {
    isConnected,
    account,
    isConnecting,
    error,
    chainId,
    balance,
    connect,
    disconnect,
    switchToEthereum,
    formatAccount,
    isMetaMaskInstalled,
  } = useMetaMask();

  // Get network name from chainId
  const getNetworkName = (chainId: string | null) => {
    if (!chainId) return 'Unknown';
    switch (chainId) {
      case '0x1':
        return 'Ethereum Mainnet';
      case '0x89':
        return 'Polygon';
      case '0xa':
        return 'Optimism';
      case '0xa4b1':
        return 'Arbitrum';
      case '0x38':
        return 'BSC';
      default:
        return `Chain ${parseInt(chainId, 16)}`;
    }
  };

  const isEthereumMainnet = chainId === '0x1';

  if (!isMetaMaskInstalled) {
    return (
      <div className="bg-white rounded-[18px] p-6">
        <div className="text-center">
          <div className="mb-4">
            <WalletIcon size={48} />
          </div>
          <h3 className="text-lg font-bold text-gray-800 mb-2">MetaMask Not Found</h3>
          <p className="text-gray-600 mb-4">
            Please install MetaMask to connect your wallet.
          </p>
          <a
            href="https://metamask.io/download/"
            target="_blank"
            rel="noopener noreferrer"
            className="inline-flex items-center gap-2 px-4 py-2 bg-orange-500 text-white rounded-lg hover:bg-orange-600 transition-colors"
          >
            <WalletIcon size={20} />
            Install MetaMask
          </a>
        </div>
      </div>
    );
  }

  if (!isConnected) {
    return (
      <div className="bg-white rounded-[18px] p-6">
        <div className="text-center">
          <div className="mb-4">
            <WalletIcon size={48} />
          </div>
          <h3 className="text-lg font-bold text-gray-800 mb-2">Connect Wallet</h3>
          <p className="text-gray-600 mb-4">
            Connect your MetaMask wallet to access DeFi features.
          </p>
          
          {error && (
            <div className="mb-4 p-3 bg-red-50 border border-red-200 rounded-lg">
              <p className="text-red-600 text-sm">{error}</p>
            </div>
          )}
          
          <button
            onClick={connect}
            disabled={isConnecting}
            className="inline-flex items-center gap-2 px-6 py-3 bg-blue-500 text-white rounded-lg hover:bg-blue-600 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
          >
            {isConnecting ? (
              <>
                <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin"></div>
                Connecting...
              </>
            ) : (
              <>
                <WalletIcon size={20} />
                Connect MetaMask
              </>
            )}
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="bg-white rounded-[18px] p-6">
      <div className="flex items-start justify-between mb-4">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 bg-gradient-to-br from-orange-400 to-orange-600 rounded-full flex items-center justify-center text-white">
            <WalletIcon size={20} />
          </div>
          <div>
            <h3 className="font-bold text-gray-800">MetaMask Wallet</h3>
            <p className="text-sm text-gray-500">Connected</p>
          </div>
        </div>
        <div className="w-2 h-2 bg-green-500 rounded-full"></div>
      </div>

      <div className="space-y-3 mb-4">
        <div className="flex justify-between items-center">
          <span className="text-sm text-gray-600">Address:</span>
          <span className="text-sm font-mono bg-gray-100 px-2 py-1 rounded">
            {formatAccount(account!)}
          </span>
        </div>
        
        <div className="flex justify-between items-center">
          <span className="text-sm text-gray-600">Network:</span>
          <div className="flex items-center gap-2">
            <span className="text-sm">{getNetworkName(chainId)}</span>
            {!isEthereumMainnet && (
              <span className="text-xs bg-yellow-100 text-yellow-800 px-2 py-1 rounded">
                Not Mainnet
              </span>
            )}
          </div>
        </div>
        
        {balance && (
          <div className="flex justify-between items-center">
            <span className="text-sm text-gray-600">Balance:</span>
            <span className="text-sm font-semibold">
              {parseFloat(balance).toFixed(4)} ETH
            </span>
          </div>
        )}
      </div>

      {!isEthereumMainnet && (
        <div className="mb-4 p-3 bg-yellow-50 border border-yellow-200 rounded-lg">
          <p className="text-yellow-800 text-sm mb-2">
            You're not on Ethereum Mainnet. Some features may not work properly.
          </p>
          <button
            onClick={switchToEthereum}
            className="text-sm bg-yellow-500 text-white px-3 py-1 rounded hover:bg-yellow-600 transition-colors"
          >
            Switch to Mainnet
          </button>
        </div>
      )}

      <div className="flex gap-2">
        <button
          onClick={() => {
            if (account) {
              navigator.clipboard.writeText(account);
            }
          }}
          className="flex-1 px-3 py-2 text-sm bg-gray-100 text-gray-700 rounded-lg hover:bg-gray-200 transition-colors"
        >
          Copy Address
        </button>
        <button
          onClick={disconnect}
          className="flex-1 px-3 py-2 text-sm bg-red-100 text-red-700 rounded-lg hover:bg-red-200 transition-colors"
        >
          Disconnect
        </button>
      </div>
      
      {error && (
        <div className="mt-4 p-3 bg-red-50 border border-red-200 rounded-lg">
          <p className="text-red-600 text-sm">{error}</p>
        </div>
      )}
    </div>
  );
} 