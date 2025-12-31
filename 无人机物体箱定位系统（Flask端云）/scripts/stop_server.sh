#!/bin/bash
# 无人机物体箱定位系统 - Linux停止脚本

# PID文件路径
PID_FILE="/var/run/drone_positioning.pid"
LOG_FILE="/var/log/drone_positioning/startup.log"

# 函数：打印带时间戳的日志
log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" | sudo tee -a "$LOG_FILE"
}

log "=== 开始停止无人机物体箱定位系统 ==="

# 检查PID文件是否存在
if [ ! -f "$PID_FILE" ]; then
    log "WARNING: PID文件不存在: $PID_FILE"
    
    # 尝试通过进程名查找
    PIDS=$(pgrep -f "python.*app.py")
    if [ -n "$PIDS" ]; then
        log "通过进程名找到运行中的应用进程: $PIDS"
        for PID in $PIDS; do
            log "终止进程: $PID"
            sudo kill -TERM "$PID"
            
            # 等待进程正常退出
            sleep 3
            
            # 如果进程仍在运行，强制终止
            if ps -p "$PID" > /dev/null; then
                log "强制终止进程: $PID"
                sudo kill -KILL "$PID"
            fi
        done
    else
        log "没有找到运行中的应用进程"
    fi
else
    # 读取PID
    PID=$(cat "$PID_FILE")
    log "从PID文件读取到进程ID: $PID"
    
    # 检查进程是否存在
    if ps -p "$PID" > /dev/null; then
        log "进程 $PID 正在运行，开始终止"
        
        # 发送TERM信号
        sudo kill -TERM "$PID"
        log "已发送TERM信号到进程 $PID"
        
        # 等待进程正常退出
        WAIT_COUNT=0
        while ps -p "$PID" > /dev/null && [ $WAIT_COUNT -lt 10 ]; do
            sleep 1
            WAIT_COUNT=$((WAIT_COUNT + 1))
            log "等待进程退出... ($WAIT_COUNT/10)"
        done
        
        # 如果进程仍在运行，强制终止
        if ps -p "$PID" > /dev/null; then
            log "进程未正常退出，强制终止"
            sudo kill -KILL "$PID"
            sleep 1
        fi
        
        # 检查进程是否已终止
        if ps -p "$PID" > /dev/null; then
            log "ERROR: 无法终止进程 $PID"
            exit 1
        else
            log "进程 $PID 已成功终止"
        fi
    else
        log "WARNING: 进程 $PID 不存在或已经停止"
    fi
    
    # 删除PID文件
    sudo rm -f "$PID_FILE"
    log "已删除PID文件: $PID_FILE"
fi

# 清理可能残留的相关进程
REMAINING_PIDS=$(pgrep -f "eventlet|socketio|flask.*app.py")
if [ -n "$REMAINING_PIDS" ]; then
    log "清理残留进程: $REMAINING_PIDS"
    for PID in $REMAINING_PIDS; do
        sudo kill -TERM "$PID" 2>/dev/null
    done
    sleep 2
    
    # 强制清理仍在运行的进程
    REMAINING_PIDS=$(pgrep -f "eventlet|socketio|flask.*app.py")
    if [ -n "$REMAINING_PIDS" ]; then
        for PID in $REMAINING_PIDS; do
            sudo kill -KILL "$PID" 2>/dev/null
        done
    fi
fi

log "=== 系统停止完成 ==="