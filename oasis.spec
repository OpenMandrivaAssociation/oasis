%define	name	oasis
%define	version	1.0
%define	release	4mdk

Summary:	Oasis - Open Access Server
Name:		%{name}
Version:	%{version}
Release:	%{release}
License:	BSD
Group:		System/Servers
URL:		http://software.stockholmopen.net/
Source0:	%{name}-%{version}.tar.bz2
Source1:	init-macbind.sql.bz2
Source2:	oasis.pam.bz2
Patch0:		oasis-1.0-DESTDIR.diff
Patch1:		oasis-1.0-avoid-version.diff
Requires:	apache2-mod_php
Requires:	apache2-mod_ssl
Requires:	dhcp-relay
Requires:	dhcp-server
Requires:	iptables
Requires:	openssl
Requires:	php-pgsql
Requires:	postgresql
Requires:	ruby
BuildRequires:	autoconf2.5
BuildRequires:	automake1.7
BuildRequires:	flex
BuildRequires:	libpcap-devel >= 0.7.2
BuildRequires:	libnet1.0.2-devel
BuildRequires:	openssl-devel
BuildRequires:	pam-devel
BuildRequires:	tetex-texi2html
BuildRoot:	%{_tmppath}/%{name}-%{version}-%{release}-buildroot

%description
Oasis is a Network Access Server (NAS) for an operator neutral
public access network.

%prep

%setup -q
%patch0 -p1
%patch1 -p1

bzcat %{SOURCE1} > init-macbind.sql
bzcat %{SOURCE2} > oasis.pam

%build
export WANT_AUTOCONF_2_5=1
rm -f configure
libtoolize --copy --force; aclocal-1.7 -I support && autoconf --force && autoheader && automake-1.7 --foreign --add-missing

pushd libcfg
rm -f configure
libtoolize --copy --force; aclocal-1.7 && autoconf --force && autoheader && automake-1.7 --foreign --add-missing
popd

%configure2_5x \
    --disable-static \
    --libdir=%{_libdir}/oasis \
    --with-www-dir=/var/www/html/oasis

%make

# fix docs
mkdir -p html
texi2html doc/basics.texi -subdir=html
texi2html doc/configuration.texi -subdir=html
texi2html doc/fwcd.texi -subdir=html
texi2html doc/instructions.texi -subdir=html
texi2html doc/oasis.texi -subdir=html
texi2html doc/stockholmopen.texi -subdir=html

%install
[ "%{buildroot}" != "/" ] && rm -rf %{buildroot}

install -d %{buildroot}%{_sysconfdir}/ssl/oasis
install -d %{buildroot}%{_sysconfdir}/pam.d

%makeinstall_std

install -m0640 etc/fwcd.conf %{buildroot}%{_sysconfdir}/fwcd.conf
install -m0640 etc/oasis.conf %{buildroot}%{_sysconfdir}/oasis.conf
install -m0640 oasis.pam %{buildroot}%{_sysconfdir}/pam.d/oasis

perl -pi -e "s|%{_sysconfdir}/|%{_sysconfdir}/oasis/|g" %{buildroot}%{_sysconfdir}/*.conf
perl -pi -e "s|pam-service.*|pam-service = oasis|g" %{buildroot}%{_sysconfdir}/*.conf

install -m0755 src/rbclient %{buildroot}%{_sbindir}/rbclient

# cleanup
rm -rf %{buildroot}%{_infodir}
rm -rf %{buildroot}%{_includedir}
rm -f %{buildroot}%{_libdir}/oasis/*.la

%clean
[ "%{buildroot}" != "/" ] && rm -rf %{buildroot}

%files
%defattr(-,root,root)
%doc ChangeLog LICENSE NEWS README TODO html contrib init-macbind.sql
%attr(0644,root,root) %config(noreplace) %{_sysconfdir}/fwcd.conf
%attr(0644,root,root) %config(noreplace) %{_sysconfdir}/oasis.conf
%attr(0644,root,root) %config(noreplace) %{_sysconfdir}/pam.d/oasis
%dir %attr(0755,root,root) %{_sysconfdir}/ssl/oasis
%{_sbindir}/*
%{_libdir}/oasis/*.so
/var/www/html/oasis

