"""
WhatsApp Bot Module for OptiSend
Handles all WhatsApp Web automation logic
"""

import time
import threading
import urllib.parse
import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager


class WhatsAppBot(threading.Thread):
    """WhatsApp automation bot running in separate thread"""

    def __init__(self, csv_file, message_template, delay,
                 log_callback, progress_callback, finished_callback):
        """
        Initialize WhatsApp bot

        Args:
            csv_file: Path to CSV file with contacts
            message_template: Message template with {name} placeholder
            delay: Delay between messages in seconds
            log_callback: Function to call for logging
            progress_callback: Function to call with progress (current, total)
            finished_callback: Function to call when finished
        """
        super().__init__(daemon=True)

        self.csv_file = csv_file
        self.message_template = message_template
        self.delay = delay
        self.log = log_callback
        self.update_progress = progress_callback
        self.on_finish = finished_callback

        self.driver = None
        self.should_stop = False

    def run(self):
        """Main execution thread"""
        try:
            self.initialize_browser()
            self.login_whatsapp()
            self.send_messages()

        except Exception as e:
            self.log(f"❌ Critical Error: {str(e)}")

        finally:
            self.cleanup()
            self.on_finish()

    def initialize_browser(self):
        """Initialize Chrome browser with WhatsApp Web"""
        self.log("🌐 Initializing browser...")

        try:
            chrome_options = Options()
            chrome_options.add_argument("--start-maximized")
            chrome_options.add_argument("--disable-notifications")
            chrome_options.add_argument("--disable-popup-blocking")
            chrome_options.add_experimental_option("excludeSwitches", ["enable-logging"])

            # Suppress WebDriver logs
            chrome_options.add_argument("--log-level=3")

            self.driver = webdriver.Chrome(
                service=Service(ChromeDriverManager().install()),
                options=chrome_options
            )

            self.log("✓ Browser initialized successfully")

        except Exception as e:
            raise Exception(f"Failed to initialize browser: {str(e)}")

    def login_whatsapp(self):
        """Navigate to WhatsApp Web and wait for QR scan"""
        self.log("📱 Opening WhatsApp Web...")

        try:
            self.driver.get("https://web.whatsapp.com")
            self.log("⏳ Please scan QR code to login (20 seconds)...")
            time.sleep(20)  # Wait for user to scan QR code
            self.log("✓ Login successful")

        except Exception as e:
            raise Exception(f"Failed to login to WhatsApp: {str(e)}")

    def send_messages(self):
        """Process CSV and send messages"""
        self.log("📊 Loading contacts from CSV...")

        try:
            # Load and prepare CSV
            df = pd.read_csv(self.csv_file)
            df.columns = df.columns.str.strip().str.lower()

            # Validate required columns
            if 'name' not in df.columns or 'number' not in df.columns:
                raise Exception("CSV must contain 'name' and 'number' columns")

            total = len(df)
            self.log(f"✓ Loaded {total} contacts")

            sent_count = 0
            failed_count = 0

            # Process each contact
            for index, row in df.iterrows():
                if self.should_stop:
                    self.log("⏹ Campaign stopped by user")
                    break

                name = str(row.get("name", "Friend")).strip()
                phone = str(row.get("number", "")).strip()

                # Skip invalid contacts
                if not phone or phone == "nan":
                    self.log(f"⚠️ Skipped: {name} (no phone number)")
                    continue

                # Format phone number
                phone = self.format_phone_number(phone)

                # Send message
                success = self.send_single_message(name, phone)

                if success:
                    sent_count += 1
                    self.log(f"✅ Sent to {name} ({phone})")
                else:
                    failed_count += 1
                    self.log(f"❌ Failed: {name} ({phone})")

                # Update progress
                self.update_progress(sent_count + failed_count, total)

                # Delay before next message
                if index < len(df) - 1:  # Don't delay after last message
                    time.sleep(self.delay)

            # Summary
            self.log("=" * 50)
            self.log(f"📊 Campaign Summary:")
            self.log(f"   Total Contacts: {total}")
            self.log(f"   ✅ Sent: {sent_count}")
            self.log(f"   ❌ Failed: {failed_count}")
            self.log("=" * 50)

        except Exception as e:
            raise Exception(f"Error processing messages: {str(e)}")

    def format_phone_number(self, phone):
        """
        Format phone number for WhatsApp
        Assumes Ghana (+233) country code
        """
        # Remove any non-digit characters
        phone = ''.join(filter(str.isdigit, phone))

        # Handle Ghanaian numbers
        if phone.startswith("0") and len(phone) == 10:
            phone = "233" + phone[1:]  # Replace leading 0 with 233
        elif len(phone) == 9:
            phone = "233" + phone  # Add 233 prefix

        return phone

    def send_single_message(self, name, phone):
        """
        Send a single message via WhatsApp Web

        Returns:
            bool: True if successful, False otherwise
        """
        try:
            # Format message with personalization
            message = self.message_template.format(name=name)
            encoded_message = urllib.parse.quote(message)

            # Construct WhatsApp URL
            url = f"https://web.whatsapp.com/send?phone={phone}&text={encoded_message}"

            # Navigate to chat
            self.driver.get(url)
            time.sleep(8)  # Wait for chat to load

            # Find and click send button
            try:
                # Try multiple XPath selectors for send button
                selectors = [
                    '//button[@aria-label="Send"]',
                    '//button[contains(@aria-label, "Send")]',
                    '//span[@data-icon="send"]',
                ]

                send_button = None
                for selector in selectors:
                    try:
                        send_button = self.driver.find_element(By.XPATH, selector)
                        break
                    except:
                        continue

                if send_button:
                    send_button.click()
                    time.sleep(2)  # Wait for message to send
                    return True
                else:
                    return False

            except Exception as e:
                return False

        except Exception as e:
            return False

    def stop(self):
        """Stop the campaign"""
        self.should_stop = True

    def cleanup(self):
        """Cleanup resources"""
        self.log("🧹 Cleaning up...")

        if self.driver:
            try:
                self.driver.quit()
                self.log("✓ Browser closed")
            except:
                pass