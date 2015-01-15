from datetime import datetime
import os
import subprocess
import sys

here_dir = os.path.dirname(os.path.abspath(__file__))
conf_dir = os.path.dirname(here_dir)
js_dir = os.path.join(conf_dir, 'ofcode', 'static', 'javascripts')
jslist = open(os.path.join(js_dir, 'JSLIST')).read()

home_dir = os.environ['HOME']
yui_bin = os.path.join(here_dir, './yuicompressor-2.4.2.jar')

ini_names = sys.argv[1:]
ini_files = [(open(os.path.join(conf_dir, x)).readlines(), x) for x in ini_names]


# Compress all the JS and store it in a big ol string
combined_js = ''
for f in jslist.split('\n'):
    # Check to see if the database is present
    f = f.strip()
    if not f: continue
    f += '.js'
    fname = os.path.join(js_dir, f)
    print fname
    
    # Compress the file and save the output
    proc = subprocess.Popen(['java', '-jar', yui_bin, '--nomunge', '--preserve-semi', fname],
                            stdout=subprocess.PIPE)
    stdout, stderr = proc.communicate()
    combined_js += stdout + '\n'


# Find the file we're going to write it out to
now = datetime.now()
fname = now.strftime('%m%d%Y')
file_name = fname
for x in range(1,30):
    exists = False
    file_name = 'ofcode-%s.%s-min.js' % (fname, x)
    try:
        stats = os.stat(os.path.join(js_dir, file_name))
        exists = True
    except OSError:
        pass
    if not exists:
        break

# Write it to the file
with open(os.path.join(js_dir, file_name), 'w') as f:
    f.write(combined_js)

# Update the ini file to use the new minified CSS
for ini_file, ini_name in ini_files:
    new_ini = ''
    for line in ini_file:
        if line.startswith('ofcode.minified_js ='):
            new_line = 'ofcode.minified_js = %s\n' % file_name
        else:
            new_line = line
        new_ini += new_line

    nf = open(os.path.join(conf_dir, ini_name), 'w')
    nf.write(new_ini)
