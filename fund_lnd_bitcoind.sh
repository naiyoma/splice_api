# We will like to credit the https://github.com/nostrassets folks
# for this script. I haven't modified it because it works perfectly
# for our intend and purposes.

# Generate init blocks and create wallet
echo "Start create wallet and generate 240 blocks"
sudo docker exec -it -u bitcoin bitcoind-backend bitcoin-cli -regtest createwallet "miningwallet"
sudo docker exec -it -u bitcoin bitcoind-backend bitcoin-cli -regtest -rpcwallet=miningwallet -generate 480
echo "======== finish generate init blocks ========"
sleep 5

# setup Alice
echo "======== start send btc to alice ========"

# create alice wallet
alice=`sudo docker exec -it -u lnd alice-lnd lncli --network=regtest newaddress p2tr`
alice=$(echo $alice | awk -F'"' '{print $4}')
echo "alice address => $alice"

sudo docker exec -it -u bitcoin bitcoind-backend bitcoin-cli -regtest -rpcwallet=miningwallet sendtoaddress $alice 1000
sudo docker exec -it -u bitcoin bitcoind-backend bitcoin-cli -regtest -rpcwallet=miningwallet -generate 6

echo "======== finish send btc to alice ($alice) ========"
sleep 5

# start auto mining
echo "copy mining.sh to backend and start mining"
# copy mining.sh to backend
cp ./mining.sh ./volumes/bitcoind/backend/regtest/
# start mining
sudo docker exec -d -u bitcoin bitcoind-backend bash "/home/bitcoin/.bitcoin/regtest/mining.sh"
echo "finish start auto mining"
sleep 3