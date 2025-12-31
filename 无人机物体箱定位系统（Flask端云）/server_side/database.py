"""
数据库操作模块 - SQLite 版本（简化且稳健）
"""
from __future__ import annotations

import json
import logging
import sqlite3
import threading
from datetime import datetime, timedelta
from typing import Dict, List, Optional

import config

logger = logging.getLogger(__name__)


class DatabaseManager:
    def __init__(self) -> None:
        # 通过 getattr 获取配置，避免类型检查器在分析期找不到属性
        _db_cfg = getattr(config, "DB_CONFIG", {}) or {}
        self.db_path = _db_cfg.get("path", "drone_positioning.db")
        self.timeout = _db_cfg.get("timeout", 30)
        self.check_same_thread = _db_cfg.get("check_same_thread", False)
        self._local = threading.local()

    def _get_connection(self) -> sqlite3.Connection:
        if not hasattr(self._local, "connection") or self._local.connection is None:
            conn = sqlite3.connect(
                self.db_path, timeout=self.timeout, check_same_thread=self.check_same_thread
            )
            conn.row_factory = sqlite3.Row
            # 提升稳定性：启用 WAL、外键，设置 busy_timeout
            try:
                conn.execute("PRAGMA journal_mode=WAL")
            except Exception:
                pass
            try:
                conn.execute("PRAGMA foreign_keys=ON")
            except Exception:
                pass
            try:
                conn.execute(f"PRAGMA busy_timeout={int(self.timeout*1000)}")
            except Exception:
                pass
            self._local.connection = conn
        return self._local.connection  # type: ignore[return-value]

    def connect(self) -> bool:
        try:
            conn = self._get_connection()
            conn.execute("SELECT 1")
            logger.info(f"SQLite数据库连接成功: {self.db_path}")
            return True
        except sqlite3.Error as e:
            logger.error(f"数据库连接失败: {e}")
            return False

    def disconnect(self) -> None:
        if hasattr(self._local, "connection") and self._local.connection:
            try:
                self._local.connection.close()
            except Exception:
                pass
            self._local.connection = None
            logger.info("数据库连接已断开")

    def create_tables(self) -> bool:
        try:
            conn = self._get_connection()
            cur = conn.cursor()

            cur.execute(
                """
                CREATE TABLE IF NOT EXISTS box_positions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TEXT NOT NULL,
                    drone_id TEXT NOT NULL,
                    barcode_data TEXT NOT NULL,
                    barcode_type TEXT,
                    latitude REAL,
                    longitude REAL,
                    altitude REAL,
                    confidence REAL,
                    bbox_x1 INTEGER,
                    bbox_y1 INTEGER,
                    bbox_x2 INTEGER,
                    bbox_y2 INTEGER,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP
                )
                """
            )

            cur.execute(
                """
                CREATE TABLE IF NOT EXISTS drone_status (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    drone_id TEXT NOT NULL UNIQUE,
                    status TEXT NOT NULL DEFAULT 'offline',
                    last_heartbeat TEXT,
                    gps_latitude REAL,
                    gps_longitude REAL,
                    gps_altitude REAL,
                    battery_level INTEGER,
                    signal_strength INTEGER,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                    updated_at TEXT DEFAULT CURRENT_TIMESTAMP
                )
                """
            )

            cur.execute(
                """
                CREATE TABLE IF NOT EXISTS system_logs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TEXT DEFAULT CURRENT_TIMESTAMP,
                    level TEXT NOT NULL,
                    source TEXT,
                    message TEXT,
                    data TEXT
                )
                """
            )

            # 索引
            for sql in [
                "CREATE INDEX IF NOT EXISTS idx_box_timestamp ON box_positions(timestamp)",
                "CREATE INDEX IF NOT EXISTS idx_box_drone_id ON box_positions(drone_id)",
                "CREATE INDEX IF NOT EXISTS idx_box_barcode ON box_positions(barcode_data)",
                "CREATE INDEX IF NOT EXISTS idx_drone_id ON drone_status(drone_id)",
                "CREATE INDEX IF NOT EXISTS idx_drone_status ON drone_status(status)",
                "CREATE INDEX IF NOT EXISTS idx_log_timestamp ON system_logs(timestamp)",
            ]:
                cur.execute(sql)

            conn.commit()
            cur.close()
            logger.info("SQLite数据库表创建成功")
            return True
        except sqlite3.Error as e:
            logger.error(f"创建数据库表失败: {e}")
            return False

    def insert_box_position(self, data: Dict) -> bool:
        try:
            conn = self._get_connection()
            cur = conn.cursor()

            gps = data.get("gps") or {}
            lat = gps.get("latitude") if isinstance(gps, dict) else None
            lon = gps.get("longitude") if isinstance(gps, dict) else None
            alt = gps.get("altitude") if isinstance(gps, dict) else None

            sql = (
                "INSERT INTO box_positions (timestamp, drone_id, barcode_data, barcode_type, "
                "latitude, longitude, altitude, confidence, bbox_x1, bbox_y1, bbox_x2, bbox_y2, created_at) "
                "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)"
            )
            values = (
                data["timestamp"],
                data["drone_id"],
                data["barcode_data"],
                data.get("barcode_type"),
                lat,
                lon,
                alt,
                data.get("confidence"),
                data.get("bbox_x1"),
                data.get("bbox_y1"),
                data.get("bbox_x2"),
                data.get("bbox_y2"),
                datetime.now().isoformat(),
            )
            cur.execute(sql, values)
            conn.commit()
            cur.close()
            logger.debug(f"物体箱位置数据插入成功: {data.get('barcode_data')}")
            return True
        except sqlite3.Error as e:
            logger.error(f"插入物体箱位置数据失败: {e}")
            return False

    def update_drone_status(self, drone_id: str, status_data: Dict) -> bool:
        try:
            conn = self._get_connection()
            cur = conn.cursor()
            cur.execute("SELECT id FROM drone_status WHERE drone_id = ?", (drone_id,))
            row = cur.fetchone()

            gps = status_data.get("gps") or {}
            now = datetime.now().isoformat()

            if row:
                sql = (
                    "UPDATE drone_status SET status=?, last_heartbeat=?, gps_latitude=?, gps_longitude=?, "
                    "gps_altitude=?, battery_level=?, signal_strength=?, updated_at=? WHERE drone_id=?"
                )
                values = (
                    status_data.get("status", "online"),
                    now,
                    gps.get("latitude") if isinstance(gps, dict) else None,
                    gps.get("longitude") if isinstance(gps, dict) else None,
                    gps.get("altitude") if isinstance(gps, dict) else None,
                    status_data.get("battery_level"),
                    status_data.get("signal_strength"),
                    now,
                    drone_id,
                )
            else:
                sql = (
                    "INSERT INTO drone_status (drone_id, status, last_heartbeat, gps_latitude, gps_longitude, "
                    "gps_altitude, battery_level, signal_strength, created_at, updated_at) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)"
                )
                values = (
                    drone_id,
                    status_data.get("status", "online"),
                    now,
                    gps.get("latitude") if isinstance(gps, dict) else None,
                    gps.get("longitude") if isinstance(gps, dict) else None,
                    gps.get("altitude") if isinstance(gps, dict) else None,
                    status_data.get("battery_level"),
                    status_data.get("signal_strength"),
                    now,
                    now,
                )

            cur.execute(sql, values)
            conn.commit()
            cur.close()
            logger.debug(f"无人机状态更新成功: {drone_id}")
            return True
        except sqlite3.Error as e:
            logger.error(f"更新无人机状态失败: {e}")
            return False

    def get_recent_positions(self, limit: int = 100, drone_id: Optional[str] = None) -> List[Dict]:
        try:
            conn = self._get_connection()
            cur = conn.cursor()
            if drone_id:
                cur.execute(
                    "SELECT * FROM box_positions WHERE drone_id = ? ORDER BY timestamp DESC LIMIT ?",
                    (drone_id, limit),
                )
            else:
                cur.execute(
                    "SELECT * FROM box_positions ORDER BY timestamp DESC LIMIT ?",
                    (limit,),
                )
            rows = cur.fetchall()
            cur.close()
            return [dict(r) for r in rows]
        except sqlite3.Error as e:
            logger.error(f"获取位置数据失败: {e}")
            return []

    def get_drone_status(self, drone_id: Optional[str] = None) -> List[Dict]:
        try:
            conn = self._get_connection()
            cur = conn.cursor()
            if drone_id:
                cur.execute("SELECT * FROM drone_status WHERE drone_id = ?", (drone_id,))
            else:
                cur.execute("SELECT * FROM drone_status ORDER BY updated_at DESC")
            rows = cur.fetchall()
            cur.close()
            return [dict(r) for r in rows]
        except sqlite3.Error as e:
            logger.error(f"获取无人机状态失败: {e}")
            return []

    def cleanup_old_data(self, days: Optional[int] = None) -> bool:
        _sys_cfg = getattr(config, "SYSTEM_CONFIG", {}) or {}
        keep_days = days or _sys_cfg.get("data_retention_days", 30)
        cutoff = (datetime.now() - timedelta(days=keep_days)).isoformat()
        try:
            conn = self._get_connection()
            cur = conn.cursor()
            cur.execute("DELETE FROM box_positions WHERE timestamp < ?", (cutoff,))
            pos_deleted = cur.rowcount
            cur.execute("DELETE FROM system_logs WHERE timestamp < ?", (cutoff,))
            log_deleted = cur.rowcount
            conn.commit()
            cur.close()
            logger.info(
                f"数据清理完成 - 位置数据: {pos_deleted}条, 日志数据: {log_deleted}条"
            )
            return True
        except sqlite3.Error as e:
            logger.error(f"数据清理失败: {e}")
            return False

    def get_statistics(self) -> Dict:
        try:
            conn = self._get_connection()
            cur = conn.cursor()
            cur.execute("SELECT COUNT(*) FROM box_positions")
            total = cur.fetchone()[0]

            today = datetime.now().date().isoformat()
            cur.execute(
                "SELECT COUNT(*) FROM box_positions WHERE date(timestamp) = ?",
                (today,),
            )
            today_count = cur.fetchone()[0]

            one_minute_ago = (datetime.now() - timedelta(minutes=1)).isoformat()
            cur.execute(
                "SELECT COUNT(*) FROM drone_status WHERE status = 'online' AND last_heartbeat > ?",
                (one_minute_ago,),
            )
            online = cur.fetchone()[0]

            cur.execute("SELECT COUNT(DISTINCT barcode_data) FROM box_positions")
            uniq = cur.fetchone()[0]
            cur.close()
            return {
                "total_detections": total,
                "today_detections": today_count,
                "online_drones": online,
                "unique_barcodes": uniq,
            }
        except sqlite3.Error as e:
            logger.error(f"获取统计信息失败: {e}")
            return {}

    def log_system_event(self, level: str, source: str, message: str, data: Optional[Dict] = None) -> None:
        try:
            conn = self._get_connection()
            cur = conn.cursor()
            cur.execute(
                "INSERT INTO system_logs (timestamp, level, source, message, data) VALUES (?, ?, ?, ?, ?)",
                (
                    datetime.now().isoformat(),
                    level,
                    source,
                    message,
                    json.dumps(data, ensure_ascii=False) if data else None,
                ),
            )
            conn.commit()
            cur.close()
        except sqlite3.Error as e:
            logger.error(f"记录系统事件失败: {e}")

    # ----- 管理操作：删除/清空/更新 -----
    def delete_positions(self, ids: List[int]) -> bool:
        if not ids:
            return True
        try:
            conn = self._get_connection()
            cur = conn.cursor()
            q = ','.join(['?'] * len(ids))
            cur.execute(f"DELETE FROM box_positions WHERE id IN ({q})", ids)
            conn.commit()
            cur.close()
            logger.info(f"删除位置数据 {len(ids)} 条")
            return True
        except sqlite3.Error as e:
            logger.error(f"删除位置数据失败: {e}")
            return False

    def clear_positions(self) -> bool:
        try:
            conn = self._get_connection()
            cur = conn.cursor()
            cur.execute("DELETE FROM box_positions")
            conn.commit()
            cur.close()
            logger.warning("已清空 box_positions 表")
            return True
        except sqlite3.Error as e:
            logger.error(f"清空位置数据失败: {e}")
            return False

    def update_position(self, pid: int, fields: Dict) -> bool:
        if not fields:
            return True
        allowed = {
            'timestamp','drone_id','barcode_data','barcode_type','latitude','longitude','altitude',
            'confidence','bbox_x1','bbox_y1','bbox_x2','bbox_y2'
        }
        sets = []
        values = []
        for k, v in fields.items():
            if k in allowed:
                sets.append(f"{k}=?")
                values.append(v)
        if not sets:
            return True
        values.append(pid)
        try:
            conn = self._get_connection()
            cur = conn.cursor()
            cur.execute(f"UPDATE box_positions SET {', '.join(sets)} WHERE id=?", values)
            conn.commit()
            cur.close()
            return True
        except sqlite3.Error as e:
            logger.error(f"更新位置数据失败: {e}")
            return False

    def clear_drones(self) -> bool:
        try:
            conn = self._get_connection()
            cur = conn.cursor()
            cur.execute("DELETE FROM drone_status")
            conn.commit()
            cur.close()
            logger.warning("已清空 drone_status 表")
            return True
        except sqlite3.Error as e:
            logger.error(f"清空无人机状态失败: {e}")
            return False

    def __del__(self) -> None:  # 防御性关闭
        try:
            self.disconnect()
        except Exception:
            pass


