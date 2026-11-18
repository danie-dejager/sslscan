Name:           sslscan
Version:        2.2.4
%global         bundled_openssl_version    3.5.8
Release:        %autorelease
Summary:        Security assessment tool for SSL/TLS
URL:            https://github.com/rbsec/sslscan

Source0:        https://github.com/rbsec/sslscan/archive/refs/tags/v%{version}.tar.gz
# Special exception to allow linking against the OpenSSL libraries
# Automatically converted from old format: GPLv3+ with exceptions - review is highly recommended.
License:        LicenseRef-Callaway-GPLv3+-with-exceptions

# By default build with bundled openssl, with explicitly enabled weak ciphers
# use --without bundled_openssl to override and build with system openssl
%bcond_without     bundled_openssl

Source1:        https://www.openssl.org/source/openssl-%{bundled_openssl_version}.tar.gz

BuildRequires:  gcc
BuildRequires:  make
BuildRequires:  perl
BuildRequires:  zlib-devel
BuildRequires:  openssl-devel

%if %{with bundled_openssl}
# Bundled openssl is used to explicitly enable weak ciphers for the purpose of the scan
Provides: bundled(openssl) = %{bundled_openssl_version}
%endif

%description
SSLScan queries SSL services, such as HTTPS, in order to determine the ciphers
that are supported. SSLScan is designed to be easy, lean and fast. 
The output includes preferred ciphers of the SSL service, the certificate
and is in text and XML formats.


%prep
%autosetup -N -n %{name}-%{version}

# Override Makefile CFLAGS assignments so RPM build flags are preserved.
patch -p1 <<'PATCH'
--- a/Makefile
+++ b/Makefile
@@ -42,14 +42,14 @@
 endif
 endif
 ifeq ($(OS), SunOS)
-	CFLAGS += -m64
+	override CFLAGS += -m64
 	LIBS   += -lsocket -lnsl
 endif

 # Enable checks for buffer overflows, add stack protectors, generate position
 # independent code, mark the relocation table read-only, and mark the global
 # offset table read-only.
-CFLAGS  += -D_FORTIFY_SOURCE=2 -fstack-protector-all -fPIE
+override CFLAGS  += -O -D_FORTIFY_SOURCE=2 -fstack-protector-all -fPIE

 # Don't enable some hardening flags on OS X because it uses an old version of Clang
 ifneq ($(OS), Darwin)
@@ -65,13 +65,13 @@
 endif

 # Force C11 mode to fix the build on very old version of GCC
-CFLAGS += -std=gnu11
+override CFLAGS += -std=gnu11

 # for static linking
 ifeq ($(STATIC_BUILD), TRUE)
 PWD          = $(shell pwd)/openssl
 LDFLAGS      += -L${PWD}/
-CFLAGS       += -I${PWD}/include/ -I${PWD}/
+override CFLAGS       += -I${PWD}/include/ -I${PWD}/
 ifeq ($(OS), Darwin)
 LIBS	     = ./openssl/libssl.a ./openssl/libcrypto.a -lz -lpthread
 else
@@ -89,7 +89,7 @@
 else
 # for dynamic linking
 LDFLAGS   += -L/usr/local/lib -L/usr/local/ssl/lib -L/usr/local/opt/openssl/lib -L/opt/local/lib
-CFLAGS    += -I/usr/local/include -I/usr/local/ssl/include -I/usr/local/ssl/include/openssl -I/usr/local/opt/openssl/include -I/opt/local/include -I/opt/local/include/openssl
+override CFLAGS    += -I/usr/local/include -I/usr/local/ssl/include -I/usr/local/ssl/include/openssl -I/usr/local/opt/openssl/include -I/opt/local/include -I/opt/local/include/openssl
 endif
PATCH

# Prevent the Makefile from downloading OpenSSL from Git during the build.
patch -p1 <<'PATCH'
--- a/Makefile
+++ b/Makefile
@@ -137,7 +137,8 @@
-	.openssl.is.fresh: opensslpull
+	.openssl.is.fresh:
+		@true
PATCH

%if %{with bundled_openssl}
mkdir openssl
cd openssl
tar xvf %{SOURCE1} --strip-components=1
cd ..
%endif


%build
%if %{with bundled_openssl}
make %{?_smp_mflags} CFLAGS="%{optflags}" static
%else
make %{?_smp_mflags} CFLAGS="%{optflags}"
%endif

%install
make install DESTDIR=%{buildroot} BINPATH=%{_bindir}/ MANPATH=%{_mandir}/

%files
%doc Changelog README.md INSTALL
%license LICENSE
%{_bindir}/%{name}
%{_mandir}/man1/%{name}.1*

%changelog
%autochangelog
