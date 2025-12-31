import { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { useTheme } from '@/hooks/useTheme';
import { StatusCard } from '@/components/DroneDashboard/StatusCard';
import { EnvironmentModel } from '@/components/DroneDashboard/EnvironmentModel';
import { FlightRouteManager } from '@/components/DroneDashboard/FlightRouteManager';
import { ControlPanel } from '@/components/DroneDashboard/ControlPanel';
import { DataCharts } from '@/components/DroneDashboard/DataCharts';
import { NotificationPanel } from '@/components/DroneDashboard/NotificationPanel';
import { mockDroneStatus, mockEnvironmentData } from '@/mocks/droneData';

// 无人机仪表盘主组件
const DroneDashboard: React.FC = () => {
  const { theme, toggleTheme, isDark } = useTheme();
  const [currentTime, setCurrentTime] = useState(new Date());
  const [droneData, setDroneData] = useState(mockDroneStatus);
  const [environmentData, setEnvironmentData] = useState(mockEnvironmentData);
  
  // 更新时间
  useEffect(() => {
    const timer = setInterval(() => {
      setCurrentTime(new Date());
    }, 1000);
    
    return () => clearInterval(timer);
  }, []);
  
  // 模拟数据更新
  useEffect(() => {
    const interval = setInterval(() => {
      setDroneData(prev => ({
        ...prev,
        altitude: Math.max(10, Math.min(100, prev.altitude + (Math.random() - 0.5) * 5)),
        speed: Math.max(0, Math.min(30, prev.speed + (Math.random() - 0.5) * 2)),
        battery: {
          ...prev.battery,
          level: Math.max(0, prev.battery.level - Math.random() * 0.1),
          temperature: Math.max(25, Math.min(40, prev.battery.temperature + (Math.random() - 0.5) * 0.5))
        },
        lastUpdated: new Date().toISOString()
      }));
      
      setEnvironmentData(prev => ({
        ...prev,
        temperature: Math.max(15, Math.min(35, prev.temperature + (Math.random() - 0.5) * 0.3)),
        humidity: Math.max(30, Math.min(80, prev.humidity + (Math.random() - 0.5) * 1)),
        timestamp: new Date().toISOString()
      }));
    }, 5000);
    
    return () => clearInterval(interval);
  }, []);
  
  // 格式化时间显示
  const formatDateTime = () => {
    return currentTime.toLocaleString('zh-CN', {
      year: 'numeric',
      month: '2-digit',
      day: '2-digit',
      hour: '2-digit',
      minute: '2-digit',
      second: '2-digit'
    });
  };
  
  // 获取电池状态样式
  const getBatteryStatus = () => {
    if (droneData.battery.level > 70) return { status: 'success', description: '电量充足' };
    if (droneData.battery.level > 30) return { status: 'normal', description: '电量正常' };
    return { status: 'warning', description: '电量低，请尽快降落' };
  };
  
  // 获取无人机状态样式
  const getDroneStatusStyle = () => {
    switch (droneData.status) {
      case 'flying':
        return { 
          bg: 'bg-green-500', 
          status: 'success',
          description: '正在执行任务'
        };
      case 'charging':
        return { 
          bg: 'bg-blue-500', 
          status: 'normal',
          description: '充电中'
        };
      case 'maintenance':
        return { 
          bg: 'bg-amber-500', 
          status: 'warning',
          description: '维护模式'
        };
      case 'alert':
        return { 
          bg: 'bg-red-500', 
          status: 'danger',
          description: '异常状态'
        };
      default:
        return { 
          bg: 'bg-gray-500', 
          status: 'normal',
          description: '待机中'
        };
    }
  };
  
  const batteryStatus = getBatteryStatus();
  const droneStatusStyle = getDroneStatusStyle();
  
  return (
    <div className="min-h-screen bg-gray-50 dark:bg-gray-900 transition-colors duration-300">
      {/* 顶部导航 */}
      <header className={`sticky top-0 z-10 ${isDark ? 'bg-gray-800' : 'bg-white'} border-b ${isDark ? 'border-gray-700' : 'border-gray-200'} shadow-sm`}>
        <div className="container mx-auto px-4 py-3">
          <div className="flex justify-between items-center">
            <div className="flex items-center">
              <motion.div
                initial={{ rotate: 0 }}
                animate={{ rotate: 360 }}
                transition={{ duration: 2, repeat: 0 }}
                className="mr-3 text-blue-500"
              >
                <i className="fas fa-drone text-2xl"></i>
              </motion.div>
              <h1 className="text-xl font-bold">无人机管理系统</h1>
            </div>
            
            <div className="flex items-center space-x-4">
              <div className="text-sm text-gray-500 dark:text-gray-400">
                {formatDateTime()}
              </div>
              
              <button
                onClick={toggleTheme}
                className={`p-2 rounded-full ${isDark ? 'bg-gray-700 text-yellow-300' : 'bg-gray-100 text-gray-700'}`}
                aria-label="切换主题"
              >
                <i className={`fas ${isDark ? 'fa-sun' : 'fa-moon'}`}></i>
              </button>
              
              <div className="flex items-center">
                <div className={`w-8 h-8 rounded-full ${isDark ? 'bg-gray-700' : 'bg-blue-100'} flex items-center justify-center mr-2`}>
                  <i className="fas fa-user text-blue-500"></i>
                </div>
                <span className="text-sm font-medium">管理员</span>
              </div>
            </div>
          </div>
        </div>
      </header>
      
      {/* 主内容区域 */}
      <main className="container mx-auto px-4 py-6">
        {/* 状态概览卡片 */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 mb-6">
          <StatusCard
            title="无人机状态"
            value={droneData.status === 'flying' ? '飞行中' : 
                  droneData.status === 'charging' ? '充电中' : 
                  droneData.status === 'maintenance' ? '维护中' : 
                  droneData.status === 'alert' ? '警报' : '待机'}
            unit=""
            icon={<i className="fas fa-drone"></i>}
            color={droneStatusStyle.bg}
            status={droneStatusStyle.status}
            description={droneStatusStyle.description}
          />
          
          <StatusCard
            title="电池电量"
            value={droneData.battery.level.toFixed(1)}
            unit="%"
            icon={<i className="fas fa-battery-three-quarters"></i>}
            color={batteryStatus.status === 'success' ? 'bg-green-500' : 
                  batteryStatus.status === 'warning' ? 'bg-amber-500' : 'bg-red-500'}
            status={batteryStatus.status}
            description={batteryStatus.description}
          />
          
          <StatusCard
            title="飞行高度"
            value={droneData.altitude.toFixed(1)}
            unit="m"
            icon={<i className="fas fa-mountain"></i>}
            color="bg-blue-500"
            status="normal"
            description={`速度: ${droneData.speed.toFixed(1)} m/s`}
          />
          
          <StatusCard
            title="环境温度"
            value={environmentData.temperature.toFixed(1)}
            unit="°C"
            icon={<i className="fas fa-temperature-high"></i>}
            color="bg-purple-500"
            status="normal"
            description={`湿度: ${environmentData.humidity.toFixed(1)}%`}
          />
        </div>
        
        {/* 主要功能区 */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 mb-6">
          <div className="lg:col-span-2 grid grid-cols-1 lg:grid-cols-2 gap-6">
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.5 }}
              className="h-[400px]"
            >
              <EnvironmentModel />
            </motion.div>
            
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.5, delay: 0.1 }}
              className="h-[400px]"
            >
              <ControlPanel />
            </motion.div>
          </div>
          
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5, delay: 0.2 }}
            className="h-[400px]"
          >
            <NotificationPanel />
          </motion.div>
        </div>
        
        {/* 航线管理和数据图表 */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-6">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5, delay: 0.3 }}
            className="h-[500px]"
          >
            <FlightRouteManager />
          </motion.div>
          
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5, delay: 0.4 }}
            className="h-[500px]"
          >
            <DataCharts />
          </motion.div>
        </div>
      </main>
      
      {/* 页脚 */}
      <footer className={`py-4 ${isDark ? 'bg-gray-800 border-t border-gray-700' : 'bg-white border-t border-gray-200'}`}>
        <div className="container mx-auto px-4 text-center text-sm text-gray-500 dark:text-gray-400">
          <p>© {new Date().getFullYear()} 无人机管理系统 | 版本 1.0.0</p>
        </div>
      </footer>
    </div>
  );
};

export default DroneDashboard;