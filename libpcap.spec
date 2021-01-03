# libpcap is used by wine
%ifarch %{x86_64}
%bcond_without compat32
%else
%bcond_with compat32
%endif

%define major 1
%define libname %mklibname pcap %{major}
%define devname %mklibname pcap -d
%define lib32name %mklib32name pcap %{major}
%define dev32name %mklib32name pcap -d
%bcond_without bluetooth

Summary:	A system-independent interface for user-level packet capture
Name:		libpcap
Version:	1.10.0
Release:	1
License:	BSD
Group:		System/Libraries
Url:		http://www.tcpdump.org/
Source0:	http://www.tcpdump.org/release/%{name}-%{version}.tar.gz
Source1:	http://www.tcpdump.org/release/%{name}-%{version}.tar.gz.sig
Patch0:		libpcap-multilib.patch
#Patch1:		libpcap-man.patch
Patch2:		libpcap-1.9.0-libnl.patch
#Patch2:		lpthread-1.3.0-libpcap.patch
BuildRequires:	bison
BuildRequires:	flex
%if %{with bluetooth}
BuildRequires:	pkgconfig(bluez)
%endif
BuildRequires:	pkgconfig(libnl-3.0)

%description
Libpcap provides a portable framework for low-level network monitoring. Libpcap
can provide network statistics collection, security monitoring and network
debugging.  Since almost every system vendor provides a different interface for
packet capture, the libpcap authors created this system-independent API to ease
in porting and to alleviate the need for several system-dependent packet
capture modules in each application.

#----------------------------------------------------------------------------

%package doc
Summary:	Manual pages for %{name}
Group:		Documentation
BuildArch:	noarch

%description doc
This contains the manual pages documenting %{name}.

%files doc
%{_mandir}/man5/pcap*
%{_mandir}/man7/pcap*

#----------------------------------------------------------------------------

%package -n %{libname}
Summary:	A system-independent interface for user-level packet capture
Group:		System/Libraries
Provides:	pcap = %{EVRD}

%description -n %{libname}
Libpcap provides a portable framework for low-level network monitoring. Libpcap
can provide network statistics collection, security monitoring and network
debugging.  Since almost every system vendor provides a different interface for
packet capture, the libpcap authors created this system-independent API to ease
in porting and to alleviate the need for several system-dependent packet
capture modules in each application.

%files -n %{libname}
%{_libdir}/libpcap.so.%{major}*

#----------------------------------------------------------------------------

%package -n %{devname}
Summary:	Development library and header files for the pcap library
Group:		Development/C
Requires:	%{libname} = %{EVRD}
Provides:	pcap-devel = %{EVRD}

%description -n %{devname}
This package contains the development pcap library and its header files needed
to compile applications such as tcpdump, etc.

%files -n %{devname}
%doc README* CREDITS LICENSE CHANGES TODO
%{_bindir}/pcap-config
%dir %{_includedir}/pcap
%{_includedir}/pcap/*.h
%{_includedir}/*.h
%{_libdir}/libpcap.so
%{_mandir}/man1/pcap-config.1*
%{_mandir}/man3/pcap*
%{_libdir}/pkgconfig/libpcap.pc

#----------------------------------------------------------------------------

%if %{with compat32}
%package -n %{lib32name}
Summary:	A system-independent interface for user-level packet capture
Group:		System/Libraries

%description -n %{lib32name}
Libpcap provides a portable framework for low-level network monitoring. Libpcap
can provide network statistics collection, security monitoring and network
debugging.  Since almost every system vendor provides a different interface for
packet capture, the libpcap authors created this system-independent API to ease
in porting and to alleviate the need for several system-dependent packet
capture modules in each application.

%files -n %{lib32name}
%{_prefix}/lib/libpcap.so.%{major}*

#----------------------------------------------------------------------------
%package -n %{dev32name}
Summary:	Development library and header files for the pcap library (32-bit)
Group:		Development/C
Requires:	%{lib32name} = %{EVRD}
Requires:	%{devname} = %{EVRD}

%description -n %{dev32name}
This package contains the development pcap library and its header files needed
to compile applications such as tcpdump, etc.

%files -n %{dev32name}
%{_prefix}/lib/libpcap.so
%{_prefix}/lib/pkgconfig/libpcap.pc
%endif

%prep
%setup -q
%autopatch -p1

autoreconf -fiv

export CFLAGS="%{optflags} -fno-strict-aliasing"
export CONFIGURE_TOP="$(pwd)"

%if %{with compat32}
mkdir build32
cd build32
%configure32 \
	--disable-static \
	--enable-ipv6 \
%if %{with bluetooth}
	--enable-bluetooth \
%endif
	--with-pcap=linux
cd ..
%endif

mkdir build
cd build
%configure \
	--disable-static \
	--enable-ipv6 \
%if %{with bluetooth}
	--enable-bluetooth \
%endif
	--with-pcap=linux

%build
%if %{with compat32}
%make_build -C build32
%endif
%make_build -C build

%install
install -d %{buildroot}%{_bindir}

%if %{with compat32}
%make_install -C build32
%endif

%make_install -C build

# install additional headers
install -m0644 pcap-int.h %{buildroot}%{_includedir}/
install -m0644 pcap/bluetooth.h %{buildroot}%{_includedir}/pcap/

# nuke the static lib
rm -f %{buildroot}%{_libdir}/libpcap.a %{buildroot}%{_prefix}/lib/libpcap.a
