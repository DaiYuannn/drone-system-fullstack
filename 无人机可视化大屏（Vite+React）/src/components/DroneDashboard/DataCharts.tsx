import { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { 
  LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, 
  AreaChart, Area, BarChart, Bar, Legend
} from 'recharts';
import { generateHistoricalData } from '@/mocks/droneData';
import { HistoricalData } from '@/types/drone';
import { useTheme } from '@/hooks/useTheme';

export const DataCharts: React.FC = () => {
  const { isDark } = useTheme();
  const [historicalData, setHistoricalData] = useState<HistoricalData[]>([]);
  const [timeRange, setTimeRange] = useState<'24h' | '7d' | '30d'>('24h');
  
  // 初始化数据
  useEffect(() => {
    setHistoricalData(generateHistoricalData());
  }, []);
  
  // 格式化时间显示
  const formatTime = (timestamp: string) => {
    const date = new Date(timestamp);
    return date.getHours().toString().padStart(2, '0') + ':00';
  };
  
  // 自定义提示框
  const CustomTooltip = ({ active, payload, label }: any) => {
    if (active && payload && payload.length) {
      return (
        <div className={`p-3 rounded-lg shadow-lg ${isDark ? 'bg-gray-800 border border-gray-700' : 'bg-white border border-gray-200'}`}>
          <p className="font-medium mb-2">{formatTime(label)}</p>
          {payload.map((entry: any, index: number) => (
            <p key={index} className="text-sm" style={{ color: entry.color }}>
              {entry.name}: {entry.value} {entry.unit || ''}
            </p>
          ))}
        </div>
      );
    }
    return null;
  };
  
  // 获取图表颜色
  const getChartColors = () => {
    return {
      primary: isDark ? '#3b82f6' : '#2563eb',
      secondary: isDark ? '#10b981' : '#059669',
      tertiary: isDark ? '#f59e0b' : '#d97706',
      quaternary: isDark ? '#8b5cf6' : '#7c3aed',
      grid: isDark ? 'rgba(255, 255, 255, 0.1)' : 'rgba(0, 0, 0, 0.1)',
      text: isDark ? 'rgba(255, 255, 255, 0.7)' : 'rgba(0, 0, 0, 0.5)',
    };
  };
  
  const chartColors = getChartColors();
  
  // 飞行轨迹数据 (简化为高度和速度)
  const flightPathData = historicalData.map(item => ({
    time: item.timestamp,
    altitude: item.altitude,
    speed: item.speed
  }));
  
  // 电池使用趋势数据
  const batteryData = historicalData.map(item => ({
    time: item.timestamp,
    batteryLevel: item.batteryLevel
  }));
  
  // 环境数据
  const environmentData = historicalData.map(item => ({
    time: item.timestamp,
    temperature: item.temperature,
    humidity: item.humidity
  }));
  
  return (
    <div className={`${isDark ? 'bg-gray-800' : 'bg-white'} border ${isDark ? 'border-gray-700' : 'border-gray-200'} rounded-xl p-5 shadow-lg h-full flex flex-col`}>
      <div className="flex justify-between items-center mb-6">
        <h3 className="text-lg font-semibold">数据图表分析</h3>
        <div className="flex space-x-2">
          {(['24h', '7d', '30d'] as const).map((range) => (
            <button
              key={range}
              onClick={() => setTimeRange(range)}
              className={`px-3 py-1 rounded-md text-sm ${
                timeRange === range
                  ? (isDark ? 'bg-blue-900/50 text-blue-400' : 'bg-blue-100 text-blue-700')
                  : (isDark ? 'bg-gray-700 hover:bg-gray-600' : 'bg-gray-100 hover:bg-gray-200')
              } transition-colors`}
            >
              {range}
            </button>
          ))}
        </div>
      </div>
      
      <div className="flex-1 grid grid-cols-1 lg:grid-cols-2 gap-6 overflow-auto">
        {/* 飞行轨迹图表 */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5, delay: 0.1 }}
          className={`p-4 rounded-lg ${isDark ? 'bg-gray-900/50' : 'bg-gray-50'} border ${isDark ? 'border-gray-700' : 'border-gray-200'}`}
        >
          <h4 className="font-medium mb-4">飞行轨迹历史</h4>
          <div className="h-64">
            <ResponsiveContainer width="100%" height="100%">
              <LineChart data={flightPathData}>
                <CartesianGrid strokeDasharray="3 3" stroke={chartColors.grid} />
                <XAxis 
                  dataKey="time" 
                  tickFormatter={formatTime} 
                  stroke={chartColors.text}
                  tick={{ fontSize: 12 }}
                  interval={4}
                />
                <YAxis yAxisId="left" stroke={chartColors.primary} />
                <YAxis yAxisId="right" orientation="right" stroke={chartColors.secondary} />
                <Tooltip content={<CustomTooltip />} />
                <Legend />
                <Line 
                  yAxisId="left"
                  type="monotone" 
                  dataKey="altitude" 
                  name="高度" 
                  unit="m"
                  stroke={chartColors.primary} 
                  strokeWidth={2}
                  dot={false}
                  activeDot={{ r: 6 }}
                />
                <Line 
                  yAxisId="right"
                  type="monotone" 
                  dataKey="speed" 
                  name="速度" 
                  unit="m/s"
                  stroke={chartColors.secondary} 
                  strokeWidth={2}
                  dot={false}
                  activeDot={{ r: 6 }}
                />
              </LineChart>
            </ResponsiveContainer>
          </div>
        </motion.div>
        
        {/* 电池使用趋势图表 */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5, delay: 0.2 }}
          className={`p-4 rounded-lg ${isDark ? 'bg-gray-900/50' : 'bg-gray-50'} border ${isDark ? 'border-gray-700' : 'border-gray-200'}`}
        >
          <h4 className="font-medium mb-4">电池使用趋势</h4>
          <div className="h-64">
            <ResponsiveContainer width="100%" height="100%">
              <AreaChart data={batteryData}>
                <defs>
                  <linearGradient id="batteryGradient" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor={chartColors.tertiary} stopOpacity={0.8}/>
                    <stop offset="95%" stopColor={chartColors.tertiary} stopOpacity={0}/>
                  </linearGradient>
                </defs>
                <CartesianGrid strokeDasharray="3 3" stroke={chartColors.grid} />
                <XAxis 
                  dataKey="time" 
                  tickFormatter={formatTime} 
                  stroke={chartColors.text}
                  tick={{ fontSize: 12 }}
                  interval={4}
                />
                <YAxis domain={[0, 100]} stroke={chartColors.tertiary} />
                <Tooltip content={<CustomTooltip />} />
                <Area 
                  type="monotone" 
                  dataKey="batteryLevel" 
                  name="电池电量" 
                  unit="%"
                  stroke={chartColors.tertiary} 
                  fillOpacity={1}
                  fill="url(#batteryGradient)"
                />
              </AreaChart>
            </ResponsiveContainer>
          </div>
        </motion.div>
        
        {/* 环境数据图表 */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5, delay: 0.3 }}
          className={`p-4 rounded-lg ${isDark ? 'bg-gray-900/50' : 'bg-gray-50'} border ${isDark ? 'border-gray-700' : 'border-gray-200'} lg:col-span-2`}
        >
          <h4 className="font-medium mb-4">环境数据变化</h4>
          <div className="h-64">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={environmentData}>
                <CartesianGrid strokeDasharray="3 3" stroke={chartColors.grid} />
                <XAxis 
                  dataKey="time" 
                  tickFormatter={formatTime} 
                  stroke={chartColors.text}
                  tick={{ fontSize: 12 }}
                  interval={4}
                />
                <YAxis yAxisId="left" orientation="left" stroke={chartColors.quaternary} />
                <YAxis yAxisId="right" orientation="right" stroke={chartColors.secondary} />
                <Tooltip content={<CustomTooltip />} />
                <Legend />
                <Bar 
                  yAxisId="left"
                  dataKey="temperature" 
                  name="温度" 
                  unit="°C"
                  fill={chartColors.quaternary} 
                  radius={[4, 4, 0, 0]}
                />
                <Line 
                  yAxisId="right"
                  type="monotone" 
                  dataKey="humidity" 
                  name="湿度" 
                  unit="%"
                  stroke={chartColors.secondary} 
                  strokeWidth={2}
                  dot={{ r: 4 }}
                />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </motion.div>
      </div>
      
      {/* 数据分析摘要 */}
      <div className="mt-6 grid grid-cols-1 md:grid-cols-3 gap-4">
        <div className={`p-3 rounded-lg ${isDark ? 'bg-gray-900/50' : 'bg-gray-50'} border ${isDark ? 'border-gray-700' : 'border-gray-200'}`}>
          <p className="text-sm text-gray-500 dark:text-gray-400 mb-1">平均飞行高度</p>
          <p className="text-xl font-semibold">{(flightPathData.reduce((sum, item) => sum + item.altitude, 0) / flightPathData.length).toFixed(1)} m</p>
        </div>
        <div className={`p-3 rounded-lg ${isDark ? 'bg-gray-900/50' : 'bg-gray-50'} border ${isDark ? 'border-gray-700' : 'border-gray-200'}`}>
          <p className="text-sm text-gray-500 dark:text-gray-400 mb-1">平均速度</p>
          <p className="text-xl font-semibold">{(flightPathData.reduce((sum, item) => sum + item.speed, 0) / flightPathData.length).toFixed(1)} m/s</p>
        </div>
        <div className={`p-3 rounded-lg ${isDark ? 'bg-gray-900/50' : 'bg-gray-50'} border ${isDark ? 'border-gray-700' : 'border-gray-200'}`}>
          <p className="text-sm text-gray-500 dark:text-gray-400 mb-1">电池消耗率</p>
          <p className="text-xl font-semibold">
            {batteryData.length > 0 
              ? `${((batteryData[0].batteryLevel - batteryData[batteryData.length - 1].batteryLevel) / batteryData.length * 24).toFixed(1)}` 
              : '0.0'} 
            %/天
          </p>
        </div>
      </div>
    </div>
  );
};