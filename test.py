import time
import requests
import random
import string
import base64

class WakuNode:
    def __init__(self, name, port):
        self.name = name
        self.port = port

    def wait_for_peers(self, expected_peers, timeout=10):
        url = f"http://localhost:{self.port}/admin/v1/peers"
        start_time = time.time()
        while True:
            try:
                response = requests.get(url)
                if response.status_code == 200:
                    peers = response.json()
                    if len(peers) >= expected_peers:
                        print(f"✅ {self.name} has {len(peers)} peers")
                        break
            except requests.exceptions.RequestException:
                pass
            if time.time() - start_time > timeout:
                print(f"⏰ Timeout waiting for peers on {self.name}")
                break
            time.sleep(1)

    def subscribe_to_topic(self, pubsub_topic, content_topic):
        url = f"http://localhost:{self.port}/filter/v2/subscriptions"
        payload = {
            "requestId": "2",
            "pubsubTopic": pubsub_topic,
            "contentFilters": [content_topic]
        }
        response = requests.post(url, json=payload)
        response.raise_for_status()
        print(f"🔔 {self.name} subscribed to topic {content_topic}")

    def send_message(self, pubsub_topic, content_topic, message):
        url = f"http://localhost:{self.port}/lightpush/v1/message"
        encoded_message = base64.b64encode(message.encode()).decode()
        payload = {
            "pubsubTopic": pubsub_topic,
            "message": {
            "payload": encoded_message,
            "contentTopic": content_topic,
            "version": 0,
            "timestamp": 0,
            "ephemeral": False,
            "meta": ""
            }
        }
        response = requests.post(url, json=payload)
        response.raise_for_status()
        print(f"📤 {self.name} sent message: {message}")

    def receive_message(self, content_topic):
        escaped_pubsub_topic = content_topic.replace("/", "%2F")
        url = f"http://localhost:{self.port}/filter/v2/messages/{escaped_pubsub_topic}"
        while True:
            try:
                response = requests.get(url)
                if response.status_code != 200:
                    continue
                messages = response.json()
                for msg in messages:
                    if msg["contentTopic"] != content_topic:
                        continue
                    decoded_message = base64.b64decode(msg["payload"]).decode()
                    print(f"📥 {self.name} received message: {decoded_message}")
                    return decoded_message
            except requests.exceptions.RequestException:
                pass
            time.sleep(1)

def generate_random_message(length=10):
    letters = string.ascii_letters
    return ''.join(random.choice(letters) for i in range(length))

def main():
    pubsub_topic = "/waku/2/rs/16/32"
    content_topic = "/example-app/1/chat/json"
    message = "Hello, Waku!"    

    boot1 = WakuNode("boot-1", 8646)
    boot2 = WakuNode("boot-2", 8647)
    lightpush_client = WakuNode("lightpush-client", 8649)
    filter_client = WakuNode("filter-client", 8650)

    # Wait for peers
    boot1.wait_for_peers(1)
    boot2.wait_for_peers(1)
    lightpush_client.wait_for_peers(1)
    filter_client.wait_for_peers(1)

    # Subscribe to topic
    filter_client.subscribe_to_topic(pubsub_topic, content_topic)

    # Send message
    lightpush_client.send_message(pubsub_topic, content_topic, message)

    # Receive message
    received_message = filter_client.receive_message(content_topic)
    assert received_message == message, f"Expected '{message}', but got '{received_message}'"

    print("🎉 Test passed!")

if __name__ == "__main__":
    main()
