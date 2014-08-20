## Usage

Getting started with the build pack is simple.  It's designed to be easy to use and minimally invasive.  For a quick start, see the [30 Second Tutorial].  This document will go into further detail and explain the more advanced options.

### Folder Structure

The easiest way to use the build pack is to put your assets and PHP files into a directory and push it to CloudFoundry.  When you do this, the build pack will take your files and automatically move them into the `htdocs` folder, which is the directory where your chosen web server looks for the files.

This works great for most situations, but does have some limitations.  Specifically, it will put all of your files into a publicly accessible directory.  In some cases, you might want to have PHP files that are not publicly accessible but are on the [include_path].  To do that, you simply create a `lib` directory in your project folder and place your protected files there.

Example:

```bash
$ ls -lRh
total 0
-rw-r--r--  1 daniel  staff     0B Feb 27 21:40 images
-rw-r--r--  1 daniel  staff     0B Feb 27 21:39 index.php
drwxr-xr-x  3 daniel  staff   102B Feb 27 21:40 lib

./lib:
total 0
-rw-r--r--  1 daniel  staff     0B Feb 27 21:40 my.class.php  <-- not public, http://app.cfapps.io/lib/my.class.php == 404
```

This comes with a catch.  If your project legitimately has a `lib` directory, these files will not be publicly available because the build pack does not copy a top-level `lib` directory into the `htdocs` folder.  If your project has a `lib` directory that needs to be publicly available then you need to make a couple additional adjustments to your application.  

Example:

```bash
$ ls -lRh
total 0
drwxr-xr-x  7 daniel  staff   238B Feb 27 21:48 htdocs

./htdocs:  <--  create the htdocs directory and put your files there
total 0
-rw-r--r--  1 daniel  staff     0B Feb 27 21:40 images
-rw-r--r--  1 daniel  staff     0B Feb 27 21:39 index.php
drwxr-xr-x  3 daniel  staff   102B Feb 27 21:48 lib

./htdocs/lib:   <--  anything under htdocs is public, including a lib directory
total 0
-rw-r--r--  1 daniel  staff     0B Feb 27 21:48 controller.php
```

The first step is to create an `htdocs` folder under your project directory.  Then move any files that should be publicly accessible into this directory.  In the example above, the `lib/controller.php` file is publicly accessible.

Given this setup, it is possible to have both a public `lib` directory and a protected `lib` directory.  Here's an example of that setup.

Example:

```bash
$ ls -lRh
total 0
drwxr-xr-x  7 daniel  staff   238B Feb 27 21:48 htdocs
drwxr-xr-x  3 daniel  staff   102B Feb 27 21:51 lib

./htdocs:
total 0
-rw-r--r--  1 daniel  staff     0B Feb 27 21:40 images
-rw-r--r--  1 daniel  staff     0B Feb 27 21:39 index.php
drwxr-xr-x  3 daniel  staff   102B Feb 27 21:48 lib

./htdocs/lib:  <-- public lib directory
total 0
-rw-r--r--  1 daniel  staff     0B Feb 27 21:48 controller.php

./lib: <-- protected lib directory
total 0
-rw-r--r--  1 daniel  staff     0B Feb 27 21:51 my.class.php
```

Beyond the `htdocs` and `lib` directories, the build pack also supports a `.bp-config` directory.  This directory should also exist at the root of your project directory and it is the location of application specific configuration files.  Application specific configuration files override the default settings used by the build pack.  This link explains [application configuration files] in depth.

[30 Second Tutorial]:https://github.com/dmikusa-pivotal/cf-php-build-pack#30-second-tutorial
[application configuration files]:https://github.com/dmikusa-pivotal/cf-php-build-pack/blob/master/docs/config.md
[include_path]:http://us1.php.net/manual/en/ini.core.php#ini.include-path
