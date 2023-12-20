PORT="5555"
COMMAND_GET_DEVICE="adb shell ifconfig wlan0 | grep \"inet addr\" | cut -d: -f2 | cut -d\" \" -f1"

ALL_APPS=([0]="com.whatsapp" [1]="com.spotify.music" [2]="com.instagram.android" [3]="com.mgoogle.android.gms" [4]="com.mgoogle.android.gms  com.whatsapp  photo.editor.photoeditor.photoeditorpro" [5]="com.mgoogle.android.gms com.spotify.music com.whatsapp  photo.editor.photoeditor.photoeditorpro" [6]="com.updateme" [7]="com.lemon.lvoverseas" [8]="com.hdobox" [9]="app.revanced.android.youtube" [10]="app.revanced.android.apps.youtube.music")

function uninstall_apps() {
    echo -n "Do you want to uninstall all apps? [y/n] "
    read
    if [ "$REPLY" == "y" ]; then
        for app in "${ALL_APPS[@]}"
        do
            adb uninstall $app 2> /dev/null 1> /dev/null > /dev/null &
        done
    fi
}

function connect_scrcpy() {
    echo -n "Do you want to start scrcpy? [y/n] "
    read
    if [ "$REPLY" == "y" ]; then
        nohup scrcpy > /dev/null 2>&1 &
        rm -f nohup.out
    fi
}

function animate() {
    while true; do
        echo -ne "\r[     ] $@"
        sleep 0.2
        echo -ne "\r[ .   ] $@"
        sleep 0.2
        echo -ne "\r[ ..  ] $@"
        sleep 0.2
        echo -ne "\r[ ... ] $@"
        sleep 0.2
        echo -ne "\r[  .. ] $@"
        sleep 0.2
        echo -ne "\r[   . ] $@"
        sleep 0.2
    done
}

function wait_usb_disconnect() {
    while true ; do
        STILL_CONNECTED=$(eval "adb devices | grep -v List | grep device")
        if [ -z "$STILL_CONNECTED" ]; then
            break
        fi
        sleep 1
    done
}

function wait_usb_connect() {
    adb wait-for-device
}

function runFunction () {
    FUNCTION=$1
    MESSAGE=$2
    animate $MESSAGE &
    ANIMATE_PID=$!
    $FUNCTION > /dev/null 2>&1
    kill $ANIMATE_PID
    echo ""
}

adb disconnect > /dev/null 2>&1
adb kill-server > /dev/null 2>&1
adb start-server > /dev/null 2>&1
runFunction wait_usb_connect "Waiting for USB connect"
IP=$(eval $COMMAND_GET_DEVICE)
adb tcpip $PORT > /dev/null 2>&1
runFunction wait_usb_disconnect "Waiting for USB disconnect"
adb connect $IP:$PORT > /dev/null 2>&1
connect_scrcpy
uninstall_apps