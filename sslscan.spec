Name:           sslscan
Version:        2.2.4
Release:        1%{?dist}
Summary:        Security assessment tool for SSL/TLS

URL:            https://github.com/rbsec/sslscan

%global bundled_openssl_version 3.5.8
%bcond_without bundled_openssl

Source0:        %{url}/archive/refs/tags/%{version}.tar.gz
Source1:        https://www.openssl.org/source/openssl-%{bundled_openssl_version}.tar.gz

License:        GPL-3.0-or-later

BuildRequires:  gcc
BuildRequires:  make
BuildRequires:  perl
BuildRequires:  zlib-devel

%if %{without bundled_openssl}
BuildRequires:  openssl-devel
%endif

%if %{with bundled_openssl}
Provides:       bundled(openssl) = %{bundled_openssl_version}
%endif

%description
SSLScan queries SSL services, such as HTTPS, to determine supported
ciphers, protocols and certificate information.

%prep
%autosetup -n %{name}-%{version}

# Preserve RPM compiler flags.
sed -E -i \
    '/^[[:space:]]*CFLAGS[[:space:]]*\+=/s/^([[:space:]]*)CFLAGS/\1override CFLAGS/' \
    Makefile

# Disable automatic OpenSSL downloads.
sed -i \
    's/^\.openssl\.is\.fresh: opensslpull$/.openssl.is.fresh:/' \
    Makefile

%if %{with bundled_openssl}
mkdir -p openssl
tar -xf %{SOURCE1} --strip-components=1 -C openssl
%endif

%build
%if %{with bundled_openssl}
make %{?_smp_mflags} static CFLAGS="%{optflags}"
%else
make %{?_smp_mflags} CFLAGS="%{optflags}"
%endif

%install
make install DESTDIR=%{buildroot} BINPATH=%{_bindir}/ MANPATH=%{_mandir}/

%files
%doc Changelog README.md INSTALL
%license LICENSE
%{_bindir}/sslscan
%{_mandir}/man1/sslscan.1*

%changelog
* Wed Nov 18 2026 Package Maintainer - 2.2.4-1
- Initial RPM packaging
