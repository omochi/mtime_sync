# mtime_sync

helper tool to treat modified time with file sharing service such git

# using

Put this script in your repository.

Before you commit, store mtime to meta file.

~~~
$ mtime_sync.py store
~~~

After you checkout, apply mtime stored in meta file to file.

~~~
$ mtime_sync.py load
~~~

Script traverses directory tree from current directory.
And put meta file in each directory.

Ofcoruse you can run script by hook script.


