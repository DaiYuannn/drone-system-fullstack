import { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { mockNotifications } from '@/mocks/droneData';
import { SystemNotification } from '@/types/drone';
import { useTheme } from '@/hooks/useTheme';

export const NotificationPanel: React.FC = () => {
  const { isDark } = useTheme();
  const [notifications, setNotifications] = useState<SystemNotification[]>(mockNotifications);
  const [showAll, setShowAll] = useState(false);
  
  // 生成新通知的定时器
  useEffect(() => {
    const interval = setInterval(() => {
      // 随机生成新通知
      const newNotification: SystemNotification = {
        id: `notif-${Date.now()}`,
        title: ['系统更新', '任务状态', '传感器数据', '电池警告'][Math.floor(Math.random() * 4)],
        message: ['数据已更新', '任务已完成', '传感器连接正常', '电池电量充足'][Math.floor(Math.random() * 4)],
        type: ['info', 'success', 'warning', 'error'][Math.floor(Math.random() * 4)] as any,
        timestamp: new Date().toISOString(),
        isRead: false
      };
      
      setNotifications(prev => [newNotification, ...prev]);
    }, 30000); // 每30秒生成一个新通知
    
    return () => clearInterval(interval);
  }, []);// 获取通知类型对应的样式和图标
  const getNotificationStyle = (type: string) => {
    switch (type) {
      case 'error':
        return {
          bg: isDark ? 'bg-red-900/20 border-red-900/50' : 'bg-red-50 border-red-100',
          text: 'text-red-600 dark:text-red-400',
          icon: 'fa-exclamation-circle',
          label: '错误'
        };
      case 'warning':
        return {
          bg: isDark ? 'bg-amber-900/20 border-amber-900/50' : 'bg-amber-50 border-amber-100',
          text: 'text-amber-600 dark:text-amber-400',
          icon: 'fa-exclamation-triangle',
          label: '警告'
        };
      case 'success':
        return {
          bg: isDark ? 'bg-green-900/20 border-green-900/50' : 'bg-green-50 border-green-100',
          text: 'text-green-600 dark:text-green-400',
          icon: 'fa-check-circle',
          label: '成功'
        };
      default:
        return {
          bg: isDark ? 'bg-blue-900/20 border-blue-900/50' : 'bg-blue-50 border-blue-100',
          text: 'text-blue-600 dark:text-blue-400',
          icon: 'fa-info-circle',
          label: '信息'
        };
    }
  };
  
  // 格式化时间
  const formatTime = (timestamp: string) => {
    const date = new Date(timestamp);
    const now = new Date();
    const diffMs = now.getTime() - date.getTime();
    const diffMins = Math.floor(diffMs / 60000);
    const diffHours = Math.floor(diffMs / 3600000);
    
    if (diffMins < 1) return '刚刚';
    if (diffMins < 60) return `${diffMins}分钟前`;
    if (diffHours < 24) return `${diffHours}小时前`;
    
    return date.toLocaleDateString();
  };
  
  // 标记所有通知为已读
  const markAllAsRead = () => {
    setNotifications(prev => prev.map(notif => ({ ...notif, isRead: true })));
  };
  
  // 删除通知
  const deleteNotification = (id: string) => {
    setNotifications(prev => prev.filter(notif => notif.id !== id));
  };
  
  // 标记单个通知为已读
  const markAsRead = (id: string) => {
    setNotifications(prev => 
      prev.map(notif => notif.id === id ? { ...notif, isRead: true } : notif)
    );
  };
  
  // 未读通知数量
  const unreadCount = notifications.filter(notif => !notif.isRead).length;
  
  // 显示的通知列表
  const displayedNotifications = showAll 
    ? notifications 
    : notifications.slice(0, 5);
  
  return (
    <div className={`${isDark ? 'bg-gray-800' : 'bg-white'} border ${isDark ? 'border-gray-700' : 'border-gray-200'} rounded-xl p-5 shadow-lg h-full flex flex-col`}>
      <div className="flex justify-between items-center mb-4">
        <div className="flex items-center">
          <h3 className="text-lg font-semibold">系统通知</h3>
          {unreadCount > 0 && (
            <span className="ml-2 w-5 h-5 rounded-full bg-red-500 text-white text-xs flex items-center justify-center">
              {unreadCount}
            </span>
          )}
        </div>
        <button 
          onClick={markAllAsRead}
          className={`text-sm ${isDark ? 'text-gray-400 hover:text-gray-300' : 'text-gray-500 hover:text-gray-700'}`}
        >
          全部标为已读
        </button>
      </div>
      
      {/* 通知列表 */}
      <div className="flex-1 overflow-y-auto space-y-3">
        <AnimatePresence>
          {displayedNotifications.length > 0 ? (
            displayedNotifications.map((notification) => {
              const style = getNotificationStyle(notification.type);
              
              return (
                <motion.div
                  key={notification.id}
                  initial={{ opacity: 0, y: 10 }}
                  animate={{ opacity: 1, y: 0 }}
                  exit={{ opacity: 0, y: -10 }}
                  transition={{ duration: 0.3 }}
                  className={`p-4 rounded-lg border ${style.bg} ${notification.isRead ? '' : 'ring-2 ring-offset-2 ring-offset-white dark:ring-offset-gray-800 ring-blue-500'}`}
                  onClick={() => markAsRead(notification.id)}
                >
                  <div className="flex justify-between items-start mb-2">
                    <div className="flex items-center">
                      <i className={`fas ${style.icon} mr-2 ${style.text}`}></i>
                      <span className={`font-medium ${style.text}`}>{notification.title}</span>
                    </div>
                    <div className="flex items-center">
                      <span className="text-xs text-gray-500 dark:text-gray-400 mr-2">{formatTime(notification.timestamp)}</span>
                      <button 
                        onClick={(e) => {
                          e.stopPropagation();
                          deleteNotification(notification.id);
                        }}
                        className={`text-gray-400 hover:text-gray-600 dark:hover:text-gray-200 p-1 rounded-full hover:bg-gray-200 dark:hover:bg-gray-700`}
                      >
                        <i className="fas fa-times"></i>
                      </button>
                    </div>
                  </div>
                  <p className={`text-sm ${isDark ? 'text-gray-300' : 'text-gray-700'}`}>{notification.message}</p>
                </motion.div>
              );
            })
          ) : (
            <div className="flex items-center justify-center h-full text-gray-500 dark:text-gray-400">
              <div className="text-center">
                <i className="fas fa-bell-slash text-4xl mb-2"></i>
                <p>暂无通知</p>
              </div>
            </div>
          )}
        </AnimatePresence>
      </div>
      
      {/* 查看更多按钮 */}
      {notifications.length > 5 && (
        <button 
          onClick={() => setShowAll(!showAll)}
          className={`mt-4 w-full py-2 rounded-md text-sm font-medium transition-colors ${
            isDark 
              ? 'bg-gray-700 hover:bg-gray-600' 
              : 'bg-gray-100 hover:bg-gray-200'
          }`}
        >
          {showAll ? '收起' : `查看更多 (${notifications.length - 5})`}
        </button>
      )}
      
      {/* 系统状态摘要 */}
      <div className="mt-4 grid grid-cols-3 gap-2">
        <div className={`p-2 rounded text-center ${isDark ? 'bg-green-900/20 text-green-400' : 'bg-green-50 text-green-700'}`}>
          <i className="fas fa-check-circle block text-lg mb-1"></i>
          <span className="text-xs">系统正常</span>
        </div>
        <div className={`p-2 rounded text-center ${isDark ? 'bg-blue-900/20 text-blue-400' : 'bg-blue-50 text-blue-700'}`}>
          <i className="fas fa-drone block text-lg mb-1"></i>
          <span className="text-xs">1台设备</span>
        </div>
        <div className={`p-2 rounded text-center ${isDark ? 'bg-amber-900/20 text-amber-400' : 'bg-amber-50 text-amber-700'}`}>
          <i className="fas fa-tasks block text-lg mb-1"></i>
          <span className="text-xs">3个任务</span>
        </div>
      </div>
    </div>
  );
};