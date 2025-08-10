#!/bin/bash

# Interactive Ohmni Robot Control
# Real-time control with keyboard

ROBOT_IP="172.16.215.191"
NODE_PATH="/data/data/com.ohmnilabs.telebot_rtc/files/assets/node-files"

# Power settings (adjustable)
POWER=2000
TURN_POWER=1500

NECK_POWER=1500

send_command() {
    local cmd="$1"
    adb shell "su -c 'cd $NODE_PATH && echo \"$cmd\" | ./node bot_shell_client.js'" > /dev/null 2>&1
}

# Send synchronized wheel commands
send_dual_wheel() {
    local left_speed="$1"
    local right_speed="$2"
    # Send both commands in a single connection for perfect sync
    adb shell "su -c 'cd $NODE_PATH && (echo \"rot 0 $left_speed\"; echo \"rot 1 $right_speed\") | ./node bot_shell_client.js'" > /dev/null 2>&1
}

echo "🤖 Ohmni Robot Interactive Control"
echo "=================================="
echo "Controls:"
echo "  w - Move Forward"
echo "  s - Move Backward" 
echo "  a - Turn Left"
echo "  d - Turn Right"
echo "  q - STOP (Emergency)"
echo "  u - Neck Up"
echo "  j - Neck Down"
echo "  c - Center Neck"
echo "  l - LED On"
echo "  o - LED Off"
echo "  + - Increase Power"
echo "  - - Decrease Power"
echo "  p - Show Power Settings"
echo "  x - Exit"
echo ""
echo "⚠️  SAFETY: Keep 'q' ready to stop! Make sure robot has clear space!"
echo ""
echo "📊 Starting Power Settings: Drive=$POWER, Turn=$TURN_POWER, Neck=$NECK_POWER"
echo ""

# Enable torque on startup
send_command "torque 0 on"
send_command "torque 1 on"
send_command "torque 3 on"

while true; do
    echo -n "Enter command: "
    read -n 1 cmd
    echo ""
    
    case $cmd in
        w)
            echo "🔼 Moving forward..."
            send_dual_wheel -$POWER $POWER
            ;;
        s)
            echo "🔽 Moving backward..."
            send_dual_wheel $POWER -$POWER
            ;;
        a)
            echo "◀️ Turning left..."
            send_dual_wheel -$TURN_POWER -$TURN_POWER
            ;;
        d)
            echo "▶️ Turning right..."
            send_dual_wheel $TURN_POWER $TURN_POWER
            ;;
        q)
            echo "🛑 STOPPING..."
            send_dual_wheel 0 0
            ;;
        u)
            echo "🔺 Neck up..."
            send_command "rot 3 -60"
            ;;
        j)
            echo "🔻 Neck down..."
            send_command "rot 3 -30"
            ;;
        c)
            echo "🎯 Centering neck..."
            send_command "torque 3 off"
            ;;
        l)
            echo "💡 LED on..."
            send_command "led 20 on"
            ;;
        o)
            echo "🌑 LED off..."
            send_command "led 20 off"
            ;;
        +)
            POWER=$((POWER + 50))
            TURN_POWER=$((TURN_POWER + 25))
            NECK_POWER=$((NECK_POWER + 10))
            echo "⚡ Power increased: Drive=$POWER, Turn=$TURN_POWER, Neck=$NECK_POWER"
            ;;
        -)
            if [ $POWER -gt 50 ]; then
                POWER=$((POWER - 50))
                TURN_POWER=$((TURN_POWER - 25))
                NECK_POWER=$((NECK_POWER - 10))
                echo "🔋 Power decreased: Drive=$POWER, Turn=$TURN_POWER, Neck=$NECK_POWER"
            else
                echo "⚠️ Power already at minimum safe level"
            fi
            ;;
        p)
            echo "📊 Current Power Settings:"
            echo "   Drive Power: $POWER"
            echo "   Turn Power: $TURN_POWER" 
            echo "   Neck Power: $NECK_POWER"
            ;;
        x)
            echo "🛑 Stopping and exiting..."
            send_command "rot 0 0"
            send_command "rot 1 0"
            send_command "torque 0 off"
            send_command "torque 1 off"
            send_command "torque 3 off"
            echo "👋 Goodbye!"
            exit 0
            ;;
        *)
            echo "❓ Unknown command: $cmd"
            ;;
    esac
    
    sleep 0.2  # Small delay for safety
done
