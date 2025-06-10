import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';
import { useEffect, useState } from 'react';
import { getCryptoHistoricalData, type HistoricalData } from '../api/cryptoApi';

interface CryptoChartProps {
  crypto: string;
  currency: string;
  days: number;
  className?: string;
}

interface ChartDataPoint {
  timestamp: number;
  price: number;
  date: string;
  formattedPrice: string;
}

export function CryptoChart({ crypto, currency, days, className = '' }: CryptoChartProps) {
  const [data, setData] = useState<ChartDataPoint[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchData = async () => {
      setLoading(true);
      setError(null);
      
      try {
        const result: HistoricalData = await getCryptoHistoricalData(crypto, currency, days);
        
        if (result.success) {
          const chartData: ChartDataPoint[] = result.data.map(([timestamp, price]) => ({
            timestamp,
            price,
            date: new Date(timestamp).toLocaleDateString(),
            formattedPrice: new Intl.NumberFormat('en-US', {
              style: 'currency',
              currency: currency.toUpperCase(),
              minimumFractionDigits: 2,
              maximumFractionDigits: 6,
            }).format(price),
          }));
          
          setData(chartData);
        } else {
          setError('Failed to fetch historical data');
        }
      } catch (err) {
        setError(err instanceof Error ? err.message : 'An error occurred');
      } finally {
        setLoading(false);
      }
    };

    fetchData();
  }, [crypto, currency, days]);

  const formatPrice = (value: number) => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: currency.toUpperCase(),
      minimumFractionDigits: 2,
      maximumFractionDigits: value < 1 ? 6 : 2,
    }).format(value);
  };

  const formatDate = (timestamp: number) => {
    const date = new Date(timestamp);
    if (days <= 1) {
      return date.toLocaleTimeString('en-US', { 
        hour: '2-digit', 
        minute: '2-digit' 
      });
    } else if (days <= 7) {
      return date.toLocaleDateString('en-US', { 
        month: 'short', 
        day: 'numeric',
        hour: '2-digit'
      });
    } else {
      return date.toLocaleDateString('en-US', { 
        month: 'short', 
        day: 'numeric' 
      });
    }
  };

  // Calculate price change
  const priceChange = data.length >= 2 ? 
    ((data[data.length - 1]?.price - data[0]?.price) / data[0]?.price) * 100 : 0;
  
  const isPositive = priceChange >= 0;

  if (loading) {
    return (
      <div className={`bg-white rounded-[18px] p-6 ${className}`}>
        <div className="flex items-center justify-center h-[300px]">
          <div className="flex items-center gap-3">
            <div className="w-6 h-6 border-2 border-[#4cafd8] border-t-transparent rounded-full animate-spin"></div>
            <span className="text-gray-600">Loading chart data...</span>
          </div>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className={`bg-white rounded-[18px] p-6 ${className}`}>
        <div className="flex items-center justify-center h-[300px]">
          <div className="text-center">
            <div className="text-red-500 text-lg font-semibold mb-2">Failed to load chart</div>
            <div className="text-gray-500 text-sm">{error}</div>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className={`bg-white rounded-[18px] p-6 ${className}`}>
      <div className="flex items-center justify-between mb-6">
        <div>
          <h3 className="text-xl font-bold text-gray-800">
            {crypto.charAt(0).toUpperCase() + crypto.slice(1)} Price Chart
          </h3>
          <p className="text-sm text-gray-500">
            Last {days} {days === 1 ? 'day' : 'days'} • {currency.toUpperCase()}
          </p>
        </div>
        <div className="text-right">
          <div className="text-2xl font-bold text-gray-800">
            {data[data.length - 1]?.formattedPrice || 'N/A'}
          </div>
          <div className={`text-sm font-semibold ${
            isPositive ? 'text-green-600' : 'text-red-600'
          }`}>
            {isPositive ? '+' : ''}{priceChange.toFixed(2)}%
          </div>
        </div>
      </div>

      <div className="h-[300px]">
        <ResponsiveContainer width="100%" height="100%">
          <LineChart data={data} margin={{ top: 5, right: 30, left: 20, bottom: 5 }}>
            <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
            <XAxis 
              dataKey="timestamp"
              tickFormatter={formatDate}
              stroke="#666"
              fontSize={12}
              axisLine={false}
              tickLine={false}
            />
            <YAxis 
              tickFormatter={formatPrice}
              stroke="#666"
              fontSize={12}
              axisLine={false}
              tickLine={false}
              domain={['dataMin - dataMin * 0.01', 'dataMax + dataMax * 0.01']}
            />
            <Tooltip 
              formatter={(value: number) => [formatPrice(value), 'Price']}
              labelFormatter={(timestamp: number) => {
                const date = new Date(timestamp);
                return date.toLocaleString('en-US', {
                  year: 'numeric',
                  month: 'short',
                  day: 'numeric',
                  hour: '2-digit',
                  minute: '2-digit',
                });
              }}
              contentStyle={{
                backgroundColor: '#fff',
                border: '1px solid #e0e0e0',
                borderRadius: '8px',
                boxShadow: '0 4px 6px -1px rgba(0, 0, 0, 0.1)',
              }}
            />
            <Line 
              type="monotone" 
              dataKey="price" 
              stroke={isPositive ? '#10b981' : '#ef4444'}
              strokeWidth={2}
              dot={false}
              activeDot={{ 
                r: 4, 
                fill: isPositive ? '#10b981' : '#ef4444',
                stroke: '#fff',
                strokeWidth: 2 
              }}
            />
          </LineChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
} 