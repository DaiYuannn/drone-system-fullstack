// 无人机状态类型定义
export interface DroneStatus {
  id: string;
  name: string;
  gps: {
    latitude: number;
    longitude: number;
    accuracy: number;
  };
  battery: {
    level: number;
    temperature: number;
    voltage: number;
  };
  altitude: number;
  speed: number;
  heading: number;
  status: 'idle' | 'flying' | 'charging' | 'maintenance' | 'alert';
  lastUpdated: string;
}

// 环境数据类型定义
export interface EnvironmentData {
  temperature: number;
  humidity: number;
  pressure: number;
  windSpeed: number;
  windDirection: number;
  timestamp: string;
}

// 航线类型定义
export interface FlightRoute {
  id: string;
  name: string;
  distance: number;
  estimatedTime: number;
  waypoints: Array<{
    id: number;
    latitude: number;
    longitude: number;
    altitude: number;
    pauseTime?: number;
  }>;
  status: 'planned' | 'active' | 'completed' | 'cancelled';
  created: string;
}

// 系统通知类型定义
export interface SystemNotification {
  id: string;
  title: string;
  message: string;
  type: 'info' | 'warning' | 'error' | 'success';
  timestamp: string;
  isRead: boolean;
}

// 历史数据类型定义
export interface HistoricalData {
  timestamp: string;
  altitude: number;
  speed: number;
  batteryLevel: number;
  temperature: number;
  humidity: number;
}