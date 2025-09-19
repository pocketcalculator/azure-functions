#!/usr/bin/env python3
"""
Event Hub message sender for testing the Azure Function
"""

import asyncio
import json
import os
from azure.eventhub.aio import EventHubProducerClient
from azure.eventhub import EventData
from datetime import datetime
import argparse

async def send_sample_messages():
    """Send sample messages to Event Hub"""
    
    # Get connection details from environment
    connection_str = os.environ.get('EVENT_HUB_CONNECTION_STRING')
    eventhub_name = os.environ.get('EVENT_HUB_NAME', 'msfthack2025iothub')
    
    if not connection_str:
        print("❌ EVENT_HUB_CONNECTION_STRING environment variable not found")
        print("Make sure to set it in your environment or local.settings.json")
        return False
    
    print(f"Connecting to Event Hub: {eventhub_name}")
    
    try:
        # Load sample data
        with open('sample_eventhub_data.json', 'r') as f:
            data = json.load(f)
        
        producer = EventHubProducerClient.from_connection_string(
            conn_str=connection_str,
            eventhub_name=eventhub_name
        )
        
        async with producer:
            print(f"\n📤 Sending {len(data['sample_eventhub_messages'])} sample messages...")
            
            for i, message in enumerate(data['sample_eventhub_messages'], 1):
                # Add current timestamp to data
                if 'data' in message and isinstance(message['data'], dict):
                    message['data']['sent_at'] = datetime.utcnow().isoformat()
                
                # Create event batch
                event_data_batch = await producer.create_batch()
                
                # Add message to batch
                message_json = json.dumps(message)
                event_data_batch.add(EventData(message_json))
                
                # Send the batch
                await producer.send_batch(event_data_batch)
                
                print(f"✅ Sent message {i}: {message.get('name', message.get('id', 'Unknown'))}")
                
                # Small delay between messages
                await asyncio.sleep(1)
        
        print(f"\n🎉 Successfully sent all {len(data['sample_eventhub_messages'])} messages!")
        return True
        
    except FileNotFoundError:
        print("❌ sample_eventhub_data.json not found!")
        return False
        
    except Exception as e:
        print(f"❌ Error sending messages: {str(e)}")
        return False

async def send_malformed_messages():
    """Send malformed messages to test error handling"""
    
    connection_str = os.environ.get('EVENT_HUB_CONNECTION_STRING')
    eventhub_name = os.environ.get('EVENT_HUB_NAME', 'msfthack2025iothub')
    
    if not connection_str:
        print("❌ EVENT_HUB_CONNECTION_STRING environment variable not found")
        return False
    
    try:
        with open('sample_eventhub_data.json', 'r') as f:
            data = json.load(f)
        
        producer = EventHubProducerClient.from_connection_string(
            conn_str=connection_str,
            eventhub_name=eventhub_name
        )
        
        async with producer:
            print(f"\n📤 Sending {len(data['malformed_messages'])} malformed messages for error testing...")
            
            for i, message in enumerate(data['malformed_messages'], 1):
                event_data_batch = await producer.create_batch()
                
                # Send the malformed message as-is (not JSON encoded if it's already a string)
                if isinstance(message, str):
                    event_data_batch.add(EventData(message))
                else:
                    event_data_batch.add(EventData(str(message)))
                
                await producer.send_batch(event_data_batch)
                
                print(f"⚠️  Sent malformed message {i}: {str(message)[:50]}...")
                await asyncio.sleep(1)
        
        print(f"\n✅ Sent all malformed messages for error testing!")
        return True
        
    except Exception as e:
        print(f"❌ Error sending malformed messages: {str(e)}")
        return False

async def send_custom_message(message_data):
    """Send a custom message"""
    
    connection_str = os.environ.get('EVENT_HUB_CONNECTION_STRING')
    eventhub_name = os.environ.get('EVENT_HUB_NAME', 'msfthack2025iothub')
    
    if not connection_str:
        print("❌ EVENT_HUB_CONNECTION_STRING environment variable not found")
        return False
    
    try:
        producer = EventHubProducerClient.from_connection_string(
            conn_str=connection_str,
            eventhub_name=eventhub_name
        )
        
        async with producer:
            event_data_batch = await producer.create_batch()
            event_data_batch.add(EventData(json.dumps(message_data)))
            
            await producer.send_batch(event_data_batch)
            print(f"✅ Sent custom message: {message_data.get('name', message_data.get('id', 'Custom Message'))}")
            return True
            
    except Exception as e:
        print(f"❌ Error sending custom message: {str(e)}")
        return False

def load_env_from_local_settings():
    """Load environment variables from local.settings.json"""
    try:
        with open('local.settings.json', 'r') as f:
            settings = json.load(f)
            for key, value in settings.get('Values', {}).items():
                os.environ[key] = value
        print("✅ Loaded environment variables from local.settings.json")
    except FileNotFoundError:
        print("⚠️  local.settings.json not found, using system environment variables")
    except Exception as e:
        print(f"⚠️  Error loading local.settings.json: {e}")

async def main():
    """Main function"""
    parser = argparse.ArgumentParser(description='Send test messages to Event Hub')
    parser.add_argument('--malformed', action='store_true', 
                       help='Send malformed messages for error testing')
    parser.add_argument('--custom', type=str, 
                       help='Send custom JSON message (provide as JSON string)')
    
    args = parser.parse_args()
    
    print("Event Hub Message Sender")
    print("=" * 40)
    
    # Load environment variables from local.settings.json
    load_env_from_local_settings()
    
    if args.custom:
        try:
            custom_data = json.loads(args.custom)
            await send_custom_message(custom_data)
        except json.JSONDecodeError:
            print("❌ Invalid JSON in custom message")
    elif args.malformed:
        await send_malformed_messages()
    else:
        await send_sample_messages()

if __name__ == "__main__":
    asyncio.run(main())