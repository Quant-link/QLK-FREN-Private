// API utility for interacting with the Flask backend

const API_BASE_URL = process.env.NODE_ENV === 'production' ? '' : 'http://localhost:5001';

export interface CryptoPrice {
  name: string;
  current_price: number;
  currency: string;
  success: boolean;
  price_change_24h?: number;
  price_change_7d?: number;
  price_change_30d?: number;
}

export interface MultipleCryptoPrices {
  prices: Record<string, CryptoPrice>;
  success: boolean;
  count: number;
}

export interface NarrationResponse {
  success: boolean;
  file_id?: string;
  expires_in_seconds?: number;
  price_data?: CryptoPrice;
  narration_text?: string;
  error?: string;
}

export interface HistoricalData {
  name: string;
  data: [number, number][]; // [timestamp, price] pairs
  currency: string;
  days: number;
  success: boolean;
}

// Get single cryptocurrency price
export const getCryptoPrice = async (
  crypto: string, 
  currency: string = 'usd',
  with24hChange: boolean = false,
  with7dChange: boolean = false,
  with30dChange: boolean = false
): Promise<CryptoPrice> => {
  const params = new URLSearchParams({
    crypto,
    currency,
    with_24h_change: with24hChange.toString(),
    with_7d_change: with7dChange.toString(),
    with_30d_change: with30dChange.toString(),
  });

  const response = await fetch(`${API_BASE_URL}/api/crypto/price?${params}`);
  if (!response.ok) {
    throw new Error(`HTTP error! status: ${response.status}`);
  }
  return response.json();
};

// Get multiple cryptocurrency prices
export const getMultipleCryptoPrices = async (
  cryptos: string[], 
  currency: string = 'usd',
  with24hChange: boolean = false
): Promise<MultipleCryptoPrices> => {
  const params = new URLSearchParams({
    cryptos: cryptos.join(','),
    currency,
    with_24h_change: with24hChange.toString(),
  });

  const response = await fetch(`${API_BASE_URL}/api/crypto/prices?${params}`);
  if (!response.ok) {
    throw new Error(`HTTP error! status: ${response.status}`);
  }
  return response.json();
};

// Narrate custom text
export const narrateText = async (
  text: string,
  lang: string = 'en',
  slow: boolean = false,
  returnAudio: boolean = false
): Promise<NarrationResponse> => {
  const response = await fetch(`${API_BASE_URL}/api/narrator/text`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      text,
      lang,
      slow,
      return_audio: returnAudio,
    }),
  });

  if (!response.ok) {
    throw new Error(`HTTP error! status: ${response.status}`);
  }
  return response.json();
};

// Narrate cryptocurrency price
export const narrateCryptoPrice = async (
  crypto: string,
  currency: string = 'usd',
  with24hChange: boolean = false,
  with7dChange: boolean = false,
  with30dChange: boolean = false,
  lang: string = 'en',
  slow: boolean = false,
  returnAudio: boolean = false
): Promise<NarrationResponse> => {
  const response = await fetch(`${API_BASE_URL}/api/narrator/crypto`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      crypto,
      currency,
      with_24h_change: with24hChange,
      with_7d_change: with7dChange,
      with_30d_change: with30dChange,
      lang,
      slow,
      return_audio: returnAudio,
    }),
  });

  if (!response.ok) {
    throw new Error(`HTTP error! status: ${response.status}`);
  }
  return response.json();
};

// Get audio file by ID
export const getAudioFile = (fileId: string): string => {
  return `${API_BASE_URL}/api/narrator/audio/${fileId}`;
};

// Health check
export const healthCheck = async (): Promise<{ status: string; version: string }> => {
  const response = await fetch(`${API_BASE_URL}/api/health`);
  if (!response.ok) {
    throw new Error(`HTTP error! status: ${response.status}`);
  }
  return response.json();
};

// Get historical price data
export const getCryptoHistoricalData = async (
  crypto: string,
  currency: string = 'usd',
  days: number = 7
): Promise<HistoricalData> => {
  const params = new URLSearchParams({
    crypto,
    currency,
    days: days.toString(),
  });

  const response = await fetch(`${API_BASE_URL}/api/crypto/historical?${params}`);
  if (!response.ok) {
    throw new Error(`HTTP error! status: ${response.status}`);
  }
  return response.json();
}; 