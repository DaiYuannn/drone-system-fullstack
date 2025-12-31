import { useState, useRef, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { mockEnvironmentModelData } from '@/mocks/droneData';
import { useTheme } from '@/hooks/useTheme';

export const EnvironmentModel: React.FC = () => {
  const { isDark } = useTheme();
  const [scale, setScale] = useState(1);
  const [position, setPosition] = useState({ x: 0, y: 0 });
  const [isDragging, setIsDragging] = useState(false);
  const [startPos, setStartPos] = useState({ x: 0, y: 0 });
  const [hoveredPoint, setHoveredPoint] = useState<number | null>(null);
  const modelRef = useRef<HTMLDivElement>(null);

  // 处理鼠标滚轮缩放
  const handleWheel = (e: React.WheelEvent) => {
    e.preventDefault();
    const delta = e.deltaY > 0 ? 0.9 : 1.1;
    setScale(prevScale => Math.max(0.5, Math.min(3, prevScale * delta)));
  };

  // 处理拖拽事件
  const handleMouseDown = (e: React.MouseEvent) => {
    setIsDragging(true);
    setStartPos({ x: e.clientX - position.x, y: e.clientY - position.y });
  };

  const handleMouseMove = (e: MouseEvent) => {
    if (isDragging) {
      setPosition({
        x: e.clientX - startPos.x,
        y: e.clientY - startPos.y
      });
    }
  };

  const handleMouseUp = () => {
    setIsDragging(false);
  };

  // 全局鼠标释放监听
  useEffect(() => {
    if (isDragging) {
      document.addEventListener('mousemove', handleMouseMove as EventListener);
      document.addEventListener('mouseup', handleMouseUp as EventListener);
      return () => {
        document.removeEventListener('mousemove', handleMouseMove as EventListener);
        document.removeEventListener('mouseup', handleMouseUp as EventListener);
      };
    }
  }, [isDragging, startPos]);

  // 获取点的颜色和大小
  const getPointStyle = (type: string) => {
    switch (type) {
      case 'ground':
        return { color: isDark ? 'bg-gray-600' : 'bg-gray-300', size: 8 };
      case 'building':
        return { color: isDark ? 'bg-blue-600' : 'bg-blue-400', size: 12 };
      case 'tree':
        return { color: isDark ? 'bg-green-600' : 'bg-green-400', size: 10 };
      case 'drone':
        return { color: 'bg-red-500', size: 16 };
      default:
        return { color: isDark ? 'bg-gray-400' : 'bg-gray-500', size: 8 };
    }
  };

  // 获取点的标签文本
  const getPointLabel = (type: string, x: number, y: number, z: number) => {
    const baseLabel = `坐标: (${x}, ${y}, ${z})`;
    switch (type) {
      case 'ground':
        return `地面点 ${baseLabel}`;
      case 'building':
        return `建筑物 ${baseLabel} 高度: ${z}m`;
      case 'tree':
        return `树木 ${baseLabel} 高度: ${z}m`;
      case 'drone':
        return `无人机位置 ${baseLabel}`;
      default:
        return baseLabel;
    }
  };

  return (
    <div className={`${isDark ? 'bg-gray-800' : 'bg-white'} border ${isDark ? 'border-gray-700' : 'border-gray-200'} rounded-xl p-5 shadow-lg h-full flex flex-col`}>
      <div className="flex justify-between items-center mb-4">
        <h3 className="text-lg font-semibold">环境模型可视化</h3>
        <div className="flex space-x-2">
          <button 
            onClick={() => setScale(1)} 
            className={`text-sm px-3 py-1 rounded-md ${isDark ? 'bg-gray-700 hover:bg-gray-600' : 'bg-gray-100 hover:bg-gray-200'}`}
          >
            重置视图
          </button>
          <div className="text-sm text-gray-500 dark:text-gray-400">
            <i className="fas fa-mouse-pointer mr-1"></i> 拖动: 平移 | 滚轮: 缩放
          </div>
        </div>
      </div>
      
      <div 
        ref={modelRef}
        className="flex-1 relative overflow-hidden border rounded-lg bg-gray-900 cursor-move"
        onWheel={handleWheel}
        onMouseDown={handleMouseDown}
      >
        <motion.div
          className="absolute inset-0 flex items-center justify-center"
          style={{ 
            scale, 
            x: position.x, 
            y: position.y,
            transition: isDragging ? 'none' : 'transform 0.3s ease-out'
          }}
        >
          {/* 简化的2D环境模型 */}
          <div className="relative w-[600px] h-[600px] border-2 border-gray-700">
            {/* 网格线 */}
            <div className="absolute inset-0 grid grid-cols-[repeat(6,1fr)] grid-rows-[repeat(6,1fr)]">
              {Array.from({ length: 6 }).map((_, i) => (
                <div key={`v-${i}`} className="absolute h-full w-px bg-gray-700" style={{ left: `${(i+1) * 100 / 6}%` }}></div>
              ))}
              {Array.from({ length: 6 }).map((_, i) => (
                <div key={`h-${i}`} className="absolute w-full h-px bg-gray-700" style={{ top: `${(i+1) * 100 / 6}%` }}></div>
              ))}
            </div>
            
            {/* 数据点 */}
            {mockEnvironmentModelData.map((point) => {
              const { color, size } = getPointStyle(point.type);
              const isHovered = hoveredPoint === point.id;
              
              return (
                <>
                  <motion.div
                    className={`absolute rounded-full ${color} flex items-center justify-center z-10`}
                    style={{
                      left: `${(point.x / 40) * 100}%`,
                      top: `${(point.y / 40) * 100}%`,
                      width: isHovered ? size + 4 : size,
                      height: isHovered ? size + 4 : size,
                    }}
                    onMouseEnter={() => setHoveredPoint(point.id)}
                    onMouseLeave={() => setHoveredPoint(null)}
                    animate={{
                      scale: isHovered ? 1.2 : 1,
                      transition: { duration: 0.2 }
                    }}
                  >
                    {point.type === 'drone' && (
                      <i className="fas fa-drone text-white text-xs"></i>
                    )}
                  </motion.div>
                  
                  {/* 悬停信息 */}
                  <AnimatePresence>
                    {isHovered && (
                      <motion.div
                        initial={{ opacity: 0, y: 10 }}
                        animate={{ opacity: 1, y: 0 }}
                        exit={{ opacity: 0, y: 10 }}
                        className="absolute z-20 bg-white dark:bg-gray-800 p-2 rounded-md shadow-lg text-xs whitespace-nowrap"
                        style={{
                          left: `${(point.x / 40) * 100}%`,
                          top: `${(point.y / 40) * 100}%`,
                          transform: 'translate(-50%, -120%)'
                        }}
                      >
                        {getPointLabel(point.type, point.x, point.y, point.z)}
                      </motion.div>
                    )}
                  </AnimatePresence>
                </>
              );
            })}
          </div>
        </motion.div>
        
        {/* 图例 */}
        <div className="absolute bottom-4 right-4 bg-black/50 text-white p-3 rounded-md text-xs flex flex-col space-y-2">
          <div className="flex items-center">
            <div className="w-3 h-3 rounded-full bg-gray-500 mr-2"></div>
            <span>地面</span>
          </div>
          <div className="flex items-center">
            <div className="w-3 h-3 rounded-full bg-blue-500 mr-2"></div>
            <span>建筑物</span>
          </div>
          <div className="flex items-center">
            <div className="w-3 h-3 rounded-full bg-green-500 mr-2"></div>
            <span>树木</span>
          </div>
          <div className="flex items-center">
            <div className="w-3 h-3 rounded-full bg-red-500 mr-2 flex items-center justify-center">
              <i className="fas fa-drone text-[8px]"></i>
            </div>
            <span>无人机</span>
          </div>
        </div>
      </div>
    </div>
  );
};