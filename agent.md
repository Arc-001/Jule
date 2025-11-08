Based on your requirements, here's a comprehensive architecture for your Discord bot with dynamic subdomain creation and HTML hosting:

## Architecture Overview

```
┌─────────────────┐
│   Discord User  │
│                 │
└────────┬────────┘
         │
         │ /create <html_content>
         ▼
┌─────────────────────────────────────┐
│       Discord Bot (Node.js/Python)  │
│  ┌───────────────────────────────┐  │
│  │ Command Handler               │  │
│  │ - Validate HTML               │  │
│  │ - Sanitize content            │  │
│  │ - Generate unique subdomain   │  │
│  └───────────────────────────────┘  │
└────────┬────────────────────────────┘
         │
         ├─────────────────┬────────────────┐
         ▼                 ▼                ▼
┌────────────────┐  ┌──────────────┐  ┌──────────────┐
│   DNS API      │  │  File System │  │    Nginx     │
│  (Porkbun)     │  │              │  │    Reload    │
│                │  │              │  │              │
│ Create DNS     │  │ Save HTML to │  │ Reload       │
│ A/CNAME record │  │ /var/www/    │  │ config       │
│ for subdomain  │  │ <user>.info  │  │              │
└────────────────┘  └──────────────┘  └──────────────┘
         │                 │                │
         └─────────────────┴────────────────┘
                           │
                           ▼
                  ┌─────────────────┐
                  │   user.info     │
                  │   .4rc.in       │
                  │                 │
                  │   HTML served   │
                  └─────────────────┘
```

## Detailed Components

### 1. **Discord Bot Layer**
```python
# Example structure (Python with discord.py)
import discord
from discord.ext import commands
import aiohttp
import os

bot = commands.Bot(command_prefix='!')

@bot.command()
async def create(ctx, *, html_content: str):
    user_id = ctx.author.id
    username = ctx.author.name
    
    # 1. Validate & sanitize HTML
    # 2. Generate subdomain: username.info.4rc.in
    # 3. Create DNS record via Porkbun API
    # 4. Save HTML file
    # 5. Update Nginx config
    # 6. Reload Nginx
```

### 2. **DNS Management (Porkbun API)**
```python
async def create_dns_record(subdomain):
    """
    Create DNS A record pointing to your server IP
    or CNAME record pointing to your main domain
    """
    url = "https://porkbun.com/api/json/v3/dns/create/4rc.in"
    payload = {
        "apikey": "YOUR_API_KEY",
        "secretapikey": "YOUR_SECRET_KEY",
        "name": f"{subdomain}.info",  # Creates subdomain.info.4rc.in
        "type": "A",
        "content": "YOUR_SERVER_IP",
        "ttl": "300"
    }
    # Make API request
```

### 3. **File System Structure**
```
/var/www/html/
├── default/                    # Default site
└── user-sites/
    ├── alice.info.4rc.in/
    │   └── index.html
    ├── bob.info.4rc.in/
    │   └── index.html
    └── charlie.info.4rc.in/
        └── index.html
```

### 4. **Nginx Configuration**

**Main config:** `/etc/nginx/nginx.conf`
```nginx
http {
    include /etc/nginx/conf.d/*.conf;
    include /etc/nginx/sites-enabled/*;
}
```

**Dynamic site config:** `/etc/nginx/sites-available/user-sites.conf`
```nginx
# Wildcard subdomain handler
server {
    listen 80;
    server_name ~^(?<subdomain>.+)\.info\.4rc\.in$;
    
    root /var/www/html/user-sites/$subdomain.info.4rc.in;
    index index.html;
    
    # Security headers
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-Content-Type-Options "nosniff" always;
    
    location / {
        try_files $uri $uri/ =404;
    }
    
    # Error handling
    error_page 404 /404.html;
}

# SSL version (recommended)
server {
    listen 443 ssl http2;
    server_name ~^(?<subdomain>.+)\.info\.4rc\.in$;
    
    ssl_certificate /etc/letsencrypt/live/4rc.in/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/4rc.in/privkey.pem;
    
    root /var/www/html/user-sites/$subdomain.info.4rc.in;
    index index.html;
    
    location / {
        try_files $uri $uri/ =404;
    }
}
```

