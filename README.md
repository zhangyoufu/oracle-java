# Features

* no "hard" dependency on audio/cups/ffmpeg/font/png/smartcard

  It's up to you to decide which package is necessary.

* support `update-java-alternatives`

  You can easily change default JVM between Oracle Java and OpenJDK packages from distro.

* support `update-ca-certificates`

  The `oracle-java-XX-cacerts` package replaces JRE cacerts bundle with ca-certificates from your distro. If you want to trust some 3rd-party CA, just put it at correct location and run `update-ca-certificates`.

# Usage

1. download public key

   ```
   # wget -nv -O /etc/apt/oracle-java.gpg https://zhangyoufu.github.io/oracle-java/oracle-java.gpg
   ```
   or
   ```
   # curl -fsSL -o /etc/apt/oracle-java.gpg https://zhangyoufu.github.io/oracle-java/oracle-java.gpg
   ```

1. configure APT repository

   ```
   # cat >/etc/apt/sources.list.d/oracle-java.sources <<EOF
   Types: deb
   URIs: https://zhangyoufu.github.io/oracle-java
   Suites: any
   Components: stable
   Architectures: amd64
   Signed-By: /etc/apt/oracle-java.gpg
   EOF
   ```
   or
   ```
   echo 'deb [arch=amd64, signed-by=/etc/apt/oracle-java.gpg] https://zhangyoufu.github.io/oracle-java any stable' >/etc/apt/sources.list.d/oracle-java.list
   ```

   Note: You have to install `apt-transport-https` if you're using Ubuntu < 18.04 or Debian < 10.

1. install packages

   ```
   # apt update
   # apt install oracle-java-8-jre-headless oracle-java-8-cacerts
   ```

# Available Packages

## Java SE 8 (LTS)

* oracle-java-8-jre-headless
* oracle-java-8-jdk-headless
* oracle-java-8-jre
* oracle-java-8-jdk
* oracle-java-8-source
* oracle-java-8-cacerts
* oracle-java-8-javafx
* oracle-java-8-javafx-runtime
* oracle-java-8-javafx-source
* oracle-java-8-visualvm

## Java 11 (LTS)

* oracle-java-11-jre-headless
* oracle-java-11-jdk-headless
* oracle-java-11-jre
* oracle-java-11-jdk
* oracle-java-11-source
* oracle-java-11-cacerts

## Java 14

* oracle-java-14-jre-headless
* oracle-java-14-jdk-headless
* oracle-java-14-jre
* oracle-java-14-jdk
* oracle-java-14-source
* oracle-java-14-cacerts

# Q&A

* jexec does not work. can't locate java: No such file or directory

  Try /usr/bin/jexec, jexec has to be invoked using absolute/relative path.
  Apparently jexec should never be symlinked under bin/ folder.

* Why not `${shlibs:Depends}`?

  There are `dlopen`/`dlsym` calls which `dh_shlibdeps` cannot handle correctly.
  Some shared libraries are listed as `Recommends`/`Suggests` (without minimum
  version constraint).

* Why not `binfmt-support`?

  `binfmt-support` does not support switching between versions. OpenJDK package
  in Debian/Ubuntu creates a symbolic link from `/usr/share/binfmts/jar` to
  `${JDK}/lib/jar.binfmt`, which is a slave link of `/usr/bin/jexec`. Although
  `/usr/bin/jexec` can be switched by `update-java-alternatives`, it leaves
  inconsistency in `binfmt-support` database.
  `binfmt-misc` is also useless for containers due to lack of namespace support
  at the time of writing.

* Your manpages are not gzipped.

  I don't care Debian packaging policy.

* Why did you removed localized man pages?

  Only Japanese available in JDK 8, doesn't worth packaging.

* Why did you removed GNOME icons, desktop/mime entries?

  Only available in JDK 8, doesn't worth packaging.

* How about browser plugin?

  Read [this](https://docs.oracle.com/javase/8/docs/technotes/guides/install/linux_plugin.html).

* Why build .deb using Debian, instead of Ubuntu?

  ```
  Build-Tainted-By:
    merged-usr-via-symlinks (due to /bin -> /usr/bin, etc.)
    usr-local-has-programs  (due to /usr/local/sbin/unminimize)
  ```

* Why don't you provide a keyring package?

  It's tedious to setup. I don't think Debian have well-designed key rotating
  for 3rd-party repositories.

# GitHub Actions secrets

* MAINTAINER: `Name <name@example.com>`
* PERSONAL_ACCESS_TOKEN: trigger GitHub Pages build
* SIGNING_KEY: APT repo signing key
