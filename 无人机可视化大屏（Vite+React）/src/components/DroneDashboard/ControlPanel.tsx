import { useState } from 'react';
import { motion } from 'framer-motion';
import { useTheme } from '@/hooks/useTheme';

export const ControlPanel: React.FC = () => {
  const { isDark } = useTheme();
  const [droneStatus, setDroneStatus] = useState<'idle' | 'flying' | 'landing'>('idle');
  const [isArmed, setIsArmed] = useState(false);
  const [isEmergency, setIsEmergency] = useState(false);
  
  // 无人机状态对应的样式和标签
  const getStatusInfo = () => {
    switch (droneStatus) {
      case 'flying':
        return {
          bg: 'bg-green-100 text-green-700 dark:bg-green-900/30 dark:text-green-400',
          label: '飞行中',
          icon: 'fa-plane-departure'
        };
      case 'landing':
        return {
          bg: 'bg-amber-100 text-amber-700 dark:bg-amber-900/30 dark:text-amber-400',
          label: '降落中',
          icon: 'fa-plane-arrival'
        };
      default:
        return {
          bg: 'bg-blue-100 text-blue-700 dark:bg-blue-900/30 dark:text-blue-400',
          label: '待机',
          icon: 'fa-pause-circle'
        };
    }
  };
  
  // 处理起飞
  const handleTakeoff = () => {
    if (!isArmed) {
      setIsArmed(true);
      setTimeout(() => {
        setDroneStatus('flying');
        setIsEmergency(false);
      }, 1000);
    }
  };
  
  // 处理降落
  const handleLand = () => {
    if (droneStatus === 'flying') {
      setDroneStatus('landing');
      setTimeout(() => {
        setDroneStatus('idle');
        setIsArmed(false);
      }, 3000);
    }
  };
  
  // 处理紧急停止
  const handleEmergency = () => {
    setIsEmergency(true);
    setDroneStatus('idle');
    setIsArmed(false);
  };
  
  // 动画变量
  const buttonVariants = {
    hover: { scale: 1.05, transition: { duration: 0.2 } },
    tap: { scale: 0.95, transition: { duration: 0.1 } }
  };
  
  const statusInfo = getStatusInfo();
  
  return (
    <div className={`${isDark ? 'bg-gray-800' : 'bg-white'} border ${isDark ? 'border-gray-700' : 'border-gray-200'} rounded-xl p-5 shadow-lg h-full flex flex-col`}>
      <div className="flex justify-between items-center mb-6">
        <h3 className="text-lg font-semibold">自动控制操作面板</h3>
        <div className={`px-3 py-1 rounded-full text-xs font-medium ${statusInfo.bg} flex items-center`}>
          <i className={`fas ${statusInfo.icon} mr-1`}></i>
          {statusInfo.label}
        </div>
      </div>
      
      {/* 核心控制按钮 */}
      <div className="flex-1 flex flex-col items-center justify-center">
        {/* 起飞/降落按钮 */}
        <div className="flex flex-col items-center mb-8">
          <motion.button
            variants={buttonVariants}
            whileHover="hover"
            whileTap="tap"
            onClick={droneStatus === 'idle' ? handleTakeoff : handleLand}
            className={`w-20 h-20 rounded-full flex items-center justify-center text-white text-lg font-bold mb-2
              ${droneStatus === 'idle' 
                ? (isDark ? 'bg-green-700 hover:bg-green-600' : 'bg-green-500 hover:bg-green-600') 
                : (isDark ? 'bg-amber-700 hover:bg-amber-600' : 'bg-amber-500 hover:bg-amber-600')
              }
            `}
            disabled={droneStatus === 'landing'}
          >
            {droneStatus === 'idle' ? (
              <i className="fas fa-rocket text-2xl"></i>
            ) : (
              <i className="fas fa-landmark text-2xl"></i>
            )}
          </motion.button>
          <span className={`text-sm font-medium ${droneStatus === 'idle' ? 'text-green-600 dark:text-green-400' : 'text-amber-600 dark:text-amber-400'}`}>
            {droneStatus === 'idle' ? '起飞' : '降落'}
          </span>
        </div>
        
        {/* 状态指示灯 */}
        <div className="grid grid-cols-2 gap-6 mb-8 w-full max-w-xs">
          <div className={`p-4 rounded-lg ${isDark ? 'bg-gray-700' : 'bg-gray-100'} flex flex-col items-center`}>
            <div className={`w-6 h-6 rounded-full mb-2
              ${isArmed 
                ? 'bg-green-500 animate-pulse' 
                : (isEmergency ? 'bg-red-500 animate-pulse' : 'bg-gray-400')
              }
            `}></div>
            <span className="text-sm">
              {isEmergency ? '紧急停止' : (isArmed ? '已解锁' : '已锁定')}
            </span>
          </div>
          
          <div className={`p-4 rounded-lg ${isDark ? 'bg-gray-700' : 'bg-gray-100'} flex flex-col items-center`}>
            <div className={`w-6 h-6 rounded-full mb-2 bg-blue-500 ${droneStatus === 'flying' ? 'animate-pulse' : ''}`}></div>
            <span className="text-sm">系统在线</span>
          </div>
        </div>
        
        {/* 紧急停止按钮 */}
        <motion.button
          variants={buttonVariants}
          whileHover="hover"
          whileTap="tap"
          onClick={handleEmergency}
          className={`px-6 py-3 rounded-md ${isDark ? 'bg-red-900 hover:bg-red-800' : 'bg-red-600 hover:bg-red-700'} text-white font-bold flex items-center transition-colors`}
        >
          <i className="fas fa-exclamation-triangle mr-2"></i>
          紧急停止
        </motion.button>
      </div>
      
      {/* 额外控制选项 */}
      <div className="mt-6 grid grid-cols-2 gap-3">
        <button className={`px-4 py-2 rounded-md ${isDark ? 'bg-gray-700 hover:bg-gray-600' : 'bg-gray-100 hover:bg-gray-200'} text-sm`}>
          <i className="fas fa-repeat mr-1"></i> 悬停
        </button>
        <button className={`px-4 py-2 rounded-md ${isDark ? 'bg-gray-700 hover:bg-gray-600' : 'bg-gray-100 hover:bg-gray-200'} text-sm`}>
          <i className="fas fa-step-forward mr-1"></i> 下一步
        </button>
        <button className={`px-4 py-2 rounded-md ${isDark ? 'bg-gray-700 hover:bg-gray-600' : 'bg-gray-100 hover:bg-gray-200'} text-sm`}>
          <i className="fas fa-pause mr-1"></i> 暂停任务
        </button>
        <button className={`px-4 py-2 rounded-md ${isDark ? 'bg-gray-700 hover:bg-gray-600' : 'bg-gray-100 hover:bg-gray-200'} text-sm`}>
          <i className="fas fa-cog mr-1"></i> 参数设置
        </button>
      </div>
      
      {/* 操作提示 */}
      <div className={`mt-6 p-3 rounded-lg text-xs text-gray-500 dark:text-gray-400 ${isDark ? 'bg-gray-900/50' : 'bg-gray-50'}`}>
        <p className="flex items-start">
          <i className="fas fa-info-circle mr-2 mt-0.5"></i>
          <span>操作说明：点击"起飞"按钮启动无人机，飞行中点击"降落"按钮返回。紧急情况下，请立即点击"紧急停止"按钮。</span>
        </p>
      </div>
    </div>
  );
};