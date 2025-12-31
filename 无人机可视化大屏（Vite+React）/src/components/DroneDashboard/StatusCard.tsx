import { motion } from 'framer-motion';
import { useTheme } from '@/hooks/useTheme';

interface StatusCardProps {
  title: string;
  value: number | string;
  unit: string;
  icon: React.ReactNode;
  color: string;
  status?: 'normal' | 'warning' | 'danger' | 'success';
  description?: string;
}

export const StatusCard: React.FC<StatusCardProps> = ({
  title,
  value,
  unit,
  icon,
  color,
  status = 'normal',
  description
}) => {
  const { isDark } = useTheme();
  
  // 根据状态获取背景颜色
  const getBgColor = () => {
    switch (status) {
      case 'warning':
        return isDark ? 'bg-amber-900/20' : 'bg-amber-50';
      case 'danger':
        return isDark ? 'bg-red-900/20' : 'bg-red-50';
      case 'success':
        return isDark ? 'bg-green-900/20' : 'bg-green-50';
      default:
        return isDark ? 'bg-gray-800' : 'bg-white';
    }
  };
  
  // 根据状态获取边框颜色
  const getBorderColor = () => {
    switch (status) {
      case 'warning':
        return 'border-amber-500';
      case 'danger':
        return 'border-red-500';
      case 'success':
        return 'border-green-500';
      default:
        return isDark ? 'border-gray-700' : 'border-gray-200';
    }
  };
  
  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.5 }}
      className={`${getBgColor()} border ${getBorderColor()} rounded-xl p-5 shadow-lg hover:shadow-xl transition-all duration-300`}
    >
      <div className="flex items-center justify-between mb-3">
        <h3 className="text-sm font-medium text-gray-500 dark:text-gray-400">{title}</h3>
        <span className={`p-2 rounded-full ${color} text-white`}>{icon}</span>
      </div>
      
      <div className="flex items-baseline justify-between">
        <div>
          <p className="text-2xl font-bold">{value}</p>
          {description && <p className="text-xs text-gray-500 dark:text-gray-400 mt-1">{description}</p>}
        </div>
        <span className="text-sm font-medium text-gray-500 dark:text-gray-400">{unit}</span>
      </div>
    </motion.div>
  );
};