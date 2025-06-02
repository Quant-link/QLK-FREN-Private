import { useState, useEffect } from "react";
import {
  getCryptoPrice,
  getMultipleCryptoPrices,
  narrateCryptoPrice,
  getAudioFile,
  healthCheck,
  type CryptoPrice,
} from "./api/cryptoApi";
import { getCryptoIcon, getCryptoDisplayName } from "./utils/cryptoIcons";
import { CryptoChart } from "./components/CryptoChart";
import { MetaMaskWallet } from "./components/MetaMaskWallet";
import {
  WalletIcon,
  SettingsIcon,
  HomeIcon,
  TrendingUpIcon,
  VolumeIcon,
  BarChartIcon,
  HelpIcon,
  AnalyticsIcon,
} from "./components/Icons";

interface SystemStatus {
  status: string;
  version: string;
}

function App() {
  // State management
  const [systemStatus, setSystemStatus] = useState<SystemStatus | null>(null);
  const [selectedCrypto, setSelectedCrypto] = useState("bitcoin");
  const [selectedCurrency, setSelectedCurrency] = useState("usd");
  const [priceChangeOptions, setPriceChangeOptions] = useState({
    change24h: false,
    change7d: false,
    change30d: false,
  });
  const [currentPrice, setCurrentPrice] = useState<CryptoPrice | null>(null);
  const [livePrices, setLivePrices] = useState<Record<string, CryptoPrice>>({});
  const [isLoading, setIsLoading] = useState(false);
  const [audioUrl, setAudioUrl] = useState<string | null>(null);
  const [isPlaying, setIsPlaying] = useState(false);
  const [activeSection, setActiveSection] = useState("home");
  const [chartDays, setChartDays] = useState(7);
  const [showWallet, setShowWallet] = useState(false);

  // Popular cryptocurrencies for live feed
  const popularCryptos = ["bitcoin", "ethereum", "solana", "cardano", "polkadot", "chainlink"];

  // Check system health on mount
  useEffect(() => {
    const checkHealth = async () => {
      try {
        const health = await healthCheck();
        setSystemStatus(health);
      } catch (error) {
        console.error("Health check failed:", error);
        setSystemStatus({ status: "unhealthy", version: "unknown" });
      }
    };

    checkHealth();
  }, []);

  // Fetch live prices every 30 seconds
  useEffect(() => {
    const fetchLivePrices = async () => {
      try {
        const prices = await getMultipleCryptoPrices(popularCryptos, "usd", true);
        if (prices.success) {
          setLivePrices(prices.prices);
        }
      } catch (error) {
        console.error("Failed to fetch live prices:", error);
      }
    };

    // Initial fetch
    fetchLivePrices();

    // Set up interval for live updates
    const interval = setInterval(fetchLivePrices, 30000);

    return () => clearInterval(interval);
  }, []);

  // Fetch single cryptocurrency price
  const handleFetchPrice = async () => {
    setIsLoading(true);
    try {
      const price = await getCryptoPrice(
        selectedCrypto,
        selectedCurrency,
        priceChangeOptions.change24h,
        priceChangeOptions.change7d,
        priceChangeOptions.change30d
      );
      setCurrentPrice(price);
    } catch (error) {
      console.error("Failed to fetch price:", error);
      alert("Failed to fetch price. Please try again.");
    }
    setIsLoading(false);
  };

  // Narrate cryptocurrency price
  const handleNarratePrice = async () => {
    if (!currentPrice) {
      alert("Please fetch a price first!");
      return;
    }

    setIsLoading(true);
    try {
      const narration = await narrateCryptoPrice(
        selectedCrypto,
        selectedCurrency,
        priceChangeOptions.change24h,
        priceChangeOptions.change7d,
        priceChangeOptions.change30d
      );

      if (narration.success && narration.file_id) {
        const audioFileUrl = getAudioFile(narration.file_id);
        setAudioUrl(audioFileUrl);
        
        // Auto-play the audio
        const audio = new Audio(audioFileUrl);
        audio.play();
        setIsPlaying(true);
        
        audio.onended = () => {
          setIsPlaying(false);
        };
      } else {
        alert("Failed to generate narration. Please try again.");
      }
    } catch (error) {
      console.error("Failed to generate narration:", error);
      alert("Failed to generate narration. Please try again.");
    }
    setIsLoading(false);
  };

  // Play audio again
  const handlePlayAudio = () => {
    if (audioUrl && !isPlaying) {
      const audio = new Audio(audioUrl);
      audio.play();
      setIsPlaying(true);
      audio.onended = () => {
        setIsPlaying(false);
      };
    }
  };

  // Format price display
  const formatPrice = (price: number) => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD',
      minimumFractionDigits: 2,
      maximumFractionDigits: 6,
    }).format(price);
  };

  // Format percentage change
  const formatPercentChange = (change: number) => {
    const sign = change >= 0 ? '+' : '';
    return `${sign}${change.toFixed(2)}%`;
  };

  // Navigation handlers
  const handleNavigation = (section: string) => {
    setActiveSection(section);
    // Here you can add navigation logic based on the section
    switch (section) {
      case "home":
        console.log("Navigate to Home");
        break;
      case "trends":
        console.log("Navigate to Trends");
        break;
      case "voice":
        console.log("Navigate to Voice Controls");
        break;
      case "analytics":
        console.log("Navigate to Analytics");
        break;
      case "help":
        console.log("Show Help");
        break;
      case "settings":
        console.log("Open Settings");
        break;
      default:
        break;
    }
  };

  // Header button handlers
  const handleWalletClick = () => {
    setShowWallet(!showWallet);
  };

  const handleAnalyticsClick = () => {
    handleNavigation("analytics");
  };

  const handleSettingsClick = () => {
    handleNavigation("settings");
  };

  return (
    <>
      <div className="bg-linear-to-b from-[#f1f1f5] to-[#c9d6e3] w-screen h-screen absolute z-[-1]"></div>
      <div className="overflow-y-auto h-screen">
        <div className="text-[#151F24] flex flex-col h-full">
          <header className="shrink-0 fixed top-0 left-0 right-0 z-50 bg-white/80 backdrop-blur-sm">
            <div className="container mx-auto flex items-center justify-between py-8 ">
              <div>
                <img src="/logo.svg" alt="Quantlink" />
              </div>
              <div className="flex gap-4">
                <button 
                  className={`w-[56px] h-[56px] rounded-full ${showWallet ? 'bg-blue-500 text-white' : 'bg-white hover:bg-gray-50'} flex items-center justify-center transition-colors`}
                  onClick={handleWalletClick}
                  title="Wallet"
                >
                  <WalletIcon size={24} />
                </button>
                <button 
                  className="w-[56px] h-[56px] rounded-full bg-white flex items-center justify-center hover:bg-gray-50 transition-colors"
                  onClick={handleAnalyticsClick}
                  title="Analytics"
                >
                  <AnalyticsIcon size={24} />
                </button>
                <button 
                  className="w-[56px] h-[56px] rounded-full bg-white flex items-center justify-center hover:bg-gray-50 transition-colors"
                  onClick={handleSettingsClick}
                  title="Settings"
                >
                  <SettingsIcon size={24} />
                </button>
              </div>
            </div>
          </header>

          {/* MetaMask Wallet Overlay */}
          {showWallet && (
            <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
              <div className="max-w-md w-full">
                <div className="mb-4 flex justify-end">
                  <button
                    onClick={() => setShowWallet(false)}
                    className="w-8 h-8 bg-white rounded-full flex items-center justify-center hover:bg-gray-100 transition-colors"
                  >
                    ×
                  </button>
                </div>
                <MetaMaskWallet />
              </div>
            </div>
          )}

          <div className="container mx-auto grid grid-cols-[64px_1fr] gap-8 h-full grow mt-[120px]">
            <aside className="flex flex-col justify-between h-full sticky top-[120px] max-h-[calc(100vh-192px)]">
              <div className="flex flex-col gap-4">
                <button 
                  className={`w-[64px] h-[64px] rounded-[18px] ${activeSection === 'home' ? 'bg-blue-500 text-white' : 'bg-white hover:bg-gray-50'} transition-colors flex items-center justify-center`}
                  onClick={() => handleNavigation('home')}
                  title="Home"
                >
                  <HomeIcon size={28} />
                </button>
                <button 
                  className={`w-[64px] h-[64px] rounded-[18px] ${activeSection === 'trends' ? 'bg-blue-500 text-white' : 'bg-white hover:bg-gray-50'} transition-colors flex items-center justify-center`}
                  onClick={() => handleNavigation('trends')}
                  title="Market Trends"
                >
                  <TrendingUpIcon size={28} />
                </button>
                <button 
                  className={`w-[64px] h-[64px] rounded-[18px] ${activeSection === 'voice' ? 'bg-blue-500 text-white' : 'bg-white hover:bg-gray-50'} transition-colors flex items-center justify-center`}
                  onClick={() => handleNavigation('voice')}
                  title="Voice Controls"
                >
                  <VolumeIcon size={28} />
                </button>
                <button 
                  className={`w-[64px] h-[64px] rounded-[18px] ${activeSection === 'analytics' ? 'bg-blue-500 text-white' : 'bg-white hover:bg-gray-50'} transition-colors flex items-center justify-center`}
                  onClick={() => handleNavigation('analytics')}
                  title="Analytics Dashboard"
                >
                  <BarChartIcon size={28} />
                </button>
              </div>
              <div className="flex flex-col gap-4">
                <button 
                  className={`w-[64px] h-[64px] rounded-[18px] ${activeSection === 'help' ? 'bg-blue-500 text-white' : 'bg-white hover:bg-gray-50'} transition-colors flex items-center justify-center`}
                  onClick={() => handleNavigation('help')}
                  title="Help & Support"
                >
                  <HelpIcon size={28} />
                </button>
                <button 
                  className={`w-[64px] h-[64px] rounded-[18px] ${activeSection === 'settings' ? 'bg-blue-500 text-white' : 'bg-white hover:bg-gray-50'} transition-colors flex items-center justify-center`}
                  onClick={() => handleNavigation('settings')}
                  title="Settings"
                >
                  <SettingsIcon size={28} />
                </button>
              </div>
            </aside>
            <main>
              <div className="flex items-center justify-between">
                <h1 className="text-[24px] font-[600]">
                  FREN |{" "}
                  <span className="text-[#899093]">
                    AI-Powered Crypto Narrator
                  </span>
                </h1>

                <div className="px-[24px] py-[12px] bg-[#70B29A26] rounded-full flex items-center gap-2">
                  <div 
                    className={`w-3 h-3 rounded-full ${
                      systemStatus?.status === 'healthy' ? 'bg-[#70B29A]' : 'bg-red-500'
                    }`}
                  ></div>
                  <div className="text-[#70B29A] text-[15px] font-[600] leading-none mt-[2px]">
                    {systemStatus?.status === 'healthy' ? 'System Active' : 'System Offline'}
                  </div>
                </div>
              </div>

              <div className="grid grid-cols-2 mt-[48px] gap-[24px]">
                <div className="bg-white rounded-[18px] px-[24px] py-[20px] font-space-grotesk">
                  <div className="flex items-center gap-[10px] mb-4">
                    <svg
                      width="25"
                      height="25"
                      viewBox="0 0 25 25"
                      fill="none"
                      xmlns="http://www.w3.org/2000/svg"
                    >
                      <path
                        d="M3.58008 21.2371L3.58008 17.2371H21.5801V21.2371H3.58008Z"
                        stroke="#323232"
                        strokeWidth="1.5"
                        strokeLinecap="round"
                        strokeLinejoin="round"
                      />
                      <path
                        d="M3.58008 14.2371L3.58008 10.2371H15.8961V14.2371H3.58008Z"
                        stroke="#323232"
                        strokeWidth="1.5"
                        strokeLinecap="round"
                        strokeLinejoin="round"
                      />
                      <path
                        d="M3.58008 7.23706L3.58008 3.23706L10.2121 3.23706V7.23706H3.58008Z"
                        stroke="#323232"
                        strokeWidth="1.5"
                        strokeLinecap="round"
                        strokeLinejoin="round"
                      />
                    </svg>
                    <h2 className="font-[700]">Cryptocurrency Narrator</h2>
                  </div>

                  <div className="space-y-4">
                    <div>
                      <div className="text-[10px] font-[700] text-[#9D9D9E] mb-2">
                        Select Cryptocurrency
                      </div>
                      <select 
                        className="bg-[#4DACE13B] py-[12px] px-[28px] rounded-[18px] w-full font-[700] border-none outline-none"
                        value={selectedCrypto}
                        onChange={(e) => setSelectedCrypto(e.target.value)}
                      >
                        <option value="bitcoin">Bitcoin (BTC)</option>
                        <option value="ethereum">Ethereum (ETH)</option>
                        <option value="solana">Solana (SOL)</option>
                        <option value="cardano">Cardano (ADA)</option>
                        <option value="polkadot">Polkadot (DOT)</option>
                        <option value="chainlink">Chainlink (LINK)</option>
                      </select>
                    </div>

                    <div>
                      <div className="text-[10px] font-[700] text-[#9D9D9E] mb-2">
                        Currency
                      </div>
                      <select 
                        className="bg-[#4DACE13B] py-[12px] px-[28px] rounded-[18px] w-full font-[700] border-none outline-none"
                        value={selectedCurrency}
                        onChange={(e) => setSelectedCurrency(e.target.value)}
                      >
                        <option value="usd">US Dollar (USD)</option>
                        <option value="eur">Euro (EUR)</option>
                        <option value="gbp">British Pound (GBP)</option>
                      </select>
                    </div>

                    <div>
                      <div className="text-[10px] font-[700] text-[#9D9D9E] mb-2">
                        Price Change Options
                      </div>
                      <div className="flex gap-4">
                        <div className="bg-gray-100 rounded-[18px] px-[16px] py-[12px] flex flex-col gap-4">
                          <label className="block">
                            <input 
                              type="checkbox" 
                              checked={priceChangeOptions.change24h}
                              onChange={(e) => setPriceChangeOptions(prev => ({ 
                                ...prev, 
                                change24h: e.target.checked 
                              }))}
                            />
                            <span className="ml-2 text-[14px] font-[700]">
                              24h Price change
                            </span>
                          </label>
                          <label className="block">
                            <input 
                              type="checkbox" 
                              checked={priceChangeOptions.change7d}
                              onChange={(e) => setPriceChangeOptions(prev => ({ 
                                ...prev, 
                                change7d: e.target.checked 
                              }))}
                            />
                            <span className="ml-2 text-[14px] font-[700]">
                              7d Price change
                            </span>
                          </label>
                          <label className="block">
                            <input 
                              type="checkbox" 
                              checked={priceChangeOptions.change30d}
                              onChange={(e) => setPriceChangeOptions(prev => ({ 
                                ...prev, 
                                change30d: e.target.checked 
                              }))}
                            />
                            <span className="ml-2 text-[14px] font-[700]">
                              30d Price change
                            </span>
                          </label>
                        </div>

                        <div className="flex flex-col justify-between">
                          <button 
                            className="w-[140px] h-[60px] border border-gray-300 rounded-[18px] hover:bg-gray-50 transition-colors font-[600] disabled:opacity-50 disabled:cursor-not-allowed"
                            onClick={handleFetchPrice}
                            disabled={isLoading}
                          >
                            {isLoading ? "Loading..." : "Fetch Price"}
                          </button>
                          <button 
                            className="w-[140px] h-[60px] border border-gray-300 rounded-[18px] hover:bg-gray-50 transition-colors font-[600] disabled:opacity-50 disabled:cursor-not-allowed"
                            onClick={handleNarratePrice}
                            disabled={isLoading || !currentPrice}
                          >
                            {isLoading ? "Loading..." : "Narrate Price"}
                          </button>
                        </div>
                      </div>
                    </div>

                    {/* Current Price Display */}
                    {currentPrice && (
                      <div className="mt-4 p-4 bg-blue-50 rounded-lg">
                        <h3 className="font-bold text-lg">{currentPrice.name}</h3>
                        <p className="text-2xl font-bold text-blue-600">
                          {formatPrice(currentPrice.current_price)}
                        </p>
                        {currentPrice.price_change_24h !== undefined && (
                          <p className={`text-sm ${currentPrice.price_change_24h >= 0 ? 'text-green-600' : 'text-red-600'}`}>
                            24h: {formatPercentChange(currentPrice.price_change_24h)}
                          </p>
                        )}
                        {currentPrice.price_change_7d !== undefined && (
                          <p className={`text-sm ${currentPrice.price_change_7d >= 0 ? 'text-green-600' : 'text-red-600'}`}>
                            7d: {formatPercentChange(currentPrice.price_change_7d)}
                          </p>
                        )}
                        {currentPrice.price_change_30d !== undefined && (
                          <p className={`text-sm ${currentPrice.price_change_30d >= 0 ? 'text-green-600' : 'text-red-600'}`}>
                            30d: {formatPercentChange(currentPrice.price_change_30d)}
                          </p>
                        )}
                        
                        {/* Audio Control */}
                        {audioUrl && (
                          <div className="mt-4 p-3 bg-gradient-to-r from-blue-50 to-indigo-50 rounded-lg border border-blue-200">
                            <div className="flex items-center justify-between">
                              <div className="flex items-center gap-2">
                                <div className="w-2 h-2 bg-green-500 rounded-full animate-pulse"></div>
                                <span className="text-sm font-medium text-gray-700">Audio Ready</span>
                              </div>
                              <button
                                className="px-4 py-2 bg-blue-500 text-white rounded-lg hover:bg-blue-600 transition-colors disabled:opacity-50 disabled:cursor-not-allowed flex items-center gap-2 text-sm font-medium"
                                onClick={handlePlayAudio}
                                disabled={isPlaying}
                              >
                                <VolumeIcon size={16} />
                                {isPlaying ? "Playing..." : "Play Audio"}
                              </button>
                            </div>
                          </div>
                        )}
                      </div>
                    )}
                  </div>
                </div>

                <div className="self-end">
                  <div className="font-[600] mb-[24px]">
                    <div className="text-[25px] leading-8">Live</div>
                    <div className="text-[40px] leading-8">Price Feed</div>
                  </div>
                  <div className="grid grid-cols-2 grid-rows-3 gap-[12px]">
                    {popularCryptos.map((crypto) => {
                      const priceData = livePrices[crypto];
                      return (
                        <div key={crypto} className="flex items-center gap-6 bg-white rounded-[18px] px-[24px] py-[20px] font-space-grotesk">
                          <div>
                            {getCryptoIcon(crypto)}
                          </div>
                          <div className="flex flex-col">
                            <div className="font-bold">{getCryptoDisplayName(crypto)}</div>
                            <div className="text-sm text-gray-500">Via CoinGecko</div>
                          </div>
                          <div className="flex flex-col">
                            <div className="font-bold">
                              {priceData ? formatPrice(priceData.current_price) : "Loading..."}
                            </div>
                            {priceData?.price_change_24h !== undefined && (
                              <div className={`text-sm ${priceData.price_change_24h >= 0 ? 'text-green-600' : 'text-red-600'}`}>
                                {formatPercentChange(priceData.price_change_24h)}
                              </div>
                            )}
                          </div>
                        </div>
                      );
                    })}
                  </div>
                </div>
              </div>

              {/* Price Chart Section */}
              <div className="mt-[48px]">
                <div className="flex justify-between items-center mb-6">
                  <div className="flex flex-col">
                    <div className="text-[24px] font-[600]">Price History</div>
                    <div className="text-[18px] text-gray-600">
                      {selectedCrypto.charAt(0).toUpperCase() + selectedCrypto.slice(1)} - Last {chartDays} days
                    </div>
                  </div>
                  <div className="flex gap-2">
                    {[1, 7, 30, 90].map((days) => (
                      <button
                        key={days}
                        onClick={() => setChartDays(days)}
                        className={`px-4 py-2 rounded-lg text-sm font-medium transition-colors ${
                          chartDays === days
                            ? 'bg-blue-500 text-white'
                            : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                        }`}
                      >
                        {days === 1 ? '24H' : `${days}D`}
                      </button>
                    ))}
                  </div>
                </div>
                <CryptoChart 
                  crypto={selectedCrypto} 
                  currency={selectedCurrency} 
                  days={chartDays}
                  className="mt-[24px]"
                />
              </div>
            </main>
          </div>
        </div>
      </div>
    </>
  );
}

export default App;
