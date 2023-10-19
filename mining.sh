echo "Generating a block every 30 seconds. "

while true; do
    bitcoin-cli -regtest -rpcwallet=miningwallet -generate 1
    sleep 30
done