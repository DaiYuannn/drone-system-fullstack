import { useState } from 'react';
import { motion } from 'framer-motion';
import { mockFlightRoutes } from '@/mocks/droneData';
import { FlightRoute } from '@/types/drone';
import { useTheme } from '@/hooks/useTheme';

// 状态样式与标签
const getStatusStyle = (status: FlightRoute['status']) => {
  switch (status) {
    case 'active':
      return { bg: 'bg-green-100 text-green-700 dark:bg-green-900/40 dark:text-green-300', label: '执行中' };
    case 'planned':
      return { bg: 'bg-amber-100 text-amber-700 dark:bg-amber-900/40 dark:text-amber-300', label: '计划中' };
    case 'completed':
      return { bg: 'bg-gray-100 text-gray-700 dark:bg-gray-800 dark:text-gray-300', label: '已完成' };
    case 'cancelled':
      return { bg: 'bg-red-100 text-red-700 dark:bg-red-900/40 dark:text-red-300', label: '已取消' };
    default:
      return { bg: 'bg-gray-100 text-gray-700 dark:bg-gray-800 dark:text-gray-300', label: status };
  }
};

const formatTime = (mins: number) => `${mins} 分钟`;

export const FlightRouteManager: React.FC = () => {
  const { isDark } = useTheme();
  const [routes, setRoutes] = useState<FlightRoute[]>(mockFlightRoutes);
  const [selectedRoute, setSelectedRoute] = useState<FlightRoute | null>(null);

  const handleSelectRoute = (route: FlightRoute) => setSelectedRoute(route);

  const handleActivateRoute = (id: string) => {
    setRoutes(prev => prev.map(r => ({ ...r, status: r.id === id ? 'active' : r.status })));
    const r = routes.find(r => r.id === id);
    if (r) setSelectedRoute({ ...r, status: 'active' });
  };

  const handleDeleteRoute = (id: string) => {
    setRoutes(prev => prev.filter(r => r.id !== id));
    setSelectedRoute(prev => (prev && prev.id === id ? null : prev));
  };

  return (
    <div className="p-4">
      <div className="flex flex-col lg:flex-row gap-4">
        {/* 左侧：航线列表 */}
        <div className={`lg:w-1/2 ${isDark ? 'bg-gray-900/50' : 'bg-white'} rounded-lg p-4 border ${isDark ? 'border-gray-800' : 'border-gray-200'}`}>
          <div className="flex items-center justify-between mb-4">
            <h3 className="font-semibold text-lg">航线列表</h3>
            <span className="text-sm text-gray-500 dark:text-gray-400">共 {routes.length} 条</span>
          </div>

          <div className="space-y-3">
            {routes.map((route) => (
              <motion.div
                key={route.id}
                whileHover={{ scale: 1.01 }}
                className={`p-3 rounded-lg cursor-pointer flex items-center justify-between border ${isDark ? 'bg-gray-800/60 border-gray-700 hover:bg-gray-800' : 'bg-gray-50 border-gray-200 hover:bg-gray-100'}`}
                onClick={() => handleSelectRoute(route)}
              >
                <div className="min-w-0">
                  <div className="flex items-center gap-2">
                    <h4 className="font-medium truncate">{route.name}</h4>
                    <span className={`text-xs px-2 py-0.5 rounded-full ${getStatusStyle(route.status).bg}`}>
                      {getStatusStyle(route.status).label}
                    </span>
                  </div>
                  <div className="text-xs text-gray-500 dark:text-gray-400 mt-1">
                    距离 {route.distance} km · 预计 {formatTime(route.estimatedTime)} · 创建于 {new Date(route.created).toLocaleString()}
                  </div>
                </div>
                <div className="flex items-center gap-2">
                  <button 
                    onClick={(e) => e.stopPropagation()}
                    className={`text-xs px-2 py-1 rounded ${isDark ? 'bg-gray-700 hover:bg-gray-600' : 'bg-gray-100 hover:bg-gray-200'}`}
                  >
                    编辑
                  </button>
                  <button 
                    onClick={(e) => {
                      e.stopPropagation();
                      handleDeleteRoute(route.id);
                    }}
                    className={`text-xs px-2 py-1 rounded ${isDark ? 'bg-red-900/50 hover:bg-red-900/70 text-red-300' : 'bg-red-100 hover:bg-red-200 text-red-700'}`}
                  >
                    删除
                  </button>
                </div>
              </motion.div>
            ))}
          </div>
        </div>

        {/* 右侧：航线详情 */}
        <div className={`flex-1 overflow-y-auto ${isDark ? 'bg-gray-900/50' : 'bg-gray-50'} rounded-lg p-4 border ${isDark ? 'border-gray-800' : 'border-gray-200'}`}>
          {selectedRoute ? (
            <div>
              <div className="flex justify-between items-center mb-4">
                <h4 className="font-semibold text-lg">{selectedRoute.name} - 详情</h4>
                <span className={`text-xs px-2 py-1 rounded-full ${getStatusStyle(selectedRoute.status).bg}`}>
                  {getStatusStyle(selectedRoute.status).label}
                </span>
              </div>

              <div className={`mb-4 rounded-lg overflow-hidden border ${isDark ? 'border-gray-700' : 'border-gray-200'}`}>
                {/* 简化的地图视图 */}
                <div className="h-48 bg-gray-900 relative">
                  {/* 航线可视化 */}
                  <svg className="absolute inset-0 w-full h-full" viewBox="0 0 400 200">
                    {/* 绘制航线 */}
                    <path
                      d={selectedRoute.waypoints.map((wp, i) => {
                        const x = (wp.longitude - 116.3) * 1000;
                        const y = (39.95 - wp.latitude) * 1000;
                        return i === 0 ? `M ${x} ${y}` : `L ${x} ${y}`;
                      }).join(' ')}
                      stroke="#3b82f6"
                      strokeWidth="2"
                      fill="none"
                      strokeDasharray={selectedRoute.status === 'active' ? '5,5' : 'none'}
                    />

                    {/* 绘制航点 */}
                    {selectedRoute.waypoints.map((wp, i) => {
                      const x = (wp.longitude - 116.3) * 1000;
                      const y = (39.95 - wp.latitude) * 1000;
                      return (
                        <g key={wp.id}>
                          <circle cx={x} cy={y} r="6" fill={i === 0 ? "#10b981" : "#6366f1"} />
                          <text 
                            x={x} 
                            y={y - 10} 
                            fill="white" 
                            fontSize="12" 
                            textAnchor="middle"
                          >
                            WP{i+1}
                          </text>
                        </g>
                      );
                    })}
                  </svg>

                  {/* 地图图例 */}
                  <div className="absolute bottom-2 left-2 bg-black/50 text-white p-2 rounded text-xs">
                    <div className="flex items-center mb-1">
                      <div className="w-3 h-0.5 bg-blue-500 mr-2"></div>
                      <span>航线</span>
                    </div>
                    <div className="flex items-center">
                      <div className="w-3 h-3 rounded-full bg-green-500 mr-2"></div>
                      <span>起点</span>
                    </div>
                  </div>
                </div>
              </div>

              {/* 航线信息 */}
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-4">
                <div className={`p-3 rounded-lg ${isDark ? 'bg-gray-800' : 'bg-white'} border ${isDark ? 'border-gray-700' : 'border-gray-200'}`}>
                  <p className="text-sm text-gray-500 dark:text-gray-400 mb-1">总距离</p>
                  <p className="text-xl font-semibold">{selectedRoute.distance} km</p>
                </div>
                <div className={`p-3 rounded-lg ${isDark ? 'bg-gray-800' : 'bg-white'} border ${isDark ? 'border-gray-700' : 'border-gray-200'}`}>
                  <p className="text-sm text-gray-500 dark:text-gray-400 mb-1">预计时间</p>
                  <p className="text-xl font-semibold">{formatTime(selectedRoute.estimatedTime)}</p>
                </div>
              </div>

              {/* 航点列表 */}
              <div className="mb-4">
                <h5 className="font-medium mb-2">航点详情</h5>
                <div className="space-y-2">
                  {selectedRoute.waypoints.map((wp, i) => (
                    <div 
                      key={wp.id}
                      className={`p-2 rounded-lg ${isDark ? 'bg-gray-800' : 'bg-white'} border ${isDark ? 'border-gray-700' : 'border-gray-200'} flex justify-between items-center`}
                    >
                      <div>
                        <div className="font-medium">
                          航点 {i+1} {i === 0 ? '(起点)' : i === selectedRoute.waypoints.length - 1 ? '(终点)' : ''}
                        </div>
                        <div className="text-xs text-gray-500 dark:text-gray-400 mt-1">
                          坐标: {wp.latitude.toFixed(6)}, {wp.longitude.toFixed(6)} | 高度: {wp.altitude}m
                        </div>
                      </div>
                      {wp.pauseTime && (
                        <span className={`text-xs px-2 py-1 rounded-full ${isDark ? 'bg-amber-900/30 text-amber-400' : 'bg-amber-100 text-amber-700'}`}>
                          停留 {wp.pauseTime}s
                        </span>
                      )}
                    </div>
                  ))}
                </div>
              </div>

              {/* 操作按钮 */}
              <div className="flex justify-between">
                <button onClick={() => selectedRoute && handleDeleteRoute(selectedRoute.id)} className={`px-4 py-2 rounded-md ${isDark ? 'bg-red-900/50 hover:bg-red-900/70 text-red-300' : 'bg-red-100 hover:bg-red-200 text-red-700'} font-medium`}>
                  <i className="fas fa-trash-alt mr-1"></i> 删除航线
                </button>
                {selectedRoute.status !== 'active' && (
                  <button onClick={() => handleActivateRoute(selectedRoute.id)} className={`px-4 py-2 rounded-md ${isDark ? 'bg-blue-700 hover:bg-blue-600' : 'bg-blue-500 hover:bg-blue-600'} text-white font-medium transition-colors`}>
                    <i className="fas fa-play mr-1"></i> 执行航线
                  </button>
                )}
              </div>
            </div>
          ) : (
            <div className="flex items-center justify-center h-full text-gray-500 dark:text-gray-400">
              <div className="text-center">
                <i className="fas fa-map-marked-alt text-4xl mb-2"></i>
                <p>选择一条航线查看详情</p>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};