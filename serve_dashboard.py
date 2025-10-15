#!/usr/bin/env python3
"""
IPOP Dashboard Server
====================

Simple HTTP server to serve the web UI dashboard.
"""

import http.server
import socketserver
import webbrowser
import os
import sys
from pathlib import Path

def serve_dashboard():
    """Serve the IPOP dashboard on localhost:3000"""
    
    # Change to the directory containing the dashboard
    dashboard_dir = Path(__file__).parent
    os.chdir(dashboard_dir)
    
    # Check if dashboard file exists
    dashboard_file = dashboard_dir / "web_ui_dashboard.html"
    if not dashboard_file.exists():
        print("❌ Dashboard file not found: web_ui_dashboard.html")
        return
    
    PORT = 3000
    
    class CustomHTTPRequestHandler(http.server.SimpleHTTPRequestHandler):
        def end_headers(self):
            # Add CORS headers to allow API calls
            self.send_header('Access-Control-Allow-Origin', '*')
            self.send_header('Access-Control-Allow-Methods', 'GET, POST, PUT, DELETE, OPTIONS')
            self.send_header('Access-Control-Allow-Headers', 'Content-Type, Authorization')
            super().end_headers()
        
        def do_OPTIONS(self):
            # Handle preflight requests
            self.send_response(200)
            self.end_headers()
    
    try:
        with socketserver.TCPServer(("", PORT), CustomHTTPRequestHandler) as httpd:
            print("🚀 IPOP Dashboard Server Starting...")
            print("=" * 50)
            print(f"📊 Dashboard URL: http://localhost:{PORT}/web_ui_dashboard.html")
            print(f"🔗 API Base URL: http://localhost:8000")
            print(f"🗄️  MongoDB Express: http://localhost:8081")
            print("=" * 50)
            print("🎯 Dashboard Features:")
            print("   • Create campaigns with configurable parameters")
            print("   • Real-time metrics monitoring")
            print("   • AI optimization decisions")
            print("   • Live activity logging")
            print("=" * 50)
            print("Press Ctrl+C to stop the server")
            print()
            
            # Open dashboard in browser
            dashboard_url = f"http://localhost:{PORT}/web_ui_dashboard.html"
            print(f"🌐 Opening dashboard in browser: {dashboard_url}")
            webbrowser.open(dashboard_url)
            
            # Start server
            httpd.serve_forever()
            
    except KeyboardInterrupt:
        print("\n🛑 Dashboard server stopped")
    except OSError as e:
        if e.errno == 10048:  # Port already in use
            print(f"❌ Port {PORT} is already in use. Please stop other servers or use a different port.")
        else:
            print(f"❌ Server error: {e}")

if __name__ == "__main__":
    serve_dashboard()
