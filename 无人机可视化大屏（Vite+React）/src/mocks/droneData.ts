import { DroneStatus, EnvironmentData, FlightRoute, SystemNotification, HistoricalData } from '@/types/drone';

// 生成当前时间
const getCurrentTime = () => new Date().toISOString();

// 生成过去24小时的历史数据
export const generateHistoricalData = (): HistoricalData[] => {
  const data: HistoricalData[] = [];
  const now = new Date();
  
  for (let i = 24; i >= 0; i--) {
    const time = new Date(now.getTime() - i * 60 * 60 * 1000);
    data.push({
      timestamp: time.toISOString(),
      altitude: Math.floor(Math.random() * 100) + 10,
      speed: Math.floor(Math.random() * 30) + 5,
      batteryLevel: Math.floor(Math.random() * 30) + 70,
      temperature: Math.floor(Math.random() * 10) + 20,
      humidity: Math.floor(Math.random() * 30) + 40
    });
  }
  
  return data;
};

// 模拟无人机状态数据
export const mockDroneStatus: DroneStatus = {
  id: 'drone-001',
  name: '探索者-1号',
  gps: {
    latitude: 39.9087,
    longitude: 116.3975,
    accuracy: 0.5
  },
  battery: {
    level: 85,
    temperature: 32,
    voltage: 12.5
  },
  altitude: 45,
  speed: 15.2,
  heading: 270,
  status: 'flying',
  lastUpdated: getCurrentTime()
};

// 模拟环境数据
export const mockEnvironmentData: EnvironmentData = {
  temperature: 25.5,
  humidity: 45.2,
  pressure: 1013.25,
  windSpeed: 3.5,
  windDirection: 180,
  timestamp: getCurrentTime()
};

// 模拟航线数据
export const mockFlightRoutes: FlightRoute[] = [
  {
    id: 'route-001',
    name: '城市巡检路线A',
    distance: 15.8,
    estimatedTime: 45,
    waypoints: [
      { id: 1, latitude: 39.9087, longitude: 116.3975, altitude: 50 },
      { id: 2, latitude: 39.9187, longitude: 116.4075, altitude: 60 },
      { id: 3, latitude: 39.9287, longitude: 116.4175, altitude: 50 },
      { id: 4, latitude: 39.9087, longitude: 116.3975, altitude: 40 }
    ],
    status: 'active',
    created: '2025-10-19T08:00:00Z'
  },
  {
    id: 'route-002',
    name: '工业区监测路线',
    distance: 22.3,
    estimatedTime: 60,
    waypoints: [
      { id: 1, latitude: 39.9387, longitude: 116.4275, altitude: 50 },
      { id: 2, latitude: 39.9487, longitude: 116.4375, altitude: 70 },
      { id: 3, latitude: 39.9587, longitude: 116.4475, altitude: 50 },
      { id: 4, latitude: 39.9387, longitude: 116.4275, altitude: 40 }
    ],
    status: 'planned',
    created: '2025-10-19T10:30:00Z'
  },
  {
    id: 'route-003',
    name: '园区巡逻路线',
    distance: 8.5,
    estimatedTime: 25,
    waypoints: [
      { id: 1, latitude: 39.8987, longitude: 116.3875, altitude: 40 },
      { id: 2, latitude: 39.9087, longitude: 116.3975, altitude: 30 },
      { id: 3, latitude: 39.8987, longitude: 116.3875, altitude: 40 }
    ],
    status: 'completed',
    created: '2025-10-19T09:15:00Z'
  }
];

// 模拟系统通知
export const mockNotifications: SystemNotification[] = [
  {
    id: 'notif-001',
    title: '任务完成',
    message: '探索者-1号已成功完成城市巡检任务',
    type: 'success',
    timestamp: '2025-10-19T14:30:00Z',
    isRead: false
  },
  {
    id: 'notif-002',
    title: '电池警告',
    message: '电池电量低于30%，请准备降落',
    type: 'warning',
    timestamp: '2025-10-19T13:45:00Z',
    isRead: true
  },
  {
    id: 'notif-003',
    title: '固件更新',
    message: '发现新的无人机固件更新版本1.2.3',
    type: 'info',
    timestamp: '2025-10-19T10:00:00Z',
    isRead: true
  },
  {
    id: 'notif-004',
    title: '连接丢失',
    message: '与无人机的通信暂时中断，请检查信号',
    type: 'error',
    timestamp: '2025-10-19T09:20:00Z',
    isRead: true
  }
];

// 模拟环境模型数据点
export const mockEnvironmentModelData = [
  { id: 1, x: 10, y: 10, z: 0, type: 'ground' },
  { id: 2, x: 20, y: 10, z: 0, type: 'ground' },
  { id: 3, x: 30, y: 10, z: 0, type: 'ground' },
  { id: 4, x: 10, y: 20, z: 0, type: 'ground' },
  { id: 5, x: 20, y: 20, z: 0, type: 'ground' },
  { id: 6, x: 30, y: 20, z: 0, type: 'ground' },
  { id: 7, x: 15, y: 15, z: 5, type: 'building' },
  { id: 8, x: 25, y: 15, z: 8, type: 'building' },
  { id: 9, x: 15, y: 25, z: 3, type: 'tree' },
  { id: 10, x: 25, y: 25, z: 4, type: 'tree' },
  { id: 11, x: 20, y: 20, z: 10, type: 'drone' },
];