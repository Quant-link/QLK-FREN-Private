import { useState, useEffect } from 'react';
import { ethers } from 'ethers';

interface MetaMaskState {
  isConnected: boolean;
  account: string | null;
  isConnecting: boolean;
  error: string | null;
  chainId: string | null;
  balance: string | null;
}

export function useMetaMask() {
  const [state, setState] = useState<MetaMaskState>({
    isConnected: false,
    account: null,
    isConnecting: false,
    error: null,
    chainId: null,
    balance: null,
  });

  // Check if MetaMask is installed
  const isMetaMaskInstalled = () => {
    return typeof window !== 'undefined' && window.ethereum && window.ethereum.isMetaMask;
  };

  // Get balance for connected account
  const getBalance = async (account: string) => {
    try {
      if (window.ethereum) {
        const provider = new ethers.BrowserProvider(window.ethereum);
        const balance = await provider.getBalance(account);
        return ethers.formatEther(balance);
      }
      return null;
    } catch (error) {
      console.error('Error getting balance:', error);
      return null;
    }
  };

  // Connect to MetaMask
  const connect = async () => {
    if (!isMetaMaskInstalled()) {
      setState(prev => ({ ...prev, error: 'MetaMask is not installed' }));
      return;
    }

    setState(prev => ({ ...prev, isConnecting: true, error: null }));

    try {
      const accounts = await window.ethereum!.request({
        method: 'eth_requestAccounts',
      });

      const chainId = await window.ethereum!.request({
        method: 'eth_chainId',
      });

      if (accounts.length > 0) {
        const account = accounts[0];
        const balance = await getBalance(account);
        
        setState(prev => ({
          ...prev,
          isConnected: true,
          account,
          chainId,
          balance,
          isConnecting: false,
          error: null,
        }));
      }
    } catch (error: any) {
      setState(prev => ({
        ...prev,
        isConnecting: false,
        error: error.message || 'Failed to connect to MetaMask',
      }));
    }
  };

  // Disconnect from MetaMask
  const disconnect = () => {
    setState({
      isConnected: false,
      account: null,
      isConnecting: false,
      error: null,
      chainId: null,
      balance: null,
    });
  };

  // Switch to Ethereum Mainnet
  const switchToEthereum = async () => {
    try {
      await window.ethereum!.request({
        method: 'wallet_switchEthereumChain',
        params: [{ chainId: '0x1' }], // Ethereum Mainnet
      });
    } catch (error: any) {
      setState(prev => ({ ...prev, error: error.message }));
    }
  };

  // Format account address for display
  const formatAccount = (account: string) => {
    return `${account.slice(0, 6)}...${account.slice(-4)}`;
  };

  // Check connection on mount and when accounts change
  useEffect(() => {
    const checkConnection = async () => {
      if (!isMetaMaskInstalled()) return;

      try {
        const accounts = await window.ethereum!.request({
          method: 'eth_accounts',
        });

        const chainId = await window.ethereum!.request({
          method: 'eth_chainId',
        });

        if (accounts.length > 0) {
          const account = accounts[0];
          const balance = await getBalance(account);
          
          setState(prev => ({
            ...prev,
            isConnected: true,
            account,
            chainId,
            balance,
          }));
        }
      } catch (error) {
        console.error('Error checking connection:', error);
      }
    };

    checkConnection();

    if (window.ethereum) {
      // Listen for account changes
      window.ethereum.on('accountsChanged', (accounts: string[]) => {
        if (accounts.length === 0) {
          disconnect();
        } else {
          const account = accounts[0];
          getBalance(account).then(balance => {
            setState(prev => ({ ...prev, account, balance }));
          });
        }
      });

      // Listen for chain changes
      window.ethereum.on('chainChanged', (chainId: string) => {
        setState(prev => ({ ...prev, chainId }));
      });
    }

    return () => {
      if (window.ethereum) {
        window.ethereum.removeAllListeners('accountsChanged');
        window.ethereum.removeAllListeners('chainChanged');
      }
    };
  }, []);

  return {
    ...state,
    connect,
    disconnect,
    switchToEthereum,
    formatAccount,
    isMetaMaskInstalled: isMetaMaskInstalled(),
  };
} 