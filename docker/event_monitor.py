from subprocess import Popen, PIPE, STDOUT

p = Popen(['docker', 'events'], stdout=PIPE, bufsize=1)
for line in iter(p.stdout.readline, b''):
    print(line)
p.stdout.close()
p.wait()