### 5. **Bot Implementation Flow**

```python
import os
import subprocess
import aiohttp
from pathlib import Path

class SubdomainManager:
    def __init__(self, porkbun_api_key, porkbun_secret):
        self.api_key = porkbun_api_key
        self.secret = porkbun_secret
        self.base_path = Path("/var/www/html/user-sites")
        
    async def create_user_site(self, username, html_content):
        # Sanitize username
        safe_username = self.sanitize_username(username)
        subdomain = f"{safe_username}.info.4rc.in"
        
        # 1. Create DNS record
        await self.create_dns_record(safe_username)
        
        # 2. Create directory structure
        site_dir = self.base_path / subdomain
        site_dir.mkdir(parents=True, exist_ok=True)
        
        # 3. Save HTML file
        html_file = site_dir / "index.html"
        html_file.write_text(self.sanitize_html(html_content))
        
        # 4. Set proper permissions
        os.chmod(site_dir, 0o755)
        os.chmod(html_file, 0o644)
        
        # 5. Reload Nginx (optional, wildcard config auto-handles)
        # subprocess.run(["sudo", "nginx", "-s", "reload"])
        
        return subdomain
    
    async def create_dns_record(self, username):
        async with aiohttp.ClientSession() as session:
            url = "https://porkbun.com/api/json/v3/dns/create/4rc.in"
            payload = {
                "apikey": self.api_key,
                "secretapikey": self.secret,
                "name": f"{username}.info",
                "type": "A",
                "content": "YOUR_SERVER_IP",
                "ttl": "300"
            }
            async with session.post(url, json=payload) as resp:
                return await resp.json()
    
    def sanitize_username(self, username):
        # Remove special characters, lowercase
        return ''.join(c for c in username.lower() if c.isalnum() or c == '-')
    
    def sanitize_html(self, html):
        # Basic sanitization (consider using bleach library)
        # Add your HTML sanitization logic here
        return html

# Discord bot command
@bot.command()
async def create(ctx, *, html_content: str):
    await ctx.send("Creating your site...")
    
    manager = SubdomainManager(API_KEY, SECRET_KEY)
    try:
        subdomain = await manager.create_user_site(
            ctx.author.name, 
            html_content
        )
        await ctx.send(f"✅ Your site is live at: https://{subdomain}")
    except Exception as e:
        await ctx.send(f"❌ Error: {str(e)}")
```

## Key Considerations

### **Security:**
1. **HTML Sanitization**: Use libraries like `bleach` to prevent XSS
2. **Rate Limiting**: Prevent abuse
3. **Content Validation**: Check file size, malicious scripts
4. **User Authentication**: Track who created what

### **Permissions:**
```bash
# Bot needs sudo access for nginx reload (if needed)
# Or use wildcard config to avoid reloads
sudo visudo
# Add: botuser ALL=(ALL) NOPASSWD: /usr/sbin/nginx -s reload
```

### **SSL/TLS:**
```bash
# Use certbot for wildcard certificate
sudo certbot certonly --manual --preferred-challenges=dns \
  -d "*.info.4rc.in" -d "4rc.in"
```

### **Alternative: Database Tracking**
```sql
CREATE TABLE user_sites (
    id SERIAL PRIMARY KEY,
    discord_id BIGINT,
    username VARCHAR(100),
    subdomain VARCHAR(100) UNIQUE,
    created_at TIMESTAMP DEFAULT NOW(),
    last_updated TIMESTAMP
);
```

Would you like me to provide more detailed code for any specific component, or help you set up the actual implementation?