#!/bin/bash -xe

FLAG=${FLAG:-"flag{this_is_a_fake_flag}"}

echo -n $FLAG > /flag
unset FLAG

function start() {
    su bot -c 'exec python bot.py'
}

start &

while inotifywait -e modify,create,delete -r ./src ./bot.py || true; do
    su bot -c 'kill -TERM -1' && wait
    start &
done