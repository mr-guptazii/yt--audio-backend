import os
import json
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.utils import platform
from kivy.network.urlrequest import UrlRequest

class DownloaderApp(App):
    def build(self):
        self.layout = BoxLayout(orientation='vertical', padding=20, spacing=10)
        
        self.label = Label(text="🎵 Paste YouTube Playlist/Video Link:")
        self.layout.add_widget(self.label)
        
        self.url_input = TextInput(multiline=False, hint_text="https://music.youtube.com/playlist?list=...")
        self.layout.add_widget(self.url_input)
        
        self.btn = Button(text="Fetch and Download Playlist", size_hint_y=0.3)
        self.btn.bind(on_release=self.send_to_server)
        self.layout.add_widget(self.btn)
        
        return self.layout

    def send_to_server(self, instance):
        url = self.url_input.text.strip()
        if not url:
            self.label.text = "❌ Please enter a link!"
            return

        self.label.text = "📡 Contacting cloud downloader engine..."
        
        # Replace this URL with your actual deployed Render server URL
        server_api = "https://yt-audio-downloader-e6qz.onrender.com/get_stream"
        headers = {'Content-type': 'application/json'}
        params = json.dumps({"url": url})

        # Added timeout=100 to give the free server plenty of time to wake up
        UrlRequest(server_api, req_body=params, req_headers=headers, 
               on_success=self.on_api_success, on_failure=self.on_api_error, on_error=self.on_api_error,
               timeout=100)
    def on_api_success(self, request, result):
        tracks = result.get("tracks", [])
        if not tracks:
            self.label.text = "❌ No audio tracks found in this link."
            return

        self.label.text = f"📥 Processing {len(tracks)} tracks. Downloading straight to device..."
        
        if platform == 'android':
            from android.storage import primary_external_storage_path
            output_folder = os.path.join(primary_external_storage_path(), "Download", "YT_Audio")
        else:
            output_folder = "YT_Audio"

        if not os.path.exists(output_folder):
            os.makedirs(output_folder)

        # Trigger downloads for the direct audio files returned by our server
        for track in tracks:
            title = track['title']
            download_url = track['download_url']
            
            clean_title = "".join([c for c in title if c.isalpha() or c.isdigit() or c==' ']).rstrip()
            file_path = os.path.join(output_folder, f"{clean_title}.m4a")
            
            # Use native downloader to stream the audio file directly into the storage folder
            UrlRequest(download_url, file_path=file_path)

        self.label.text = f"✅ Success! Saved to:\nInternal Storage -> Download -> YT_Audio"

    def on_api_error(self, request, error):
        self.label.text = f"❌ Cloud Server Error: Connection Refused"

if __name__ == '__main__':
    DownloaderApp().run()
