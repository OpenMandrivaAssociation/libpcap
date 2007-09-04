%define	major 0
%define minor 9
%define libname %mklibname pcap %major
%define libdevel %libname-devel

Summary:        A system-independent interface for user-level packet capture
Name:		libpcap
Version:	0.9.7
Release:	%mkrel 2
License:	BSD
Group:		System/Libraries
URL:		http://www.tcpdump.org/
Source0:	http://www.tcpdump.org/release/%{name}-%{version}.tar.gz
Source1:	http://www.tcpdump.org/release/%{name}-%{version}.tar.gz.sig
BuildRequires:	bison
BuildRequires:	flex
BuildRequires:	autoconf2.5
BuildRoot:	%{_tmppath}/%{name}-%{version}-%{release}-buildroot

%description
Libpcap provides a portable framework for low-level network monitoring. Libpcap
can provide network statistics collection, security monitoring and network
debugging.  Since almost every system vendor provides a different interface for
packet capture, the libpcap authors created this system-independent API to ease
in porting and to alleviate the need for several system-dependent packet
capture modules in each application.

%package -n	%{libname}
Summary:	A system-independent interface for user-level packet capture
Group:          System/Libraries
Obsoletes:      %{name} < %{version}-%{release}
Provides:	%{name} = %{version}-%{release}
Provides:       pcap = %{version}-%{release}

%description -n	%libname
Libpcap provides a portable framework for low-level network monitoring. Libpcap
can provide network statistics collection, security monitoring and network
debugging.  Since almost every system vendor provides a different interface for
packet capture, the libpcap authors created this system-independent API to ease
in porting and to alleviate the need for several system-dependent packet
capture modules in each application.

%package -n	%{libdevel}
Summary:	Static library and header files for the pcap library
Group:		Development/C
Obsoletes:	%{name}-devel < %{version}-%{release}
Provides:	%{name}-devel = %{version}-%{release}
Provides:       pcap-devel = %{version}-%{release}
Requires:	%{libname} = %{version}-%{release}

%description -n	%libdevel
Libpcap provides a portable framework for low-level network monitoring. Libpcap
can provide network statistics collection, security monitoring and network
debugging.  Since almost every system vendor provides a different interface for
packet capture, the libpcap authors created this system-independent API to ease
in porting and to alleviate the need for several system-dependent packet
capture modules in each application.

This package contains the static pcap library and its header files needed to
compile applications such as tcpdump, etc.

%prep

%setup -q

%build
%serverbuild

%configure2_5x --enable-ipv6

%make "CCOPT=$CFLAGS -fPIC"

# nah, doing it the hard way instead...
#%%make "CCOPT=$RPM_OPT_FLAGS -fPIC" shared

#
# (fg) FIXME - UGLY - HACK - but libpcap's Makefile doesn't allow to build a
# shared lib...
#

gcc -Wl,-soname,libpcap.so.%{major} -shared -fPIC -o libpcap.so.%{major}.%{minor} *.o

%install
[ "%{buildroot}" != "/" ] && rm -rf %{buildroot}

%makeinstall_std

install -m755 libpcap.so.%{major}.%{minor} %{buildroot}%{_libdir}

pushd %{buildroot}%{_libdir} && {
    ln -s libpcap.so.%{major}.%{minor} libpcap.so.0
    ln -s libpcap.so.%{major}.%{minor} libpcap.so
} && popd

# install additional headers
install -m0644 pcap-int.h %{buildroot}%{_includedir}/

%clean
[ "%{buildroot}" != "/" ] && rm -rf %{buildroot}

%post -n %{libname} -p /sbin/ldconfig

%postun -n %{libname} -p /sbin/ldconfig

%files -n %{libname}
%defattr(-,root,root)
%doc README* CREDITS FILES INSTALL.txt LICENSE VERSION doc
%{_libdir}/libpcap.so.*

%files -n %{libdevel}
%defattr(-,root,root)
%doc CHANGES TODO
%{_includedir}/*
%{_libdir}/libpcap.so
%{_libdir}/libpcap.a
%{_mandir}/man3/pcap.3*
